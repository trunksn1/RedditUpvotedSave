#!/usr/bin/python 3.6

import os, pprint, requests, shelve, sys
import bs4, praw

from gfycat.client import GfycatClient

FILE_PRAW = 'praw.ini'
PATH_SLUT = 'Y:\\Giochi\\Mega'
PATH_SLUT_IMG = 'Y:\\Giochi\\Mega\\nsfw_img'
PATH_SLUT_VID = 'Y:\\Giochi\\Mega\\nsfw_vid'

def main():
	#TODO: vedi se il file praw.ini esiste
	#se non esiste crealo
	#altrimenti fai subito il login
	
	cartella_user = inizializza()
	os.chdir(cartella_user)

	'''try:
		reddit = praw.Reddit('rus', user_agent='RedditUpvotedSave (by /u/jacnk3)')
		redditore = reddit.user.me()    
		print('e adesso?')
	except:
		print('oops, non riesco a loggare!! Hai sbagliato qualcosa!')
		sys.exit()
	else:
		print('niente try')
		print(cartella_user)
		
		#TODO cancella cartella_user
		#reinizializza'''

	redditore = reddit_login()
	
	sfigatto = GfycatClient()
	
	lista_imgup, lista_vidup = upvote_redditore(redditore, sfigatto, cartella_user)

	img(lista_imgup) 
	vid(lista_vidup)
	
def reddit_login(): #COMPLETARE
	while True:
		try:
			reddit = praw.Reddit('rus', user_agent='RedditUpvotedSave (by /u/jacnk3)')
			redditore = reddit.user.me()    
			print('e adesso?')
		except:
			print('oops, non riesco a loggare!! Hai sbagliato qualcosa!')
			reddit_login()
		else:
			print('niente exception')
			print(cartella_user)
			return redditore
		
		#TODO cancella cartella_user
		#reinizializza
	
def inizializza():
	"""Cerca nella cwd la cartella col nome dell'username fornito
	se non la trova la crea, crea le cartelle in Y per i file
	crea il file config per fare dopo il praw.ini, e lo apre
	Se la trova, cerca e apre il file config.
	Restituisce la cartella dell'utente """
	
	username = input('what\'s your reddit username?\n')
	cartella = os.path.join(os.sys.path[0], username)
	if not os.path.exists(cartella):
		os.makedirs(cartella, exist_ok=True)
		configFile = shelve.open(os.path.join(cartella, 'config'))
		configFile['username'] = username
		#TODO: va messo un check casomai l'utente sbaglia la password!
		configFile['password'] = input ('what\'s /u/%s password?\n' %username)
		os.chdir('y:')
		os.makedirs(PATH_SLUT_IMG, exist_ok=True)
		os.makedirs(PATH_SLUT_VID, exist_ok=True)
	else:
		configFile = shelve.open(os.path.join(cartella, 'config'))
	os.chdir(cartella)
	crea_prawini(configFile)
	return (cartella)

def crea_prawini(configFile):
	with open (FILE_PRAW, 'w') as fileini:
		'''Crea il file praw.ini da usare successivamente'''
		fileini.write('[rus]\n')
		fileini.write('username=' + configFile['username'] + '\n')
		fileini.write('password=' + configFile['password'] + '\n')
		#TODO: come fare a nascondere queste info sensibili?
		fileini.write('client_id=IIjAZV_ce3rkgA\n')
		fileini.write('client_secret=qXdKaWzr9CxBEsFGto0IEgHtKEg')
		
