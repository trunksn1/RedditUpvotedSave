#!/usr/bin/python 3.6
# -*- coding: utf-8 -*-

import os, pprint, re, requests, shelve, shutil, sys, time
import bs4, praw, send2trash

from gfycat.client import GfycatClient
from login import reddit_login, inizializza, crea_prawini

# regex = r'http.*imgur.*/[0-9a-zA-Z]*(jpeg|jpg|png|gif)? | http.*gfycat.*(jpeg|jpg|png|gif|gfv|gifv|gfy)?'
# regex = r'http.*imgur[0-9a-zA-Z/\.]*|http.*gfycat[0-9a-zA-Z/\.]*'
regex = r'http[^\s()]*'  # |www).*'

PATH_SLUT = 'Y:\\Giochi\\Mega'
PATH_SLUT_IMG = 'Y:\\Giochi\\Mega\\nsfw_img'
PATH_SLUT_VID = 'Y:\\Giochi\\Mega\\nsfw_vid'
PATH_SLUT_COM = 'Y:\\Giochi\\Mega\\nsfw_com\\'

LISTA_IMMAGINI = []
LISTA_VIDEO = []
LISTA_GIFV = []
DOPPIONI = []
# LISTA_ALBUM = []
IRRISOLTI = []
DIZ_CLEANER = {}
LISTE = [LISTA_IMMAGINI, LISTA_VIDEO, LISTA_GIFV, ]
COMMENTI = []
COMM_IRR = []


