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

LISTA_IMMAGINI, LISTA_VIDEO, LISTA_GIFV, DOPPIONI, IRRISOLTI, COMM_IRR = [], [], [], [], [], []
LISTE = [LISTA_IMMAGINI, LISTA_VIDEO, LISTA_GIFV, ]
DIZ_CLEANER = {}
COMMENTI = set()
POST = set()

IMGUR = ImgurClient(imgur_client_id, imgur_client_secret)
SFIGATTO = GfycatClient()

def main():
    # Fase preparatoria dei login e delle configurazioni
    redditore, cartella_user, db = reddit_login()
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

    # ADESSO: Aggiorno il db e le tabelle: sub, selezioni e selezioni_sub
    aggiorno_db(db, cursore, nome_file_txt, set_sub, sub_scelte)

    # Seleziono solo i post che provengono dalle sub indicate, e li restituisco in una lista
    lista_post_da_salvare = selezione_post(lista_post_upvoted, sub_scelte)
    print('\nprinto i submission selezionati!\n')
    mostra_upvotes(lista_post_da_salvare)

    # Da ogni post nella lista viene estrapolato l'url, e creata una lista di url pronti per essere checkati per doppioni, e poi salvati
    for post_da_salvare in lista_post_da_salvare:
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


def scelta(stringa, opz1y="s", opz2n="n"):
    while True:
        decisione = input(stringa)
        if decisione.lower() == opz1y:
            return True
        elif decisione.lower() == opz2n:
            return False
        else:
            print("Devi scrivere solo '%s' oppure '%s'\nRIPROVA\n" % (opz1y, opz2n))
            continue

def parse_commenti2(cursore, post):
    """Se ho un post, ho un oggetto specifico di reddit, se ho un commento invece maneggio un URL"""
    print("parse commenti del post: ", post.shortlink)
    regex = r'http[^\s()]*'  # |www).*'
    # Se capisco bene questo try/except serve solo a ME per capire se sto trattando un post o un commento
    try:  # se ho un post
        post.comments.replace_more(limit=0)
    except:  # se ho un commento
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
    print(len(COMMENTI))


def remove_upvote(el):
    # TODO da aggiornare vista l'implementazione del database
    try:
        print('sto per togliere l\'upvote a: \n', el.subreddit, el.title.encode(errors='replace'), el.url, el.shortlink)
    except AttributeError:
        print("volevo dirti che sto rimuovendo\n" + str(el))

    if scelta("posso togliere gli upvote dai post oramai salvati? [s/n]"):
        print("mò levo tutto! ADDIO ", el)
        try:
            el.clear_vote()
        except:
            print("non ho tolto niente perchè non ce sò riuscito, probabilmente non mi hai passato un post ma un url!")


def selezione_post(lista_upvotes, sub_scelte):
    """prende la lista con gli upvotes dell'utente, e le sub indicate
    restituisce una lista contenente dei post upvotati provenienti solo
    da quelle sub"""

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
    upvoted = redditore.upvoted()  # praw.models.listing.generator.ListingGenerator object

    for upvote in upvoted:
        lista_up.append(upvote)
        sub_origine.add((str(upvote.subreddit).lower()))
    return lista_up, sub_origine


def aggiorno_db(db, cursore, nome_file_txt, set_sub, sub_scelte):
    # ADESSO: Lavoro col database
    # 1) Aggiorno la tabella sub con tutti i nuovi subreddit che trovo negli upvote dell'utente
    # Se la subreddit è già nella tabella sub avrei un errore perchè il campo è specificato come UNIQUE
    for sub in set_sub:
        try:
            cursore.execute('''INSERT INTO sub(subreddit) VALUES (?)''', (sub,))
        except sql3.IntegrityError:
            print("sub già presente nella tabella sub: r/", sub)
    db.commit()

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
            input("STOP")


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
                        # splitlines() separa le stringhe lette da read(), e fa una lista
                        copiafilesub = filesub.read().lower().splitlines()

                        percorso_filesub = os.path.join(cartella_user, sceltatxt)
                        print("\nContenuto del file %s\n" % sceltatxt)
                        print(copiafilesub)

                        # confronto tra gli elementi di due liste:
                        # la lista di sub dei post upvotati e le sub contenute nel file selezionato
                        # seleziona le sub al di fuori dal file scelto così da poterle mostrare

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
                return percorso_filenuovo, listasub, filenome[:-4]
        # Restituito il percorso della cartella dell'user con l'elenco di sub scritte pocanzi ma non salvate in un file.
            return cartella_user, listasub, 'temp'

        # TODO opzione speciale per salvare tutti i file upvotati direttamente!
        """elif opz == 3:
            listasub = list()
            for el in upvoted:
                listasub.append(upvoted.subreddit)
            return cartella_user, listasub
        else:
            continue"""


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


def doppione(cursore, post):
    """Se il post è già presente nel database -> è un doppione -> TRUE
    Se tuttavia il file non c'è chiede all'utente se salvarlo!
    Se il post è assente nel database, o se l'utente decide di salvarlo comunque -> return FALSE
    Aggiorna poi il database sia se il post è stato salvato che se non lo è stato"""

    try:
        print("Ho un post")
        url = str(post.url)
    except:
        print("Ho un URL")
        url = str(post)
    print("\nDOPPIONE?\n", url)

    # Vediamo se l'url del post è già nella tabella file_salvati
    # Seleziono percorso perchè mi serve dopo per ottenere la cartella dove andare a cercare il file.
    # Se il file esiste nella cartella è certamente un doppione e si salta, se manca, si chiede all'utente se salvarlo.
    cursore.execute('SELECT percorso FROM file_salvati WHERE url=?', (url,))
    selezioni_percorso = cursore.fetchone()

    # Se il post già esiste nel database: controlliamo se esiste il file
    if selezioni_percorso:
        print("l'url è già presente nel database, controllo che ci sia il file")
        nome = os.path.basename(url)
        # Controllo se il file è tra la cartella commenti
        if os.path.isfile(os.path.join(PATH_SLUT_COM, nome)):
            print("Commento già in lista. Saltato!")
            return True
        # Controllo se il file è tra la cartella immagini o video
        elif not os.path.isfile(os.path.join(PATH_SLUT_IMG, nome)) or os.path.isfile(os.path.join(PATH_SLUT_VID, nome)) or os.path.isfile(os.path.join(PATH_SLUT_VID, nome, '.webm')) or os.path.isfile(os.path.join(PATH_SLUT_VID, nome, '.mp4')):
            print("Url nel database ma file non esistente!\n", nome)
            mess = 'vuoi salvare il file: ' + url + '? S/N\n'
            opz = scelta(mess)
        # Se l'utente ha detto di voler salvare il file allora, la funzione restituisce False e si procedere al salvataggio
            if opz:
                return False
        # In questo caso l'utente ha detto di non voler salvare il file, quindi la funz restituisce True
            return True

    # Se l'url non è presente nel database restituisci False così da poter avviare la fase di salvataggio in main()
    if not selezioni_percorso:
        print("NUOVO, SLURP")
        return False


def aggiungi_a_db(db, cursore, post, nome_file_txt, percorso=''):
    """Aggiorna la tabella file_salvati, aggiungendo i dati sia di post che dei commenti
    Per i post aggiunge TUTTO, per i commenti aggiunge solo URL, il file_txt, ed il percorso in cui è salvato"""

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
                print("Salviamo le immagini ALBUM!")
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