def upvote_redditore (redditore, sfigatto, cartella_user):    
	lista_immagini = list()
	lista_video = list()
	listone = list()
	        
	upvoted = redditore.upvoted()

	for upvote in upvoted:
		print(upvote)
		url = upvote.url
		lista_urls = upvote_passati(redditore)
		
		print ('for loop in upvote_redditore')
		print(cartella_user)
		sub_di_origine_scelte = scelta_subreddit (cartella_user, upvoted)
		print(sub_di_origine_scelte)
		#TODO: piuttosto che questo check sciocco
		#creare un file con una lista di tutti i subreddit interessanti
		if upvote in sub_di_origine_scelte: #upvote.subreddit != 'dwarffortress':
			listone.append(url.rstrip('?1'))
			
			#YODO: se l'url è in lista ed il file è nel computer salta il resto e togli l'upvote.
			if doppione(url, lista_urls):
				continue
			else:			
				if str(url).endswith('.jpg') or str(url).rstrip('?1').endswith('.png') or str(url).endswith('.gif'):
					lista_immagini.append(url.rstrip('?1'))
				elif str(url).startswith('https://gfycat.com/'):
					sfnome = os.path.basename(url)
					sfinfo = sfigatto.query_gfy(sfnome)
					#pprint.pprint (sfinfo)
					sfurl = sfinfo['gfyItem']['mp4Url']
					#video = 'https://giant.gfycat.com/' + str(upvote.url)[18:] + '.webm'
					lista_video.append(sfurl)
				else:
					lista_immagini.append(url.rstrip('?1'))
		#pprint.pprint(listone)
	#printa_post(upvoted)
	return (lista_immagini, lista_video)

def scelta_subreddit(cartella_user, upvoted):
	os.chdir(cartella_user)
	printa_post(upvoted)
	while True:
		scelta = int(input('importare un file di subreddit [1] o scegliere manualmente i subreddit [2]?\t'))
		if scelta == 1:
			print(os.listdir(cartella_user))
			sceltatxt = input('quale file? specifica anche l\'estensione\t')
			if os.path.isfile(sceltatxt):
				with open (sceltatxt, 'r') as filesub:
					return filesub
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
			
			return listasub
		else: continue
	
	return 1
	
	

def printa_post(lista_upvoted):
	num = 1
	for up in lista_upvoted:
		sub = str(up.subreddit)
		if len(sub) > 12:
			spazi = '\t'
		elif len(sub) > 6:
			spazi = '\t\t'
		else:
			spazi = '\t\t\t'
		print (str(num) + ') /r/',up.subreddit, spazi, up.title.encode(errors='replace'))
		num += 1
	
	
def upvote_passati(utente):
	#TODO: cerca la lista dei doppioni in PATH_SLUT. Se c'è l'apre e si prepara ad
	#controllare se i post dell'utente già ci sono e nel caso li salto (e toglie l'upvote)
	#aggiunge i post mancanti
	os.chdir(PATH_SLUT)
	if not os.path.isfile(os.path.join(PATH_SLUT, 'listone.txt')):
		modo = 'w+'
	else:
		modo = 'a+'
	#with open ('listone.txt', modo) as lista:
	#	return lista
	lista = open ('lista_upvote.txt', modo)
	return lista
	
def doppione(url, lista_url):
	lettura = lista_url.read()
	#Se l'Url non è nella scheda, prosegui e vai a salvarlo
	if url not in lettura:
		lista_url.write(url)
		return False
	#se l'Url è nella scheda, vedi se c'è il file a cui si riferisce, se no, vai a salvarlo
	elif not os.path.isfile(os.path.join(PATH_SLUT_IMG, os.path.basename(url))) or os.path.isfile(os.path.join(PATH_SLUT_VID, os.path.basename(url))):
		print('Url già presente in lista, ma file assente!')
		scelta = input('vuoi salvare il file: ' + str(url) +'? S/N')
		while scelta != 'n' or scelta != 's':	
			if scelta.lower() == 's':
				return False
			elif scelta.lower() == 'n':
				return True
	#se l'url è nella lista ed esiste pure il file allora è proprio un doppione da eliminare
	else:
		return True
		#TODO: controllare se il file esiste ancora nella cartella...
	
	
def img(lista):
	for i in range(len(lista)):
		res = requests.get(lista[i])
		res.raise_for_status()
		if lista[i].endswith('.gifv'):
			lista[i] = lista[i][:-4] + 'mp4'
			imageFile = open(os.path.join(PATH_SLUT_IMG, os.path.basename(lista[i])), 'wb')
		else:		
			imageFile = open(os.path.join(PATH_SLUT_IMG, os.path.basename(lista[i])) , 'wb')
		salva(imageFile, res)

def vid(lista):	
	for i in range(len(lista)):
		res = requests.get(lista[i])
		res.raise_for_status()	
		vidFile = open(os.path.join(PATH_SLUT_VID, os.path.basename(lista[i])) , 'wb')
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