def main():
    # Fase preparatoria dei login e delle configurazioni
    sfigatto = GfycatClient()
    redditore, cartella_user = reddit_login()

    # creo la lista degli upvotes e la stampo a schermo
    lista_upvotes = crea_lista_up(redditore)
    num = 1
    for el in lista_upvotes:
        printa_up(num, el)
        num += 1

    pausa = input("PAUSA")

    # creo un set delle sub in cui sono stati postati i post upvotati
    # e la stampo
    sub_upvotes = prepara_sub(lista_upvotes)
    pprint.pprint(sub_upvotes)

    percorso, sub_scelte = scelta_subreddit(cartella_user, lista_upvotes)
    print()
    print(sub_scelte)

    pausa = input("PAUSA")

    if os.path.isfile(percorso):

        # TODO:Chiedi se vuoi aggiungere altre sub al file passato
        print('file')
    else:
        # TODO: Chiedi se vuoi salvare questa lista in un file da poter riutilizzare
        print('path')

    # Crea/Legge il file con i vecchi post upvotati, preparando così il controllo per i doppioni
    file_old_up = txt_upvote_passati(PATH_SLUT)
    lista_old_up = file_old_up.readlines()

    # Seleziono i post upvotati provenienti dalle sub indicate prima
    lista_new_up = selezione_post(lista_upvotes, sub_scelte)
    print('printo i submission selezionati!\n')
    num = 1
    for post in lista_new_up:
        printa_up(num, post)
        num += 1

    pausa = input("PAUSA")

    # Da ogni post nella lista creata viene estrapolato l'url a cui si riferisce e questo inserito in una lista pronto per essere prima checkato per doppione, e poi salvato
    for elemento in lista_new_up:
        smista_formato(sfigatto, elemento=elemento)
        # metto qua il parse dei commenti per evitare dopo un altro ciclo identico
        parse_commenti2(elemento)

    # pausa = input("premi per continuare")

    # A questo punto per ogni lista nel megalistone, guarda se gli elementi sono dei doppioni
    for lista_formato in LISTE:

        # Perchè lista_formato[:]???
        # Perchè così iteri su una copia della lista, in modo che quando
        # modfichi la lista orginale non stai modificando la copia che stai usando per iterare nel ciclo!

        for elemento in lista_formato[:]:
            # Se l'elemento è un doppione lo toglie dalla sua lista di appartenenza
            if check_doppione(elemento, lista_old_up, file_old_up):
                lista_formato.remove(elemento)

    # Andiamo a salvare:
    for immagine in LISTA_IMMAGINI:
        da_salvare(immagine, PATH_SLUT_IMG)
    for video in LISTA_VIDEO:
        da_salvare(video, PATH_SLUT_VID)
    for gifvideo in LISTA_GIFV:
        down_gifv(gifvideo, cartella_file=PATH_SLUT_VID)

    print('RECAP POST')
    print(len(LISTA_IMMAGINI), 'immagini salvate')
    print(len(LISTA_VIDEO), 'video salvati')
    print(len(LISTA_GIFV), 'GIFV salvati')
    print(len(IRRISOLTI), 'irrisolti!!!')
    print(len(DOPPIONI), "doppioni")
    print(len(IRRISOLTI), "IRRISOLTI")
    print(len(DIZ_CLEANER), "DIZ_CLEANER")
    pprint.pprint(DIZ_CLEANER)

    pausa = input("aspetto un tuo segnale per continuare...\n")

    # TODO ADESSO PULIRE GLI UPVOTE E AZZERARE LE LISTE PER I COMMENTI!!!
    DA_RIMUOVERE = LISTA_GIFV[:] + LISTA_VIDEO[:] + LISTA_IMMAGINI[:] + DOPPIONI[:]
    print(len(DA_RIMUOVERE))
    pausa = input("aspetto un tuo segnale per continuare...\n")
    del LISTA_IMMAGINI[:]
    del LISTA_VIDEO[:]
    del LISTA_GIFV[:]

    # Cerchiamo di pescare golosità nei commenti
    print("smistiamo i commenti!!!!")
    for commento in COMMENTI:
        try:
            smista_formato(sfigatto, commento=commento)
        except:
            print("ERRORE DI RECUPERO!!")
            COMM_IRR.append(commento)
            continue

    pausa = input("PAUSA")

    file_old_comm = txt_upvote_passati(PATH_SLUT_COM)
    lista_old_comm = file_old_comm.readlines()

    for lista_commenti in LISTE:
        for elemento in lista_commenti[:]:
            # Se l'elemento è un doppione lo toglie dalla sua lista di appartenenza
            if check_doppione(elemento, lista_old_comm, file_old_comm):
                lista_commenti.remove(elemento)

    for immagine in LISTA_IMMAGINI:
        da_salvare(immagine, PATH_SLUT_COM)
    for video in LISTA_VIDEO:
        da_salvare(video, PATH_SLUT_COM)
    for gifvideo in LISTA_GIFV:
        down_gifv(gifvideo, cartella_file=PATH_SLUT_COM)
    rimozione = [LISTA_IMMAGINI, LISTA_VIDEO, LISTA_GIFV, DOPPIONI]

    print('RECAP2: COMMENTI')
    print(len(LISTA_IMMAGINI), 'immagini salvate')
    print(len(LISTA_VIDEO), 'video salvati')
    print(len(LISTA_GIFV), 'GIFV salvati')
    print(len(IRRISOLTI), 'irrisolti!!!')
    pprint.pprint(IRRISOLTI)
    print(len(DOPPIONI), "doppioni")
    print(len(DIZ_CLEANER), "DIZ_CLEANER")
    print(LISTE)
    print('commenti irrecuperabili\n', COMM_IRR)
    pprint.pprint(COMM_IRR)

    pausa = input("PAUSA")

    for lista in (DA_RIMUOVERE):
        for post in DIZ_CLEANER:
            if DIZ_CLEANER[post] in lista:
                print("andiamo a rimuovere")
                remove_upvote(post)

def scelta(stringa, opz1y="s" , opz2n="n"):
    while True:
        scelta = input(stringa)
        if scelta.lower() == opz1y:
            return 1
        elif scelta.lower() == opz2n:
            return 2
        else:
            print("Devi scrivere solo '%s' oppure '%s'\nRIPROVA\n" %(opz1y, opz2n))
            continue


def parse_commenti2(post):
    pattern = re.compile(regex)
    try:  # se ho un post
        print("TRYHo un POST")
        post.comments.replace_more(limit=0)
    except:  # se ho un commento
        print("EXCEPTHo un COMMENTO")
        post.replace_more(limit=0)

    for commento in post.comments.list():
        bytestring = commento.body.encode('utf-8', 'replace')
        # cerca = pattern.search(str(bytestring, 'utf-8'))
        cerca = pattern.findall(str(bytestring, 'utf-8'))
        # print(bytestring)
        # print(cerca)
        if cerca:
            print("\n***********TROVATO!********:\n", cerca)
        for elem in cerca:
            COMMENTI.append(elem)
    print(len(COMMENTI))


