import os
import sqlite3 as sql3
import sys

import praw
import prawcore
from src.helpers import crea_prawini

import src.config as cg


class Utente():
    def __init__(self, username='', password='', redditor='', db=''):
        self.username = username
        self.password = password
        self.redditor = redditor
        self.db = db
        self.cartella = os.path.join(os.sys.path[0], 'utenti', username)

    def __str__(self):
        return "{}, {}, {}, {}".format(self.username, self.redditor, self.cartella, self.db)

    def attiva_utente(self):
        self.login_redditor()
        self.database()

    def login_redditor(self):
        if os.path.exists(self.cartella):
            print("cartella con utente già esistente")

            os.chdir(self.cartella)
            reddit = praw.Reddit('rus', user_agent='RedditUpvotedSave (by /u/jacnk3)')
            if self.is_redditor(reddit):
                self.redditor = reddit.user.me()
                os.chdir(self.cartella)
                print('connesso il selezionato {}'.format(self.redditor))
            else:
                print('Utente non esistente')
                sys.exit()
        else:
            reddit = praw.Reddit(client_id=cg.prawini_client_id,
                                 client_secret=cg.prawini_client_secret,
                                 user_agent=cg.prawini_user_agent,
                                 username=self.username,
                                 password=self.password)
            if self.is_redditor(reddit):
                self.cartella = os.path.join(os.sys.path[0], 'utenti', self.username)
                os.makedirs(self.cartella)
                os.chdir(self.cartella)
                crea_prawini(self, self.cartella)
                self.redditor = reddit.user.me()
            else:
                print('Utente non esistente')
                sys.exit()

    def is_redditor(self, reddit):
        try:
            redditor_esistente = reddit.user.me()
        except prawcore.exceptions.OAuthException:
            print("AuthException", str(sys.exc_info()[0]))
            return False
        except:
            print("Ex2", sys.exc_info()[0])
            return False
        else:
            print('nome del redditore: {}\ntipo del redditore: {}'.format(redditor_esistente, type(redditor_esistente)))
            return True

    def database(self):
        db_file = os.path.join(self.cartella, self.username + '.db')
        # Connettiamo il database e verifichiamo che ci siano le tabelle
        db = sql3.connect(db_file)
        """Verifica che il database abbia la sue tabelle, altrimenti le crea"""
        try:
            # cerca la tabella file_salvati nel database
            db.execute("SELECT * FROM file_salvati")
        except:
            # crea le tabelle nel database
            print("eccetto db")
            db.execute(
                'CREATE TABLE "file_salvati" ( `post` TEXT UNIQUE, `url` TEXT NOT NULL UNIQUE, `subID` INTEGER, `txt_subreddit` TEXT, `percorso` TEXT, `ID` INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE )')
            db.execute(
                'CREATE TABLE "non_salvati" ( `post` TEXT UNIQUE, `url` TEXT NOT NULL UNIQUE, `ID` INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE )')
            db.execute(
                'CREATE TABLE "selezioni" ( `fileselezione` TEXT NOT NULL UNIQUE, `ID` INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE )')
            db.execute(
                'CREATE TABLE `sub` ( `subreddit` TEXT UNIQUE, `ID` INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE )')
            db.execute('CREATE TABLE `selezioni_sub` ( `selezioniID` INTEGER NOT NULL, `subID` INTEGER NOT NULL )')

        #self.db = db.cursor()
        self.db = db