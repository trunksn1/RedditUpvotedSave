#!/usr/bin/python 3.6
# -*- coding: utf-8 -*-

import os, pprint, re, requests, shelve, shutil, sys, time
import bs4, praw, send2trash

from gfycat.client import GfycatClient

FILE_PRAW = 'praw.ini'
PATH_SLUT = 'Y:\\Giochi\\Mega'
PATH_SLUT_IMG = 'Y:\\Giochi\\Mega\\nsfw_img'
PATH_SLUT_VID = 'Y:\\Giochi\\Mega\\nsfw_vid'
LISTA_IMMAGINI = []
LISTA_VIDEO = []
LISTA_GIFV = []
IRRISOLTI = []
DOPPIONI = []

def main():
	print('partiti!')
	sfigatto = GfycatClient()
	redditore, cartella_user = reddit_login()
	
	lista_upvotes = crea_lista_up(redditore, sfigatto, cartella_user)
	
	sub_upvotes = set()
	for el in lista_upvotes:
		sub_upvotes.add((str(el.subreddit)))
	pprint.pprint (sub_upvotes)
	
	percorso, sub_scelte = scelta_subreddit(cartella_user, lista_upvotes)
	print (sub_scelte)
	
	if os.path.isfile(percorso):
		#TODO:Chiedi se vuoi aggiungere altre sub al file passato
		print ('file')
	else:
		#TODO: Chiedi se vuoi salvare questa lista in un file da poter riutilizzare
		print ('path')
		
	elenco_old_up = txt_upvote_passati()
	
	lista_old_up = elenco_old_up.readlines()
	lista_new_up = selezione_post (lista_upvotes, sub_scelte)
	
	for elemento in lista_new_up:
		if not check_doppione(elemento, lista_old_up, elenco_old_up):
			formato(elemento, sfigatto)
			
	print('ok fatto')			
	
	print ('immagini salvate')
	print(LISTA_IMMAGINI)
	print('video salvati')
	print(LISTA_VIDEO)
	print('GIFV salvati')	
	print(LISTA_GIFV) 
	print('irrisolti!!!')
	print(IRRISOLTI) 
	print("doppioni")
	print(DOPPIONI)
	
	for post in lista_new_up:
		commenti = parse_commenti(post)
	
	rimozione = [LISTA_IMMAGINI, LISTA_VIDEO, LISTA_GIFV, DOPPIONI]
	
	#PROVA CON UN ELEMENTO SOLO ALLA VOTLA:
	remove_upvote(DOPPIONI[-1])
	
	#for lista in rimozione:
	#	for el in lista:
	#		remove_upvote(el)

def parse_commenti(post):
	patt_imgur = re.compile(r'.*imgur.*\s|.*gfycat.*\s')
	post.comments.replace_more(limit=0)
	comment_queue = post.comments[:]  # Seed with top-level
	while comment_queue:
		comment = comment_queue.pop(0)
		bytestring = comment.body.encode('utf-8', 'replace')
		#comment =  comment.encode('ascii', 'replace')
		cerca = patt_imgur.search(str(bytestring, 'utf-8'))
		if cerca:
			print (type(cerca))
			print (cerca.group(0))
		comment_queue.extend(comment.replies)
	#TODO legge i commenti in cerca di album ed affini
	

def remove_upvote(el):
	print('sto per togliere l\'upvote a: ', el.subreddit, el.title.encode(errors='replace'), el.url, el.shortlink)
	while True:
		opzione = input("posso togliere gli upvote dai post oramai salvati? [s/n]")
		if opzione.lower() not in ['s', 'n']:
			continue
		elif opzione.lower() == 's':
			el.clear_vote()
			break
			
			

def selezione_post (lista_upvotes, sub_scelte):
	'''prende la listadi submission degli upvotes dell'utente, e le sub indicate come
	interessanti, restituisce una lista contenente i post upvotati 
	provenienti da quelle sub'''
	#url_selezionati = list()
	post_selezionati = list()
	for up in lista_upvotes:
		#url = up.url
		sub = up.subreddit
		if sub in sub_scelte:
			post_selezionati.append(up)
	print('printo i submission selezionati!\n')
	print (post_selezionati)
	return post_selezionati
	
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
	with open (FILE_PRAW, 'w') as fileini:
		'''Crea il file praw.ini da usare successivamente'''
		fileini.write('[rus]\n')
		fileini.write('username=' + configFile['username'] + '\n')
		fileini.write('password=' + configFile['password'] + '\n')
		#TODO: come fare a nascondere queste info sensibili?
		fileini.write('client_id=IIjAZV_ce3rkgA\n')
		fileini.write('client_secret=qXdKaWzr9CxBEsFGto0IEgHtKEg')

