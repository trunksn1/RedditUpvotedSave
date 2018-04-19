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

    # creo la lista degli upvotes e un set delle subreddit in cui sono stati postati i post upvotati
    lista_upvotes, sub_upvotes = lista_post_set_sub(redditore)

    # stampa a schermo: num) /r/subreddit: 'Titolo post upvotato'
    mostra_upvotes(lista_upvotes)

    # O è il percorso verso un file.txt con la lista da esso creato con .readlines()
    # Oppure sono il percorso della cartella_user con la listadisub indicate appena prima ma non salvate in txt
    percorso, sub_scelte = scelta_subreddit(cartella_user, lista_upvotes, sub_upvotes)

    print("Lista finale delle sub selezionate:\n")
    pprint.pprint(sub_scelte)
    #pausa = input("PAUSA")

    # Crea/Legge il file dove sono segnati tutti gli url dei vecchi post upvotati; servirà per il controllo dei doppioni
    file_old_up = txt_upvote_passati(PATH_SLUT)
    lista_old_up = file_old_up.readlines()

    # Seleziono i post upvotati provenienti dalle sub indicate prima, restituendoli in una lista di post
    lista_new_up = selezione_post(lista_upvotes, sub_scelte)
    print('\nprinto i submission selezionati!\n')
    mostra_upvotes(lista_new_up)
    #pausa = input("PAUSA")

    # Da ogni post nella lista viene estrapolato l'url, e creata una lista di url pronti per essere checkati per doppioni, e poi salvati
    for elemento in lista_new_up:
        smista_formato(sfigatto, elemento=elemento)
        # metto qua il parse dei commenti per evitare dopo un altro ciclo identico
        parse_commenti2(elemento)

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

    # TODO ADESSO PULIRE GLI UPVOTE E AZZERARE LE LISTE PER I COMMENTI!!!
    DA_RIMUOVERE = LISTA_GIFV[:] + LISTA_VIDEO[:] + LISTA_IMMAGINI[:] + DOPPIONI[:]
    print(len(DA_RIMUOVERE))
    #pausa = input("aspetto un tuo segnale per continuare...\n")
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

    #pausa = input("PAUSA")

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

    for lista in (DA_RIMUOVERE):
        for post in DIZ_CLEANER:
            if DIZ_CLEANER[post] in lista:
                print("andiamo a rimuovere")
                remove_upvote(post)

def scelta(stringa, opz1y="s" , opz2n="n"):
    while True:
        scelta = input(stringa)
        if scelta.lower() == opz1y:
            return True
        elif scelta.lower() == opz2n:
            return False
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

    if scelta ("posso togliere gli upvote dai post oramai salvati? [s/n]"):
        print("mò levo tutto! ADDIO ", el)
        try:
            el.clear_vote()
        except:
            print("non ho tolto niente perchè non ce sò riuscito, probabilmente non mi hai passato un post ma un url!")

def selezione_post(lista_upvotes, sub_scelte):
    '''prende la lista con gli upvotes dell'utente, e le sub indicate
    restituisce una lista contenente dei post upvotati provenienti solo
    da quelle sub'''

    post_selezionati = list()
    for up in lista_upvotes:
        sub = up.subreddit
        if sub in sub_scelte:
            post_selezionati.append(up)
    return post_selezionati

def lista_post_set_sub(redditore):
    """Creo contemporaneamente sia la lista dei post upvotati che il set con i subreddit dei post.
    Restituisce una tupla con la lista dei post upvotati dal redditor, e un set delle sub di origine dei post upvotati
    Per accedere alla subreddit di ogni elemento si fa: lista[el].subreddit"""
    lista_up = list()
    sub_origine = set()
    print("NUOVA FUNZIONE LISTA_POST_SET_SUB")
    # .upvoted() Return a ListingGenerator for items the user has upvoted.
    upvoted = redditore.upvoted()

    for upvote in upvoted:
        lista_up.append(upvote)
        sub_origine.add((str(upvote.subreddit).lower()))
    return lista_up, sub_origine