def remove_upvote(el):
    try:
        print('sto per togliere l\'upvote a: \n', el.subreddit, el.title.encode(errors='replace'), el.url, el.shortlink)
    except AttributeError:
        print("volevo dirti che sto rimuovendo\n" + str(el))

    if scelta ("posso togliere gli upvote dai post oramai salvati? [s/n]") == 1:
        print("mò levo tutto! ADDIO ", el)
        try:
            el.clear_vote()
        except:
            print("non ho tolto niente perchè non ce sò riuscito, probabilmente non mi hai passato un post ma un url!")

#    while True:
#        opzione = input("posso togliere gli upvote dai post oramai salvati? [s/n]")
#        if opzione.lower() not in ['s', 'n']:
#            print('risposta errata')
#            continue
#        elif opzione.lower() == 's':
#            print("mò levo tutto! ADDIO ", el)
#            try:
#                el.clear_vote()
#                break
#            except:
#                print(
#                    "non ho tolto niente perchè non ce sò riuscito, probabilmente non mi hai passato un post ma un url!")
#                break
#        elif opzione.lower() == 'n':
#            break


def selezione_post(lista_upvotes, sub_scelte):
    '''prende la lista con gli upvotes dell'utente, e le sub indicate
    restituisce una lista contenente dei post upvotati provenienti solo
    da quelle sub'''

    post_selezionati = list()
    for up in lista_upvotes:
        # url = up.url
        sub = up.subreddit
        if sub in sub_scelte:
            post_selezionati.append(up)
    return post_selezionati


def crea_lista_up(redditore):
    '''Restituisce una lista contenente	i post upvotati dal redditor.
    Per accedere alla subreddit di ogni elemento si fa:
    lista[el].subreddit'''

    lista_up = list()
    # .upvoted() Return a ListingGenerator for items the user has upvoted.
    upvoted = redditore.upvoted()
    # crea la lista
    for upvote in upvoted:
        lista_up.append(upvote)
    return lista_up


def prepara_sub(lista_upvotes):
    '''Prende la lista degli upvotes dell'utente e restituisce un set
    che contiene le sub di origine dei post upvotati'''
    print("siamo in prepara_sub")
    sub_origine = set()
    for el in lista_upvotes:
        sub_origine.add((str(el.subreddit)))
    return sub_origine


def printa_up(numero, post):
    sub = str(post.subreddit)
    lunghezza = len(sub)
    if lunghezza > 12:
        spazi = '\t'
    elif lunghezza > 6:
        spazi = '\t\t'
    else:
        spazi = '\t\t\t'
    print(str(numero) + ') /r/', post.subreddit, spazi, post.title.encode(errors='replace'))


