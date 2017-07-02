#!/usr/bin/python 3.6
# -*- coding: utf-8 -*-
import os, pprint, re, requests, shelve, shutil, sys, time
import bs4, praw, send2trash
from gfycat.client import GfycatClient

def reddit_login(): #COMPLETARE non funziona: il secondo login non va mai in porto!
	while True:	
		username = input('what\'s your reddit username?\n')
		cartella = os.path.join(os.sys.path[0], username)
		inizializza(username, cartella)
		
		try:
			reddit = praw.Reddit('rus', user_agent='RedditUpvotedSave (by /u/jacnk3)')
			redditore = reddit.user.me()    
			print('e adesso?')
		except:
			print('oops, non riesco a loggare!! Hai sbagliato qualcosa!')
			print(os.getcwd())
			
			time.sleep(2)
			os.chdir('..')
			shutil.rmtree(cartella, ignore_errors = True)			
			
		else:
			print('niente exception')
			print(os.getcwd())
			return redditore, cartella
		
def inizializza(username, cartella):
	"""Cerca nella cwd la cartella col nome dell'username fornito
	se non la trova la crea, crea le cartelle in Y per i file
	crea il file config per fare dopo il praw.ini, e lo apre
	Se la trova, cerca e apre il file config.
	Restituisce la cartella dell'utente """

	print('inizializziamo')
	print(os.path.exists(cartella))
	if not os.path.exists(cartella):
		os.makedirs(cartella, exist_ok=True)
		configFile = shelve.open(os.path.join(cartella, 'config'))
		configFile['username'] = username
		#TODO: va messo un check casomai l'utente sbaglia la password!
		configFile['password'] = input ('what\'s /u/%s password?\n' %username)
		os.chdir('y:')
		os.makedirs(PATH_SLUT_IMG, exist_ok=True)
		os.makedirs(PATH_SLUT_VID, exist_ok=True)
	#Se esiste, leggila
	else:
		configFile = shelve.open(os.path.join(cartella, 'config'))
	os.chdir(cartella)
	crea_prawini(configFile)

def crea_prawini(configFile):
	print('creo praw.ini')
	FILE_PRAW = 'praw.ini'
	with open (FILE_PRAW, 'w') as fileini:
		'''Crea il file praw.ini da usare successivamente'''
		fileini.write('[rus]\n')
		fileini.write('username=' + configFile['username'] + '\n')
		fileini.write('password=' + configFile['password'] + '\n')
		#TODO: come fare a nascondere queste info sensibili?
		fileini.write('client_id=IIjAZV_ce3rkgA\n')
		fileini.write('client_secret=qXdKaWzr9CxBEsFGto0IEgHtKEg')