def crea_lista_up(redditore, sfigatto, cartella_user):
	'''restituisce una lista di submission, per ogni elemento
	puoi accedere alla sua subreddit con:
	lista[el].subreddit'''
	
	lista_up = list()
	
	upvoted = redditore.upvoted()
	num = 1
	for upvote in upvoted:
		lista_up.append(upvote)
		printa_up(num, upvote)
		num += 1
	return lista_up
	
def printa_up(numero, upvotato):
	sub = str(upvotato.subreddit)
	lunghezza = len(sub)
	if lunghezza > 12:
		spazi = '\t'
	elif lunghezza > 6:
		spazi = '\t\t'
	else:
		spazi = '\t\t\t'
	print (str(numero) + ') /r/',upvotato.subreddit, spazi, upvotato.title.encode(errors='replace'))

def scelta_subreddit(cartella_user, upvoted):
	'''passandogli la path della cartella user e la lista di upvotes
	restituisce una tupla contenente, il percorso della cartella e la
	lista delle sub scelte, oppure il percorso per il file txt ed la
	variabile file.read() se già esistente'''
	
	os.chdir(cartella_user)
	
	while True:
		print('\n\n***Hai due possibilità per salvare i file:' +
		'\n[1]Importare un file di subreddit dalla cartella:' +
		'\n%s' %cartella_user +
		'\n[2] scegliere manualmente i subreddit \t***' )
		
		scelta = int(input())
		
		if scelta == 1:
			print(os.listdir(cartella_user))
			sceltatxt = input('quale file? specifica anche l\'estensione\t')
			if os.path.isfile(sceltatxt):
			#Lo apro in append mode per poter vedere se posso modificarlo
				with open (sceltatxt, 'r+') as filesub:
					percorso_filesub = os.path.join(cartella_user, sceltatxt)
					lista_filesub = filesub.readlines()
					for i in range (len(lista_filesub)):
						lista_filesub[i] = lista_filesub[i].rstrip('\n')
					return percorso_filesub, lista_filesub
			else: 
				print('il file %s non esiste' %sceltatxt)
				continue
				
		elif scelta == 2:
			listasub = list()
			sub_indicata = 1
			while sub_indicata:
				sub_indicata = input('quale subreddit scegli? bada bene a come scrivi! Lascia bianco per proseguire\n')
				listasub.append(sub_indicata)
				print(listasub)
			#TODO: chiedi all'utente se vuole creare un file con queste 
			#specifiche sub che ha scelto, o se ne vuole modificare uno esistente
			return cartella_user, listasub
		elif scelta == 3:
			listasub = list()
			for el in upvoted:
				listasub.append(upvoted.subreddit)
			return cartella_user, listasub
		else: continue

	
def txt_upvote_passati():
	#TODO: cerca la lista dei doppioni in PATH_SLUT. Se c'è l'apre e si prepara ad
	#controllare se i post dell'utente già ci sono e nel caso li salto (e toglie l'upvote)
	#aggiunge i post mancanti
	os.chdir(PATH_SLUT)
	if not os.path.isfile(os.path.join(PATH_SLUT, 'lista_upvote.txt')):
		modo = 'w+'
	else:
		modo = 'r+'
	#with open ('listone.txt', modo) as lista:
	#	return lista
	print ('modo del listone: ', modo)
	lista = open ('lista_upvote.txt', modo)
	return lista
	
def check_doppione(post, lista_passato, file_passato):
	url = post.url
	print('check doppione: ', url)
	for rigo in lista_passato:
		if url in rigo:
			nome = os.path.basename(url)
			
			immag = os.path.isfile(os.path.join(PATH_SLUT_IMG, nome))
			vid = os.path.isfile(os.path.join(PATH_SLUT_VID, nome))
			gfy = os.path.isfile(os.path.join(PATH_SLUT_VID, nome + '.mp4'))
			gifv = os.path.isfile(os.path.join(PATH_SLUT_VID, nome[:-4] + 'mp4'))
			print (immag, vid,  gfy, gifv)
			
			#controlla se il file esiste
			if not (immag or vid or gfy or gifv):
				print('Url già presente in lista, ma file assente!')
				while True:
					scelta = input('vuoi salvare il file: ' + str(url) +'? S/N\n')
					if scelta.lower() in ['n', 's']:
						break
				if scelta.lower() == 's':
					return False
				elif scelta.lower() == 'n':
					DOPPIONI.append(post)
					return True			
			else:
				print(url + ' già presente, con relativo file. DOPPIONISSIMO!')
				DOPPIONI.append(post)
				return True	
		
		else: continue
			#cerca nel prossimo rigo
	print (url + ' è nuovo! SLURP')
	file_passato.write(url + '\n')
	return False
	