def scelta_subreddit(cartella_user, upvoted):
    """Chiede le subreddit in cui si trovano i post_upvotati che vuoi salvare
    passando la path della cartella user e la lista di upvotes
    restituisce una tupla contenente:
    1)il percorso della cartella e la 	lista delle sub scelte, oppure
    2)il percorso per il file txt ed la	variabile file.read() se già esistente"""

    while True:
        msg = '\n\n***Hai due possibilità per salvare i file:'
        msg += '\n[1] Importare un file di subreddit dalla cartella:'
        msg += '\n%s' % cartella_user
        msg += '\n [2] scegliere manualmente i subreddit \t***'

        #scelta() = int(input())
        opz = scelta(msg, opz1y='1', opz2n='2')

        # TODO L'idea è di mettere questi dati in un file config
        if opz == 1:
            print(os.listdir(cartella_user))
            sceltatxt = input('quale file? specifica anche l\'estensione\t')
            if os.path.isfile(sceltatxt):
                # Lo apro in append mode per poter vedere se posso modificarlo
                with open(sceltatxt, 'r+') as filesub:
                    percorso_filesub = os.path.join(cartella_user, sceltatxt)
                    lista_filesub = filesub.readlines()
                    print(lista_filesub)

                    while True:
                        opzione = scelta("vuoi aggiungere altre sub a questo file?\n [s/n]")
                        if opzione == 1:
                            del lista_filesub[:]
                            agg = input("Quale sub aggiungere? ATTENTO\n")
                            agg = agg + '\n'
                            print(agg)
                            filesub.write(agg)
                        elif opzione == 2:
                            break

                    #while True:
                    #    opzione = input("vuoi aggiungere altre sub a questo file?\n [s/n]")
                    #    if opzione.lower() == 's':
                    #        del lista_filesub[:]
                    #        agg = input("Quale sub aggiungere? ATTENTO\n")
                    #        agg = agg + '\n'
                    #        print(agg)
                    #        filesub.write(agg)
                    #    elif opzione.lower() == 'n':
                    #        break
                    #    else:
                    #        print("scrivi solo: S o N")
                    #        continue

                    # una volta letto con readlines prima il file è arrivato alla fine se provi a copiarlo nella lista con un
                    # nuovo readlines, copierà niente, perchè il file è finito, va quindi riavvolto con seek
                    filesub.seek(0)
                    lista_filesub = filesub.readlines()

                    for i in range(len(lista_filesub)):
                        lista_filesub[i] = lista_filesub[i].rstrip('\n')

                    return percorso_filesub, lista_filesub
            else:
                print('il file %s non esiste' % sceltatxt)
                continue

        elif opz == 2:
            listasub = list()
            sub_indicata = 1
            while sub_indicata:
                sub_indicata = input('quale subreddit scegli? bada bene a come scrivi! Lascia bianco per proseguire\n')
                listasub.append(sub_indicata)
                print(listasub)
            listasub.pop()
            print(listasub)

            opzione = scelta("vuoi salvare queste scelte in un file per una futura ricerca?\n [s/n]")
            if opzione == 1:
                filenome = input("che nome dai al file?\n")
                print(filenome)
                if not filenome.endswith('.txt'):
                    filenome = filenome + '.txt'
                    print(filenome)
                if os.path.isfile(filenome):
                    print("Il file esiste già! Scegli un altro nome\n")
                    continue

                with open(filenome, 'w') as filenuovo:
                    for sub in listasub:
                        filenuovo.write(sub + '\n')


            elif opzione == 2:
                print("va bene niente nuovi file")




#            while opzione:
#                if opzione.lower() == 's':
#                    filenome = input("che nome dai al file?\n")
#                    print(filenome)
#                    if not filenome.endswith('.txt'):
#                        filenome = filenome + '.txt'
#                        print(filenome)
#                    if os.path.isfile(filenome):
#                        print("Il file esiste già! Scegli un altro nome\n")
#                        continue
#
#                    with open(filenome, 'w') as filenuovo:
#                        for sub in listasub:
#                            filenuovo.write(sub + '\n')
#                        break
#
#                elif opzione.lower() == 'n':
#                    print("va bene niente nuovi file")
#                    break
#                else:
#                    print("S o N")

            # TODO: chiedi all'utente se vuole creare un file con queste
            # specifiche sub che ha scelto, o se ne vuole modificare uno esistente
            return cartella_user, listasub
        elif opz == 3:
            listasub = list()
            for el in upvoted:
                listasub.append(upvoted.subreddit)
            return cartella_user, listasub
        else:
            continue


def txt_upvote_passati(percorso):
    '''crea o legge, poi restituisce il file txt che conterrà/contiene
    l'url dei vecchi post upvotati'''
    # TODO: cerca la lista dei doppioni in PATH_SLUT. Se c'è l'apre e si prepara ad
    # controllare se i post dell'utente già ci sono e nel caso li salto (e toglie l'upvote)
    # aggiunge i post mancanti
    os.chdir(percorso)
    print('percorso per il txt', percorso)
    if not os.path.isfile(os.path.join(percorso, 'lista_upvote.txt')):
        modo = 'w+'
    else:
        modo = 'r+'
    # with open ('listone.txt', modo) as lista:
    #	return lista
    print('modo del listone: ', modo)
    lista = open('lista_upvote.txt', modo)
    return lista


