#!/usr/bin/python 3.6
# -*- coding: utf-8 -*-

import os, pprint, re, requests, shelve, shutil, sys, time
import bs4, praw, send2trash

from gfycat.client import GfycatClient
from imgurpython import ImgurClient
from login import reddit_login
from config import PATH_SLUT, PATH_SLUT_IMG, PATH_SLUT_VID, PATH_SLUT_COM, imgur_client_id, imgur_client_secret
import sqlite3 as sql3
from siti import gfycazz, imagur

# regex = r'http.*imgur.*/[0-9a-zA-Z]*(jpeg|jpg|png|gif)? | http.*gfycat.*(jpeg|jpg|png|gif|gfv|gifv|gfy)?'
# regex = r'http.*imgur[0-9a-zA-Z/\.]*|http.*gfycat[0-9a-zA-Z/\.]*'
regex = r'http[^\s()]*'  # |www).*'

LISTA_IMMAGINI = []
LISTA_VIDEO = []
LISTA_GIFV = []
DOPPIONI = []
# LISTA_ALBUM = []
IRRISOLTI = []
DIZ_CLEANER = {}
LISTE = [LISTA_IMMAGINI, LISTA_VIDEO, LISTA_GIFV, ]
COMMENTI = set()
POST = set()
COMM_IRR = []

IMGUR = ImgurClient(imgur_client_id, imgur_client_secret)
SFIGATTO = GfycatClient()

def main():
    # Fase preparatoria dei login e delle configurazioni
    #sfigatto = GfycatClient()
    redditore, cartella_user, db = reddit_login()
    #imgur = ImgurClient(imgur_client_id, imgur_client_secret)
    cursore = db.cursor()

    # creo la lista degli upvotes e un set delle subreddit in cui sono stati postati i post upvotati
    lista_post_upvoted, set_sub = lista_post_set_sub(redditore)

    # stampa a schermo: num) /r/subreddit: 'Titolo post upvotato'
    mostra_upvotes(lista_post_upvoted)

    # O è il percorso verso un file.txt, ed una lista creato a partire da questo grazie a .readlines()
    # Oppure è il percorso della cartella_user, e la lista di sub indicate appena prima ma non salvate in txt
    percorso, sub_scelte, nome_file_txt = scelta_subreddit(cartella_user, lista_post_upvoted, set_sub)

    print("Lista finale delle sub selezionate:\n")
    pprint.pprint(sub_scelte)
    #pausa = input("PAUSA")

    # ADESSO: Aggiorno le tabelle: sub, selezioni e selezioni_sub
    aggiorno_db(db, cursore, nome_file_txt, set_sub, sub_scelte)

    #TODO piuttosto che file txt andrebbe usato un database
    # Crea/Legge il file dove sono segnati tutti gli url dei vecchi post upvotati; servirà per il controllo dei doppioni
    #file_old_up = txt_upvote_passati(PATH_SLUT)
    #lista_old_up = file_old_up.readlines()

    # Seleziono solo i post che provengono dalle sub indicate, e li restituisco in una lista
    lista_post_da_salvare = selezione_post(lista_post_upvoted, sub_scelte)
    print('\nprinto i submission selezionati!\n')
    mostra_upvotes(lista_post_da_salvare)
    #pausa = input("PAUSA")

    # Da ogni post nella lista viene estrapolato l'url, e creata una lista di url pronti per essere checkati per doppioni, e poi salvati
    for post_da_salvare in lista_post_da_salvare:
        #smista_post(post_da_salvare)
        if doppione(cursore, post_da_salvare):
            continue
        else:
            path = smista_e_salva(post_da_salvare)
            aggiungi_a_db(db, cursore, post_da_salvare, nome_file_txt, path)
            parse_commenti2(cursore, post_da_salvare)

    for commento in COMMENTI:
        if not doppione(cursore, commento):
            da_salvare(commento, cartella_file=PATH_SLUT_COM)
            aggiungi_a_db(db, cursore, commento, nome_file_txt, PATH_SLUT_COM)
    db.close()


        #smista_formato(sfigatto, elemento=post_da_salvare)
        # metto qua il parse dei commenti per evitare dopo un altro ciclo identico
        #parse_commenti2(post_da_salvare)

    j,i = prova_regex(list(POST))
    y, z = prova_regex(list(COMMENTI))
    print(j)
    print(i)
    print(y)
    print(z)
    input()
    print(POST)
    print(COMMENTI)
    input()

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
            smista_formato(SFIGATTO, commento=commento)
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

    file_old_up.close()
    file_old_comm.close()
    db.close()

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