def mostra_upvotes(lista_up):
    num = 0

    for post in lista_up:
        sub = str(post.subreddit)
        # Formula che calcola le tab ottimali per pareggiare la spaziatura tra il nome del sub e il titolo
        lun = len(sub)
        spazi = "\t" * (6 - lun // 4)
        if lun % 4 == 0:
            spazi += "\t"

        print(str(num) + ')\t/r/' + sub + spazi + str(post.title.encode(errors='replace')))
        num += 1


def scelta_subreddit(cartella_user, upvoted, sub_upvoted):
    """I post provenienti da quelle subreddit vuoi salvare?
    passando la path della cartella user e la lista di upvotes
    restituisce una tupla contenente:
    1)il percorso della cartella e la lista delle sub scelte, oppure
    2)il percorso per il file txt ed la	variabile file.read() se già esistente"""

    while True:
        msg = '\n\n***\tHai due possibilità per salvare i file:'
        msg += '\n***\t[1] Leggere le subreddit scritte in un file situato nella cartella:'
        msg += '\n***\t%s' % cartella_user
        msg += '\n***\t[2] Scrivere manualmente i subreddit \t***\n'
        filetxt = scelta(msg, opz1y='1', opz2n='2')     # filetext sarà o True o False

        # TODO L'idea è di mettere questi dati in un file config
        if filetxt:
            while True:
                print('Quale file tra questi?')
                print(os.listdir(cartella_user))
                sceltatxt = input()
                # Se manca l'estensione .txt l'aggiungo
                if not sceltatxt.endswith(".txt"):
                    sceltatxt += ".txt"
                    print(sceltatxt)

                if os.path.isfile(sceltatxt):
                    # Lo apro in append mode per poter vedere se posso modificarlo
                    with open(sceltatxt, 'r+') as filesub:
                        copiafilesub = filesub.read().lower().splitlines() # splitlines() separa le stringhe lette da read(), e fa una lista

                        percorso_filesub = os.path.join(cartella_user, sceltatxt)
                        print("\nContenuto del file %s\n" % sceltatxt)
                        print(copiafilesub)

                        #TODO Penso che si possa fare diversamente il confronto tra gli elementi di due liste, senza necessità di crearne una terza
                        #confronta le sub dei post upvotati con le sub contenute nel file selezionato
                        # per mostrare quelle che sono rimaste fuori dal file scelto così da potercele aggiungere

                        listasubescluse = list(set(sub_upvoted).difference(copiafilesub))
                        print('Scegliendo %s, gli upvotes dalle seguenti subreddit NON verrano salvati\n' % sceltatxt)
                        pprint.pprint(listasubescluse)
                        input('\nENTER per continuare')
                        # Si da la possibilità di aggiungere altre subreddit al file scelto in modo permamenente
                        aggiungi_sub(filesub)

                        return percorso_filesub, copiafilesub
                else:
                    print('il file %s non esiste!!!' % sceltatxt)
                    continue

        elif not filetxt:   # se ho indicato di voler scegliere manualmente i subreddit
            listasub = list()
            aggiungi_sub(listasub)

            if scelta("vuoi salvare queste scelte in un file per una futura ricerca?\n [s/n]"):
                # Scelta del nome del file
                while True:
                    filenome = input("che nome dai al file?\n")

                    if not filenome.endswith('.txt'):
                        filenome = filenome + '.txt'
                        print(filenome)

                    if os.path.isfile(filenome):
                        print("Il file esiste già! Scegli un altro nome\n")
                        continue
                    else:
                        break
                # Fase 1 Creazione del file: modo 'w'
                filenuovo = open(filenome, 'w')
                percorso_filenuovo = os.path.join(cartella_user, filenome)
                for sub in listasub:
                    filenuovo.write(sub + '\n')
                filenuovo.close()
                # Restituito il percorso del file creato e la lista creata sulla base del file
                return percorso_filenuovo, listasub #lista_filenuovo
            # Restituito il percorso della cartella dell'user con l'elenco di sub scritte pocanzi ma non salvate in un file.
            return cartella_user, listasub

        # TODO opzione speciale per salvare tutti i file upvotati direttamente!
        elif opz == 3:
            listasub = list()
            for el in upvoted:
                listasub.append(upvoted.subreddit)
            return cartella_user, listasub
        else:
            continue

def aggiungi_sub(data):
    """Aggiunge all'argomento passatole (file o lista) le subreddit scelte dall'utente"""
    messaggio = "quale subreddit vuoi aggiungere? Scrive bene il nome! Lascia bianco per proseguire\n"
    sub_indicata = 1
    while sub_indicata:
        print(messaggio)
        sub_indicata = input()

        if not sub_indicata:
            break
        if (type(data)) == list:
            data.append(sub_indicata)
            print(sub_indicata)
        else:
            sub_indicata = sub_indicata + '\n'
            data.write(sub_indicata)
            print(sub_indicata)
    print(data)


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
    #print('modo del listone: ', modo)
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
                if opz:
                    return False
                elif not opz:
                    DOPPIONI.append(url)
                    return True

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
    '''smista i post tra i vari formati e restituisce liste contenenti gli url finali da avviare al check_doppione
    il kwargs serve a far si che la funzione possa usare sia i post che gli url dei post (quando studi i commenti)'''
    #SI PUO REFACTORIARE! E Forse semplificare togliendo il **kwargs.


    # print('\nsiamo in smista_formato')
    try:
        # Se hai un post da cui estrarre l'url
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
    # TODO bisogna cercare se la pagina contiene il bottone per caricare più foto,
    # se si: caricare il file in modalità grid aggiungendo alla fine dell'url "/a/imageid/all" e scaricare tutte le foto
    #che non funziona, forse con ?grid
    #se no scarica l'album come è
    url += "?grid"
    print (url)
    #input("pausa")
    res = requests.get(url)
    res.raise_for_status()
    soup = bs4.BeautifulSoup(res.text, "html.parser")
    #album = soup.select("a img[src]")  # ("[class==post-image-container]")
    album = soup.select(".post-image")
    print(album)
    print(str(len(album)) + ' foto trovate nell album url: ' + url)
    #input("pausa")
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
    try:
        res = requests.get(url)
        res.raise_for_status()
        soup = bs4.BeautifulSoup(res.text, "html.parser")
        elem = soup.select("body div source")
        ind = 'http:' + (elem[0]['src'])
        # print(elem[0]['src'])
        da_salvare(ind, cartella_file)
    except:
        print("c'è stato un problema con le gifv di imgur")

def da_salvare(url, cartella_file):
    if os.path.isfile(os.path.join(cartella_file, os.path.basename(url))):
        print('File già esistente!: ', url)
        return

    res = requests.get(url)
    stato = res.status_code
    if stato != 200:
        print("qualcosa è andato storto.")
        print(stato)
        print(url)
        return 505
    else:
        try:
            salvato = open(os.path.join(cartella_file, os.path.basename(url)), 'wb')
            salva(salvato, res)
            print("Salvato: ", url)
        except:
            # TODO piazzare l'url salvato da qualche parten
            print("qualcosa è andato storto al salvataggio dell'url: " + str(url))
            return 505

    # Riscritto
    #try:
    #    res = requests.get(url)
    #    print(res.status_code)
    #except:
    #    print("ERRORE, non possibile caricare la pagina!")
    #    return 404
    #else:
    #    print("qualcosa è andato storto.")
    #    print(url)
    #    return 505
    #    #res.raise_for_status()
    #salvato = open(os.path.join(cartella_file, os.path.basename(url)), 'wb')
    #salva(salvato, res)


def salva(path, res):
    for pezzo in res.iter_content(100000):
        path.write(pezzo)
    path.close()


if __name__ == "__main__":
    main()