def check_doppione(url, lista_passato, file_passato):
    print('\ncheck doppione: ', url)
    for rigo in lista_passato:
        # Se l'url che sto controllando è già nella lista di upvote vecchi allora controllo se il file esiste effettivamente
        if url in rigo:
            nome = os.path.basename(url)

            immag = os.path.isfile(os.path.join(PATH_SLUT_IMG, nome))
            singola_immag = os.path.isfile(os.path.join(PATH_SLUT_IMG, nome + '.jpg'))
            vid = os.path.isfile(os.path.join(PATH_SLUT_VID, nome))
            gfy = os.path.isfile(os.path.join(PATH_SLUT_VID, nome + '.mp4'))
            gifv = os.path.isfile(os.path.join(PATH_SLUT_VID, nome[:-4] + 'mp4'))
            commento = os.path.isfile(os.path.join(PATH_SLUT_COM, nome))

            # controlla se il file esiste
            if commento:
                print("Commento già in lista. Saltato!")
                DOPPIONI.append(url)
                return True

            elif not (immag or vid or gfy or gifv or singola_immag):
                print('Url già presente in lista, ma file assente!')

                mess = 'vuoi salvare il file: ' + str(url) + '? S/N\n'
                opz = scelta(mess)
                if opz == 1:
                    return False
                elif opz == 2:
                    DOPPIONI.append(url)
                    return True

                #while True:
                #    scelta = input('vuoi salvare il file: ' + str(url) + '? S/N\n')
                #    if scelta.lower() in ['n', 's']:
                #        break
                #if scelta.lower() == 's':
                #    return False
                #elif scelta.lower() == 'n':
                #    DOPPIONI.append(url)
                #    return True
            # Poichè la cartella dei commenti è lì giusto per lo smistamento se l'url del file è presente nel txt, lo dò già per doppione.
            else:
                print(url + ' già presente, con relativo file. DOPPIONISSIMO!')
                DOPPIONI.append(url)
                return True

        else:
            continue
    # cerca nel prossimo rigo

    print(url + ' è nuovo! SLURP')
    file_passato.write(url + '\n')
    return False


def smista_formato(sfigatto, **kwargs):
    '''smista i post tra i vari formati e restituisce liste contenente
    l'url finali da avviare al check_doppione
    il kwargs serve a far si che la funzione possa usare sia i post che
    gli url a cui i post puntano (quando usi i commenti)'''

    # print('\nsiamo in smista_formato')
    try:
        # Se hai un post da cui prendere l'url
        for k in kwargs:
            pre_url = kwargs[k].url
            url = str(pre_url)
    except:  # va specificato l'except o si fanno errori sciocchi!!! basta che sia sbagliato un print nel try per finire nell'except aspecifico e perdersi l'errore!
        # Se hai un url direttamente
        for k in kwargs:
            pre_url = kwargs[k]
            url = str(pre_url)

    if url.startswith('https://www.reddit.com/r/') or url.startswith('https://np.reddit.com/r/'):
        try:
            parse_commenti2(url)
        # print(url)
        # pausa = input("fermo GUARDA!")
        except:
            print("SMISTA: Errore nel recuperare il link da reddit")
        # print(url)
        # pausa = input("fermo GUARDA!")

    if url.endswith('.jpg') or url.endswith('.png') or url.endswith('.gif'):
        print('abbiamo a che fare con una immagine!\n')
        formato(LISTA_IMMAGINI, url, kwargs, k)

    elif url.startswith('http://imgur.com/a/'):
        print('abbiamo a che fare con ALBUM IMGUR!\n')
        album_imgur(url, kwargs, k)

    elif url.startswith('http://imgur.com'):
        print('abbiamo a che fare con una immagine IMGUR!\n')
        url = 'https://i.imgur.com//' + os.path.basename(url) + '.jpg'
        formato(LISTA_IMMAGINI, url, kwargs, k)

    elif url.startswith('https://m.imgur.com'):
        res = requests.get(url)
        res.raise_for_status()
        soup = bs4.BeautifulSoup(res.text, "html.parser")
        m = soup.select("div img[src]")
        print(m)
        print(type(m))
        print(len(m))
        #pausa = input("IMGUR MMMMM")
        for num in range(len(m)):
            url = 'http:' + m[num]['src']
            print(url)
            #pausa = input("IMGUR MMMMM")
            if url.endswith('.jpg') or url.endswith('.png') or url.endswith('.gif'):
                formato(LISTA_IMMAGINI, url, kwargs, k)
                #pausa = input("IMGUR MIMG")
            if url.endswith('.gifv'):
                formato(LISTA_GIFV, url, kwargs, k)
                #pausa = input("IMGUR MGIFV")



    elif url.startswith('https://imgur.com'):
        print('HTTPS IMGUR!\n')
        url = decifra_imgur_https(url)
        print(url)
        if url.endswith('.jpg') or url.endswith('.png') or url.endswith('.gif'):
            formato(LISTA_IMMAGINI, url, kwargs, k)
        elif url.endswith('.mp4'):
            formato(LISTA_VIDEO, url, kwargs, k)

    elif url.startswith('https://gfycat.com/') or url.startswith('https://giant.gfycat.com/') or url.startswith(
            'https://fat.gfycat.com/'):
        print("siamo su gfycat!\n", url)
        sfnome = os.path.basename(url)
        sfinfo = sfigatto.query_gfy(sfnome)
        # pprint.pprint (sfinfo)
        sfurl = sfinfo['gfyItem']['mp4Url']
        print(sfurl)
        formato(LISTA_VIDEO, sfurl, kwargs, k)

    elif url.endswith('.gifv'):
        print("siamo su imgur con una GIFV!")
        formato(LISTA_GIFV, url, kwargs, k)

    else:
        print('***********ODDIO!!! dove siamo?!?********\n', url)
        IRRISOLTI.append(kwargs[k])

    return LISTA_IMMAGINI, LISTA_VIDEO, LISTA_GIFV, IRRISOLTI