def formato(post, sfigatto):
	'''smista i post tra i vari formati e li avvia al salvataggio, restituendo
	le diverse liste dei post smistati pronti per essere rimossi, riutilizzati'''
	print('siamo in formato')	
	pre_url = post.url
	url = str(pre_url)#.rstrip('?1')
	if url.endswith('.jpg') or url.endswith('.png') or url.endswith('.gif'):
	#if str(url).endswith('.jpg') or str(url).rstrip('?1').endswith('.png') or str(url).endswith('.gif'):
		print ('abbiamo a che fare con una immagine!\n' + url)
		img(url)
		LISTA_IMMAGINI.append(post)
	elif url.startswith('http://imgur.com'):
		print ('abbiamo a che fare con una immagine IMGUR!\n' + url)
		url = url + '.jpg'
		img(url)
		LISTA_IMMAGINI.append(post)
	elif url.startswith('https://gfycat.com/'):
		print ("siamo su gfycat!", url)
		sfnome = os.path.basename(url)
		sfinfo = sfigatto.query_gfy(sfnome)
		#pprint.pprint (sfinfo)
		sfurl = sfinfo['gfyItem']['mp4Url']
		vid(sfurl)
		LISTA_VIDEO.append(post)
	elif url.endswith('.gifv'):
		print ("siamo su imgur con una GIFV!", url)
		down_gifv(url)
		LISTA_GIFV.append(post)
	else:
		print ('oddio, dove siamo?', url)
		IRRISOLTI.append(post)		

	return LISTA_IMMAGINI, LISTA_VIDEO, IRRISOLTI
	
def down_gifv (url):
	#UNICO CHE NON RICEVE UNA LISTA MA UN URL, UNIFORMARE???
	#Questo vale solo per le gifv del sito IMGUR.COM
	print('FIGVVVAFA?')
	res = requests.get(url)
	res.raise_for_status()
	soup = bs4.BeautifulSoup(res.text, "html.parser")
	elem = soup.select("body div source")
	#print(url)
	#print(len(elem))
	#print (elem)
	ind = 'http:' + (elem[0]['src'])
	#print(elem[0]['src'])
	if os.path.isfile(os.path.join(PATH_SLUT_VID, os.path.basename(ind))):
		print('File già esistente!: ', ind)
		return
	res = requests.get(ind)
	res.raise_for_status()	
	vidFile = open(os.path.join(PATH_SLUT_VID, os.path.basename(ind)) , 'wb')
	salva (vidFile, res)
	#return elem[0]['src']
	
def img(url):
	if os.path.isfile(os.path.join(PATH_SLUT_IMG, os.path.basename(url))):
		print('File già esistente!: ', url)
		return
	res = requests.get(url)
	res.raise_for_status()
	imageFile = open(os.path.join(PATH_SLUT_IMG, os.path.basename(url)), 'wb')
	salva(imageFile, res)

def vid(url):
	if os.path.isfile(os.path.join(PATH_SLUT_VID, os.path.basename(url))):
		print('File già esistente!: ', url)
		return
	res = requests.get(url)
	res.raise_for_status()	
	vidFile = open(os.path.join(PATH_SLUT_VID, os.path.basename(url)), 'wb')
	salva (vidFile, res)
	
def salva(path, res):
	for pezzo in res.iter_content(100000):
		path.write(pezzo)
	path.close()
	
if __name__ == "__main__":
	main()
	#ciao

#x = reddit.subreddit('redditdev')
#print(x)

#print(x.display_name)  # Output: redditdev
#print(x.title)         # Output: reddit Development
#print(x.description)   # Output: A subreddit for discussion of ...

	#for i in range(len(lista)):
	#	res = requests.get(lista[i])
	#	res.raise_for_status()
	#	imageFile = open(os.path.join('nsfw_img', os.path.basename(lista[i])) , 'wb')
	#	for pezzo in res.iter_content(100000):
	#		imageFile.write(pezzo)
	#	imageFile.close()


#	soup = bs4.BeautifulSoup(res.text , "html.parser")
#	imag = soup.select('img src')
	#try:
#	print(imag)
#	url = 'http:' + imag[0].get('src')
#	res = raise_for_status()
	#except:
	#	print('cazzi')
#pprint.pprint(lista_upvote)
#pprint.pprint(dir(upvote))
#		print(upvote.title)
#		print(upvote.subreddit)
#		print(upvote.thumbnail)
#		print(str(upvote.thumbnail_height) + '*' + str(upvote.thumbnail_width))