def parse_commenti2(cursore, post):
    """Se ho un post, ho un oggetto specifico di reddit, se ho un commento invece maneggio un URL"""
    print("parse commenti del post: ", post.shortlink)
    # Se capisco bene questo try/except serve solo a ME per capire se sto trattando un post o un commento
    try:  # se ho un post
        #print("TRY\nHo un POST")
        post.comments.replace_more(limit=0)
    except:  # se ho un commento
        #print("EXCEPT\nHo un COMMENTO")
        post.replace_more(limit=0)

    pattern = re.compile(regex)
    # Trasoformo i commenti in utf-8, e cerco il pattern (https) all'interno del commento
    for commento in post.comments.list():
        bytestring = commento.body.encode('utf-8', 'replace')
        # cerca = pattern.search(str(bytestring, 'utf-8'))
        cerca = pattern.findall(str(bytestring, 'utf-8'))
        # print(bytestring)
        # print(cerca)
        if cerca:
            print("\n***********TROVATO! URL nei commenti********:\n", cerca)
        for elem in cerca:
            COMMENTI.add(elem)
            #if not doppione(cursore, elem):
            #    da_salvare(elem, cartella_file=PATH_SLUT_COM)
            #    aggiungi_a_db()

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
    upvoted = redditore.upvoted() # praw.models.listing.generator.ListingGenerator object

    for upvote in upvoted:
        lista_up.append(upvote)
        sub_origine.add((str(upvote.subreddit).lower()))
    return lista_up, sub_origine

def aggiorno_db(db, cursore, nome_file_txt, set_sub, sub_scelte):
    # ADESSO: Lavoro col database
    # 1) Aggiorno la tabella sub del db con tutti i nuovi subreddit che trovo negli upvote dell'utente
    # Se la subreddit è già nella tabella sub avrei un errore perchè il campo è specificato come UNIQUE
    for sub in set_sub:
        try:
            cursore.execute('''INSERT INTO sub(subreddit) VALUES (?)''', (sub,))
        except sql3.IntegrityError:
            print("sub già presente nella tabella sub: r/", sub)
    db.commit()

    input("Aggiornato tabella sub")

    # 2) Aggiorno la tabella selezioni inserendovi il nome del file txt da cui prendo le sub scelte da salvare
    # Se il file txt è già nel db saltalo (il campo è specificato come UNIQUE perciò genera errore se si duplica)
    try:
        cursore.execute('''INSERT INTO selezioni(fileselezione) VALUES (?)''', (nome_file_txt,))
        db.commit()
    except:
        print("già presente nella tabelle selezioni il file ", nome_file_txt)

    # 3) Aggiorno la tabella selezioni_sub che è la tabella multi relazionale tra subID e selezioniID
    # Per aggiornare la tabella mi serve per prima cosa l'ID del file nella tabella selezioni
    cursore.execute('SELECT id FROM selezioni WHERE fileselezione=?', (nome_file_txt,))
    rigo_selezioni = cursore.fetchone()

    # Per aggiornare la tabella mi serve anche l'ID delle singole sub scelte nella tabella sub
    for sub in sub_scelte:
        cursore.execute('SELECT id FROM sub WHERE subreddit=?', (sub,))
        rigo_sub = cursore.fetchone()

        # Qualora per uno dei sub scelti, non ci siano post upvotati da salvare avremo un errore
        try:
            cursore.execute("SELECT * FROM selezioni_sub WHERE selezioniID = ? AND subID = ?",
                            (rigo_selezioni[0], rigo_sub[0]))
            retrieve = cursore.fetchone()
        except TypeError:
            print("non c'è tra i file da salvare nulla che proviene dalla sub /r/", sub)
            continue

        # L'if serve a Evitare di copiare nella tabella selezioni_sub gli stessi dati più volte
        if retrieve:
            print("Nella tabella selezioni_sub è gia presente la coppia: /r/" + sub + "; " + nome_file_txt)
            continue
        print("Cerco di inserire nella tabella selezioni_sub: r/" + sub + "; " + nome_file_txt)
        try:
            cursore.execute('INSERT INTO selezioni_sub (selezioniID, subID) VALUES (?,?)',
                            (rigo_selezioni[0], rigo_sub[0]))
            db.commit()
        except:
            print("qualcosa è andato storto")
            input()