def formato(lista, url, dizkw, kwk):
    lista.append(url)
    DIZ_CLEANER[dizkw[kwk]] = url


def album_imgur(url, dizkw, kwk):
    res = requests.get(url)
    res.raise_for_status()
    soup = bs4.BeautifulSoup(res.text, "html.parser")
    album = soup.select("a img[src]")  # ("[class==post-image-container]")
    for num in range(len(album)):
        foto = 'http:' + album[num]['src']
        if foto.endswith('.jpg') or foto.endswith('.png') or foto.endswith('.gif'):
            print('foto dell album', foto)
            formato(LISTA_IMMAGINI, foto, dizkw, kwk)
        if foto.endswith('.gifv'):
            formato(LISTA_GIFV, foto, dizkw, kwk)


def decifra_imgur_https(url):
    res = requests.get(url)
    res.raise_for_status()
    soup = bs4.BeautifulSoup(res.text, "html.parser")
    elem = soup.select("body div source")
    try:
        ind = 'https:' + (elem[0]['src'])
    except:
        elem = soup.select("body div img")
        ind = 'https:' + (elem[0]['src'])
    return ind


def down_gifv(url, cartella_file=PATH_SLUT_VID):
    # Questo vale solo per le gifv del sito IMGUR.COM
    res = requests.get(url)
    res.raise_for_status()
    soup = bs4.BeautifulSoup(res.text, "html.parser")
    elem = soup.select("body div source")
    ind = 'http:' + (elem[0]['src'])
    # print(elem[0]['src'])
    da_salvare(ind, cartella_file)


def da_salvare(url, cartella_file):
    if os.path.isfile(os.path.join(cartella_file, os.path.basename(url))):
        print('File già esistente!: ', url)
        return
    try:
        res = requests.get(url)
    except:
        print("ERRORE, non possibile caricare la pagina!")
        return 404
    else:
        res.raise_for_status()
    salvato = open(os.path.join(cartella_file, os.path.basename(url)), 'wb')
    salva(salvato, res)


def salva(path, res):
    for pezzo in res.iter_content(100000):
        path.write(pezzo)
    path.close()


if __name__ == "__main__":
    main()
# ciao

# x = reddit.subreddit('redditdev')
# print(x)

# print(x.display_name)  # Output: redditdev
# print(x.title)         # Output: reddit Development
# print(x.description)   # Output: A subreddit for discussion of ...

# for i in range(len(lista)):
#	res = requests.get(lista[i])
#	res.raise_for_status()
#	imageFile = open(os.path.join('nsfw_img', os.path.basename(lista[i])) , 'wb')
#	for pezzo in res.iter_content(100000):
#		imageFile.write(pezzo)
#	imageFile.close()


#	soup = bs4.BeautifulSoup(res.text , "html.parser")
#	imag = soup.select('img src')
# try:
#	print(imag)
#	url = 'http:' + imag[0].get('src')
#	res = raise_for_status()
# except:
#	print('cazzi')
# pprint.pprint(lista_upvote)
# pprint.pprint(dir(upvote))
#		print(upvote.title)
#		print(upvote.subreddit)
#		print(upvote.thumbnail)
#		print(str(upvote.thumbnail_height) + '*' + str(upvote.thumbnail_width))
