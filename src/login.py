#!/usr/bin/python 3.6
# -*- coding: utf-8 -*-
import os, sys
import sqlite3 as sql3
import praw, prawcore, send2trash, shutil
from src import config as cg


#def inizializza(username, cartella):
def inizializza():
	"""Cerca nella cwd la cartella col nome dell'username fornito
	se non la trova la crea, crea le cartelle in Y per i file
	crea il file config per fare dopo il praw.ini, e lo apre
	Se la trova, cerca e apre il file config.
	Restituisce la cartella dell'utente """

	print('inizializziamo')
	#anzichè creare subito la cartella dell'utente, creane una temporanea, e solo quando il login riesce
	#Tcrea quella dell'utente, trasferiscine il contneuto e cancella quella vecchia
	diz_utente = {"username": "", "password": ""}
	diz_utente["username"] = input('what\'s your reddit username?\n')

	cartella = os.path.join(os.sys.path[0], diz_utente["username"])
	cartella_tmp = os.path.join(os.sys.path[0], "TMP")
	print(cartella)

	if not os.path.exists(cartella):
		print("utente .. non in memoria")
		# TODO: un try per vedere se sbagli password
		diz_utente["password"] = input('what\'s /u/%s password?\n' % diz_utente["username"])

		os.makedirs(cartella_tmp, exist_ok=True)
		os.chdir(cartella_tmp)

		crea_prawini(diz_utente) #Non ho bisogno di ricreare il file praw.ini se esiste giò!

		try:
			r, redditore = reddit_login(diz_utente, os.getcwd())
		except prawcore.exceptions.OAuthException:
			print("Hai fornito dati errati per il login su reddit CAZZONE!")
			raise
		except:
			print("Qualcosa altro è andato storto al login, riproviamo", sys.exc_info()[0])
			raise

		else:
			#Se è andato tutto ok, copiare il contenuto di tmp(praw.ini) nella cartella utente
			os.makedirs(cartella, exist_ok=True)
			shutil.move(os.path.join(cartella_tmp, "praw.ini"), cartella)
			os.chdir(cartella)
		finally: #Adesso rimuovi la cartella temporanea
			if not os.path.exists(cartella): #Se non c'è stato errore hai creato e stai lavorando nella cartella utente
				os.chdir("..") 				#Se hai attivato l'exception devi toglierti dalla cartella TMP
			send2trash.send2trash(cartella_tmp)

	else: #Se già esiste la cartella dell'utente
		os.chdir(cartella)
		try:
			r, redditore = reddit_login(diz_utente, os.getcwd())
		except FileNotFoundError:
			print("ERRORE, non trovo la cartella: %s" %cartella)
			raise
		except:
			print(sys.exc_info()[0])
			raise

	db_file = os.path.join(cartella, diz_utente["username"] + '.db')
	# Connettiamo il database e verifichiamo che ci siano le tabelle
	db = sql3.connect(db_file)
	database(db)

	return r, redditore, cartella, db


def reddit_login(username, cartella): #COMPLETARE non funziona: il secondo login non va mai in porto!
	reddit = praw.Reddit('rus', user_agent='RedditUpvotedSave (by /u/jacnk3)')
	redditore = reddit.user.me()
	return reddit, redditore


def inizializza_path(username, file_txt):
	cg.PATH_SLUT = os.path.join(cg.PATH_SLUT, username, file_txt)
	cg.PATH_SLUT_COM = os.path.join(cg.PATH_SLUT, 'comm')
	cg.PATH_SLUT_VID = os.path.join(cg.PATH_SLUT, 'vid')
	cg.PATH_SLUT_IMG = os.path.join(cg.PATH_SLUT, 'img')
	cg.PATH_SLUT_ALBUM = os.path.join(cg.PATH_SLUT, 'album')

	if not os.path.exists(cg.PATH_SLUT):
		os.makedirs(cg.PATH_SLUT)
		os.chdir(cg.PATH_SLUT)
		print(os.getcwd())
		input("STOP1")
	#elif not os.path.exists(cg.PATH_SLUT_COM):
		os.makedirs(cg.PATH_SLUT_COM, exist_ok=True)
	#elif not os.path.exists(cg.PATH_SLUT_VID):
		os.makedirs(cg.PATH_SLUT_VID, exist_ok=True)
	#elif not os.path.exists(cg.PATH_SLUT_IMG):
		os.makedirs(cg.PATH_SLUT_IMG, exist_ok=True)
		#os.makedirs(cg.PATH_SLUT_ALBUM, exist_ok=True)
	else:
		print("Esistono già le path")


def crea_prawini(utente):
	print('creo praw.ini')
	with open ('praw.ini', 'w') as fileini:
		'''Crea il file praw.ini da usare successivamente'''
		fileini.write('[rus]\n')
		fileini.write('username=' + utente['username'] + '\n')
		fileini.write('password=' + utente['password'] + '\n')
		fileini.write('client_id=' + cg.prawini_client_id + '\n')
		fileini.write('client_secret=' + cg.prawini_client_secret)

def database(db):
	"""Verifica che il database abbia la sue tabelle, altrimenti le crea"""
	try:
		# cerca la tabella file_salvati nel database
		db.execute("SELECT * FROM file_salvati")
	except:
		# crea le tabelle nel database
		print("eccetto db")
		db.execute('CREATE TABLE "file_salvati" ( `post` TEXT UNIQUE, `url` TEXT NOT NULL UNIQUE, `subID` INTEGER, `txt_subreddit` TEXT, `percorso` TEXT, `ID` INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE )')
		db.execute('CREATE TABLE "non_salvati" ( `post` TEXT UNIQUE, `url` TEXT NOT NULL UNIQUE, `ID` INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE )')
		db.execute('CREATE TABLE "selezioni" ( `fileselezione` TEXT NOT NULL UNIQUE, `ID` INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE )')
		db.execute('CREATE TABLE `sub` ( `subreddit` TEXT UNIQUE, `ID` INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE )')
		db.execute('CREATE TABLE `selezioni_sub` ( `selezioniID` INTEGER NOT NULL, `subID` INTEGER NOT NULL )')