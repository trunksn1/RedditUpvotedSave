#!/usr/bin/python 3.6
# -*- coding: utf-8 -*-
import os, pprint, re, requests, shelve, shutil, sys, time
import sqlite3 as sql3
import bs4, praw, send2trash
import config as cg
from gfycat.client import GfycatClient

def reddit_login(): #COMPLETARE non funziona: il secondo login non va mai in porto!
	while True:	
		username = input('what\'s your reddit username?\n')
		cartella = os.path.join(os.sys.path[0], username)
		inizializza(username, cartella)
		db_file = os.path.join(cartella, username + '.db')

		try:
			reddit = praw.Reddit('rus', user_agent='RedditUpvotedSave (by /u/jacnk3)')
			redditore = reddit.user.me()

		except:
			print('oops, non riesco a loggare!! Hai sbagliato qualcosa!')
			print(os.getcwd())
			
			time.sleep(2)
			os.chdir('..')
			while True:
				print("vuoi rimuovere la cartella appena creata? \n" + cartella)
				sel = input("S/N")
				if sel.upper() == "S":
					shutil.rmtree(cartella, ignore_errors = True)
					break
				elif sel.upper() == "N":
					break
			time.sleep(2)
			continue
		else:
			print('niente exception')
			print(os.getcwd())
			# Connettiamo il database e verifichiamo che ci siano le tabelle
			db = sql3.connect(db_file)
			database(db)

			return redditore, cartella, db
		
def inizializza(username, cartella):
	"""Cerca nella cwd la cartella col nome dell'username fornito
	se non la trova la crea, crea le cartelle in Y per i file
	crea il file config per fare dopo il praw.ini, e lo apre
	Se la trova, cerca e apre il file config.
	Restituisce la cartella dell'utente """

	print('inizializziamo')
	if not os.path.exists(cartella):
		os.makedirs(cartella, exist_ok=True)
		configFile = shelve.open(os.path.join(cartella, 'config'))
		configFile['username'] = username
		#TODO: va messo un check casomai l'utente sbaglia la password!
		configFile['password'] = input ('what\'s /u/%s password?\n' %username)
	# Se esiste, leggila
	else:
		configFile = shelve.open(os.path.join(cartella, 'config'))

	cg.PATH_SLUT = os.path.join(cg.PATH_SLUT, username)
	cg.PATH_SLUT_COM = os.path.join(cg.PATH_SLUT, 'comm')
	cg.PATH_SLUT_VID = os.path.join(cg.PATH_SLUT, 'vid')
	cg.PATH_SLUT_IMG = os.path.join(cg.PATH_SLUT, 'img')

	if not os.path.exists(cg.PATH_SLUT):
		os.makedirs(cg.PATH_SLUT)
		os.chdir(cg.PATH_SLUT)
	#elif not os.path.exists(cg.PATH_SLUT_COM):
		os.makedirs(cg.PATH_SLUT_COM, exist_ok=True)
	#elif not os.path.exists(cg.PATH_SLUT_VID):
		os.makedirs(cg.PATH_SLUT_VID, exist_ok=True)
	#elif not os.path.exists(cg.PATH_SLUT_IMG):
		os.makedirs(cg.PATH_SLUT_IMG, exist_ok=True)
	else:
		print("Esistono già le path")

	os.chdir(cartella)
	crea_prawini(configFile)

def crea_prawini(configFile):
	print('creo praw.ini')
	with open ('praw.ini', 'w') as fileini:
		'''Crea il file praw.ini da usare successivamente'''
		fileini.write('[rus]\n')
		fileini.write('username=' + configFile['username'] + '\n')
		fileini.write('password=' + configFile['password'] + '\n')
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
		db.execute('CREATE TABLE "file_salvati" ( `post` TEXT NOT NULL UNIQUE, `url` TEXT NOT NULL UNIQUE, `subID` INTEGER NOT NULL, `txt_subreddit` TEXT, `filetype` TEXT, `ID` INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE )')
		db.execute('CREATE TABLE `non_salvati` ( `post` TEXT NOT NULL UNIQUE, `url` TEXT NOT NULL UNIQUE, `ID` INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE )')
		db.execute('CREATE TABLE "selezioni" ( `fileselezione` TEXT NOT NULL UNIQUE, `ID` INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE )')
		db.execute('CREATE TABLE `sub` ( `subreddit` TEXT UNIQUE, `ID` INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE )')
		db.execute('CREATE TABLE `selezioni_sub` ( `selezioniID` INTEGER NOT NULL, `subID` INTEGER NOT NULL )')