def mostra_upvotes(lista_up):
    num = 0
    for post in lista_up:
        sub = str(post.subreddit)
        titolo = str(post.title.encode(errors='replace'))
        # Formula che calcola le tab ottimali per pareggiare la spaziatura tra il nome del sub e il titolo
        lun = len(sub)
        spazi = "\t" * (6 - lun // 4)
        if lun % 4 == 0:
            spazi += "\t"

        print(str(num) + ')\t/r/' + sub + spazi + titolo)
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

                        #confronto tra gli elementi di due liste:
                        #la lista di sub dei post upvotati e le sub contenute nel file selezionato
                        #seleziona le sub al di fuori dal file scelto così da poterle mostrare

                        listasubescluse = list(set(sub_upvoted).difference(copiafilesub))
                        print('Scegliendo %s, gli upvotes dalle seguenti subreddit NON verrano salvati\n' % sceltatxt)
                        pprint.pprint(listasubescluse)
                        input('\nENTER per continuare')
                        # Si da la possibilità di aggiungere altre subreddit al file scelto in modo permamenente
                        aggiungi_sub(filesub)

                        # Se sono state aggiunte delle sub bisogna aggiornare la lista delle sub da restituire!
                        filesub.seek(0)
                        copiafilesub = filesub.read().lower().splitlines()


                        return percorso_filesub, copiafilesub, sceltatxt[:-4]
                else:
                    print('il file %s non esiste!!!' % sceltatxt)
                    continue

        elif not filetxt:   # se ho indicato di voler scegliere manualmente i subreddit
            listasub = list()
            aggiungi_sub(listasub)

            if scelta("vuoi salvare queste scelte in un file per una futura ricerca?\n [s/n]"):
                # Scelta del nome del file
                mess = "che nome dai al file?"
                filenome = ''
                while not filenome:
                    print(mess)
                    filenome = input()
                    # Se il nome del file è stato lasciato in bianco, ripeti il nome
                    if not filenome:
                        mess = "Non hai dato un nome valido!!!\n che nome dai al file?"
                        continue
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
                return percorso_filenuovo, listasub, filenome[:-4] #lista_filenuovo
            # Restituito il percorso della cartella dell'user con l'elenco di sub scritte pocanzi ma non salvate in un file.
            return cartella_user, listasub, 'temp'

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
    print(messaggio)
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

def doppione(cursore, post):
    """
    Se il post è già presente nel database -> è un doppione
    Se tuttavia il file non c'è chiede all'utente se salvarlo!
    Se il post è assente nel database, o se l'utente così decide -> Salvalo
    Aggiorna poi il database sia se il post è stato salvato che se non lo è stato"""
    url = ''
    try:
        print("Ho un post")
        url = str(post.url)
    except:
        print("Ho un URL")
        url = str(post)
    #url = str(post.url)
    print("\nDOPPIONE?\n", url)


    # Vediamo se l'url del post è già nella tabella file_salvati Seleziono filetype perchè mi serve dopo per ottenere la cartella dove andare a cercare il file.
    # Se infatti il file esiste nella cartella esso è certamente un doppione e si salta, se manca, si chiede all'utente se salvarlo.
    cursore.execute('SELECT percorso FROM file_salvati WHERE url=?', (url,))
    selezioni_filetype = cursore.fetchone()

    # Se il post già esiste nel database: controlliamo se esiste il file
    if selezioni_filetype:
        print("l'url è già presente nel database, controllo che ci sia il file")
        nome = os.path.basename(url)
        """print(nome)
        print(os.path.join(PATH_SLUT_COM, nome))
        print(os.path.join(PATH_SLUT_IMG, nome))
        print(os.path.join(PATH_SLUT_VID, nome))
        input()"""
        # Controllo se il file è tra la cartella commenti
        if os.path.isfile(os.path.join(PATH_SLUT_COM, nome)):
            print("Commento già in lista. Saltato!")
            return True
        # Controllo se il file è tra la cartella immagini o video
        elif not os.path.isfile(os.path.join(PATH_SLUT_IMG, nome)) or os.path.isfile(os.path.join(PATH_SLUT_VID, nome)) or os.path.isfile(os.path.join(PATH_SLUT_VID, nome, '.webm')) or os.path.isfile(os.path.join(PATH_SLUT_VID, nome, '.mp4')):
            print("Url nel database ma file non esistente!\n", nome)
            mess = 'vuoi salvare il file: ' + url + '? S/N\n'
            opz = scelta(mess)
            if opz: # Se l'utente ha detto di voler salvare il file allora, la funzione restituisce False e si procedere al salvataggio
                return False
            return True # In questo caso l'utente ha detto di non voler salvare il file, quindi la funz restituisce True

    # Se l'url non è presente nel database restituisci False così da poter avviare la fase di salvataggio in main()
    if not selezioni_filetype:
        print("NUOVO, SLURP")
        return False


def aggiungi_a_db(db, cursore, post, nome_file_txt, percorso=''):
    #TODO
    # Aggiungo i dati al db
    #Ricaviamo l'id della subreddit originaria del post dalla tabella sub:
    print(type(post))
    # Comportamento diverso se abbiamo un post o un commento:
    if isinstance(post, praw.models.reddit.submission.Submission):
        cursore.execute('SELECT id FROM sub WHERE subreddit=?', (str(post.subreddit).lower(),))
        rigo_sub = cursore.fetchone()
        print(rigo_sub[0])

        try:
            print("aggiungo il post al database")
            cursore.execute('INSERT INTO file_salvati(post, url, subID, txt_subreddit, percorso) VALUES(?,?,?,?,?)',
                            (str(post.shortlink), str(post.url), rigo_sub[0], nome_file_txt, percorso))
            db.commit()
        except sql3.IntegrityError:
            print("Post, già presente nel database")
        #else:
        #    # Controlla se esiste il file nella cartella! nsfw_<formato>
        #    print("Non aggiunto")
        #input("Stop")
        return True
    # Se stiamo aggiungendo un commento post.subreddit dà un Attribute errore che va aggirato
    # Aggiungiamo un commento:
    else:
        print("aggiungo il commento al database")
        # Allora provo ad aggiungere il commento, sempre che non sia già presente in lista
        try:
            cursore.execute('INSERT INTO file_salvati(url, txt_subreddit, percorso) VALUES(?,?,?)',
                            (str(post), nome_file_txt, percorso))
            db.commit()
        except sql3.IntegrityError:
            print("Url {}, già presente nel database".format(str(post)))

def check_doppione(url, lista_passato, file_passato):
    print('\ncheck doppione: ', url)

    # Se l'url che sto controllando è già nella lista di upvote vecchi allora controllo se il file esiste effettivamente
    if url in lista_passato:
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

    # cerca nel prossimo rigo
    print(url + ' è nuovo! SLURP')
    file_passato.write(url + '\n')
    return False

def url_dal_post(post):
    """Da un postricava il suo url e lo appende in una lista POST,
    l'url andrà poi analizzato così da usare l'API corretta per salvarlo
     (vedendo se viene da imgur o gfycat o reddit ecc...)"""

    url = str(post.url)
    POST.add(url)
    # Otteniamo gli url postati nei commenti
    parse_commenti2(post)

def prova_regex(lista):
    pattern = re.compile(r'(.*?imgur.*)|(.*?redd.*)|(.*?gfycat.*)') #(.*?png$|.*?jp(e)?g$)|((.*?imgur.*)|(.*?redd.*)|(.*?gfycat.*))')
                         #r'((http)(s)?(://))?(imgur.com).*')
    x = list()
    y= list()
    for url in lista:
        """if url.endswith('.jpg') or url.endswith('.png') or url.endswith('.gif'):
            print('abbiamo a che fare con una immagine!\n')
            # TODO
        print(url)"""
        x = pattern.findall(url)
        v = pattern.search(url)
        match = pattern.match(url)

        if match:
            x.append(match[0])
            print(url)
            print(pattern)
            print(x)
            print(v.groups())
            print(match)
            input("Input, pattern, findall, groups, e match")
            print()
        else:
            y.append(url)
        """try:
            print(x)
        except:
            print("non riesco a mostrarti i groups di: " + url)"""
    return x, y

def smista_e_salva(post):
    print("\nSMISTO POST")
    url = ''
    try:
        print("Ho un post")
        url = str(post.url)
    except:
        print("Ho un URL")
        url = str(post)

    print(url)

    if url.endswith('.jpg') or url.endswith('.png') or url.endswith('.gif'):
        print('abbiamo a che fare con una immagine!\n')
        return da_salvare(url, PATH_SLUT_IMG)

        #formato('immagine', post)
        #formato(LISTA_IMMAGINI, url, kwargs, k)

    elif url.endswith('.gifv'):
        print("siamo su imgur con una GIFV!")
        link = imagur(IMGUR, url)
        return da_salvare(url, PATH_SLUT_VID)

        #formato(LISTA_GIFV, url, kwargs, k)

    elif url.endswith('.mp4'):
        print("è un video!")
        return da_salvare(url, PATH_SLUT_VID)



    pattern = re.compile(r'(.*?imgur.*)|(.*?redd.*)|(.*?gfycat.*)')
    v = pattern.search(url)
    try:
        tupla_search = v.groups()
        if tupla_search[0]: #imgur
            print("imgur")
            link = imagur(IMGUR, url)
            #if type(link) == list:
            if isinstance(link, list):
                print("ALBUM!")
                for el in link:
                    da_salvare(el) # in questo caso non gli faccio restituire niente o non salvo le singole immagini
            else:
                return da_salvare(link)

        elif tupla_search[1]: #forse reddit
            print("reddit")
            #input("Quali sono le possibilità? STOP")
            pass

        elif tupla_search[2]: #gfycat
            print("gfycat")
            link = gfycazz(SFIGATTO, url)
            print(link)
            #input("STOP, CONTROLLA COME E' IL FORMATO ")
            return da_salvare(link)

        else:
            print(url)
            #Da aggiungere alla tabella non_salvati
            print("non riconosciuto")
    except:
        print("URL non da imgur reddit o gfycat")


def db_pre_salvataggio(formato, post):
    #if file già esiste nel database
        #se esiste, controlla che ci sia effettivamente
            #se esiste e c'è -> salta
        #se non c'è il file chiedi se salvarlo

    # se non c'è nel database il post/url ->vai a salvare il file
    # solo adesso aggiungi i dati al database!
    return

def smista_formato(sfigatto, **kwargs):
    '''smista i post tra i vari formati e restituisce liste contenenti gli url finali da avviare al check_doppione
    il kwargs serve a far si che la funzione possa usare sia i post che gli url dei post (quando studi i commenti)'''
    #SI PUO REFACTORIARE! E Forse semplificare togliendo il **kwargs.

    print('\nsiamo in smista_formato')
    """print(kwargs)
    print(type(kwargs))
    input("ENTER per continuare")"""
    url = ''
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
    print(url)

    if url.startswith('https://www.reddit.com/r/') or url.startswith('https://np.reddit.com/r/'):
        try:
            parse_commenti2(url)
        # print(url)
        # pausa = input("fermo GUARDA!")
        except:
            print("SMISTA: Errore nel recuperare il link da reddit")

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

    elif url.endswith('.gifv'):
        print("siamo su imgur con una GIFV!")
        formato(LISTA_GIFV, url, kwargs, k)

    elif url.startswith('https://gfycat.com/') or url.startswith('https://giant.gfycat.com/') or url.startswith(
            'https://fat.gfycat.com/'):
        print("siamo su gfycat!\n")
        sfnome = os.path.basename(url)
        sfinfo = sfigatto.query_gfy(sfnome)
        # pprint.pprint (sfinfo)
        sfurl = sfinfo['gfyItem']['mp4Url']
        print(sfurl)
        formato(LISTA_VIDEO, sfurl, kwargs, k)
        """

    pattern = re.compile(r'.*?imgur.*')
    match = pattern.match(url)
    if match:
        siti.imagur(url)

    pattern = re.compile(r'.*?gfycat.*')
    match = pattern.match(url)
    if match:
        siti.gfycazz(url)"""




    else:
        print('***********ODDIO!!! dove siamo?!?********\n')
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


# def da_salvare(url, cartella_file):
def da_salvare(url, cartella_file=''):

    # Se il programma funziona bene, questo check qua è inutile
    """if os.path.isfile(os.path.join(cartella_file, os.path.basename(url))):
        print('File già esistente!: ', url)
        return il percorso di dove va a salvare il file"""
    if not cartella_file:
        if url.endswith('.jpg') or url.endswith('.png') or url.endswith('.gif'):
            cartella_file = PATH_SLUT_IMG

        elif url.endswith('.gifv') or url.endswith('.mp4') or url.endswith('.webm'):
            cartella_file = PATH_SLUT_VID

    print(cartella_file)

    res = requests.get(url)
    stato = res.status_code
    if stato != 200:
        print("qualcosa è andato storto.")
        print(stato)
        print(url)
        return stato
    else:
        try:
            salvato = open(os.path.join(cartella_file, os.path.basename(url)), 'wb')
            salva(salvato, res)
            print("Salvato: ", url)
            return cartella_file
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