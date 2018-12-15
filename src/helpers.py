import os, requests
import src.config as cg
import bs4, praw
import sqlite3 as sql3
from PyQt5 import QtGui

def crea_prawini(utente, path=os.getcwd()):
    if type(utente) == dict:
        username = utente['username']
        password = utente['password']
    else:
        username = utente.username
        password = utente.password
    with open (os.path.join(path, 'praw.ini'), 'w') as fileini:
        '''Crea il file praw.ini da usare successivamente'''
        fileini.write('[rus]\n')
        fileini.write('username=' + username + '\n')
        fileini.write('password=' + password + '\n')
        fileini.write('client_id=' + cg.prawini_client_id + '\n')
        fileini.write('client_secret=' + cg.prawini_client_secret)

def database(db):
    """Verifica che il database abbia la sue tabelle, altrimenti le crea"""
    try:
        # cerca la tabella file_salvati nel database
        db.execute("SELECT * FROM file_salvati")
    except:
        # crea le tabelle nel database
        db.execute('CREATE TABLE "file_salvati" ( `post` TEXT UNIQUE, `url` TEXT NOT NULL UNIQUE, `subID` INTEGER, `txt_subreddit` TEXT, `percorso` TEXT, `ID` INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE )')
        db.execute('CREATE TABLE "non_salvati" ( `post` TEXT UNIQUE, `url` TEXT NOT NULL UNIQUE, `ID` INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE )')
        db.execute('CREATE TABLE "selezioni" ( `fileselezione` TEXT NOT NULL UNIQUE, `ID` INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE )')
        db.execute('CREATE TABLE `sub` ( `subreddit` TEXT UNIQUE, `ID` INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE )')
        db.execute('CREATE TABLE `selezioni_sub` ( `selezioniID` INTEGER NOT NULL, `subID` INTEGER NOT NULL )')

def link_gifv(url):
    # Questo vale solo per le gifv del sito IMGUR.COM
    try:
        res = requests.get(url)
        res.raise_for_status()
        soup = bs4.BeautifulSoup(res.text, "html.parser")
        elem = soup.select("body div source")
        ind = 'http:' + (elem[0]['src'])
        return ind
    except:
        print("c'è stato un problema con le gifv di imgur")

def aggiungi_a_db(db, cursore, post, nome_file_txt, percorso=''):
    """Aggiorna la tabella file_salvati, aggiungendo i dati sia di post che dei commenti
    Per i post aggiunge TUTTO, per i commenti aggiunge solo URL, il file_txt, ed il percorso in cui è salvato"""

    # Comportamento diverso se abbiamo un post o un commento:
    if isinstance(post, praw.models.reddit.submission.Submission):
        # Ricaviamo l'id della subreddit originaria del post dalla tabella sub:
        cursore.execute('SELECT id FROM sub WHERE subreddit=?', (str(post.subreddit).lower(),))
        rigo_sub = cursore.fetchone()
        #print(rigo_sub[0])

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


def aggiungi_non_salvato(db, cursore, elemento):
    #TODO: dovrebbe assicurarsi di non mettere nella tabella non salvati elementi che invece sono nella tabella dei salvati.
    """Aggiungo l'elemento che non sono riuscito a scaricare nella tabella non_salvati così da poter riprovarci in futuro"""
    print("Fallimento, aggiungo l'elemento alla tabella non_salvati")
    if isinstance(elemento, praw.models.reddit.submission.Submission):
        try:
            cursore.execute('INSERT INTO non_salvati(post, url) VALUES(?,?)',
                            (str(elemento.shortlink), str(elemento.url)))
        except:
            print("Già presente nella tabella non_salvati, ", elemento.url)
        else:
            db.commit()
            print("Aggiunto")
    else:
        try:
            cursore.execute('INSERT INTO non_salvati(url) VALUES(?)', (str(elemento),))
        except:
            print("Già presente nella tabella non_salvati, ", elemento)
        else:
            db.commit()
            print("Aggiunto")