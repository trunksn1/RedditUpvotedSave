#!/usr/bin/python 3.6
# -*- coding: utf-8 -*-

import os, pprint, re, requests, shelve, shutil, sys, time
import bs4, praw, send2trash

from gfycat.client import GfycatClient
from login import reddit_login, inizializza, crea_prawini

#regex = r'http.*imgur.*/[0-9a-zA-Z]*(jpeg|jpg|png|gif)? | http.*gfycat.*(jpeg|jpg|png|gif|gfv|gifv|gfy)?'
#regex = r'http.*imgur[0-9a-zA-Z/\.]*|http.*gfycat[0-9a-zA-Z/\.]*'
regex = r'^http.*' #|www).*'

PATH_SLUT = 'Y:\\Giochi\\Mega'
PATH_SLUT_IMG = 'Y:\\Giochi\\Mega\\nsfw_img'
PATH_SLUT_VID = 'Y:\\Giochi\\Mega\\nsfw_vid'
LISTA_IMMAGINI = []
LISTA_VIDEO = []
LISTA_GIFV = []
DOPPIONI = []
#LISTA_ALBUM = []
IRRISOLTI = []
LISTE = [LISTA_IMMAGINI, LISTA_VIDEO, LISTA_GIFV,]

def main():
	print('partiti!')
	
	#Fase preparatoria dei login e delle configurazioni
	sfigatto = GfycatClient()
	redditore, cartella_user = reddit_login()
	
	#creo la lista degli upvotes e la stampo a schermo
	lista_upvotes = crea_lista_up(redditore)
	num = 1
	for el in lista_upvotes:
		printa_up(num, el)
		num += 1
	
	#creo un set delle sub in cui sono stati postati i post upvotati
	#e la stampo
	sub_upvotes = prepara_sub(lista_upvotes)
	pprint.pprint (sub_upvotes)
	
	percorso, sub_scelte = scelta_subreddit(cartella_user, lista_upvotes)
	print (sub_scelte)
	
	if os.path.isfile(percorso):
		#TODO:Chiedi se vuoi aggiungere altre sub al file passato
		print ('file')
	else:
		#TODO: Chiedi se vuoi salvare questa lista in un file da poter riutilizzare
		print ('path')
		
		
	#Crea/Legge il file con i vecchi post upvotati, preparando così il controllo per i doppioni	
	file_old_up = txt_upvote_passati()
	lista_old_up = file_old_up.readlines()
	
	#Seleziono i post upvotati provenienti dalle sub indicate prima
	lista_new_up = selezione_post (lista_upvotes, sub_scelte)
	print('printo i submission selezionati!\n')
	num = 1
	for post in lista_new_up:
		printa_up(num, post)
		num += 1
	
	#Da ogni post nella lista creata viene estrapolato l'url a cui si riferisce e questo inserito in una lista pronto per essere prima checkato per doppione, e poi salvato
	for elemento in lista_new_up:
		smista_formato(elemento, sfigatto)
		
	#A questo punto per ogni lista nel megalistone, guarda se gli elementi sono dei doppioni
	for lista_formato in LISTE:
		for elemento in lista_formato:
			#Se l'elemento è un doppione lo toglie dalla sua lista di appartenenza
			if check_doppione(elemento, lista_old_up, file_old_up):
				lista_formato.remove(elemento)
		pprint.pprint(lista_formato)
			
	#Andiamo a salvare:
	for immagine in LISTA_IMMAGINI:
		da_salvare(immagine, PATH_SLUT_IMG)
	for video in LISTA_VIDEO:
		da_salvare(video, PATH_SLUT_IMG)
	for gifvideo in LISTA_GIFV:
		down_gifv(gifvideo)
		
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
	
	#Cerchiamo di pescare golosità nei commenti
	for post in lista_new_up:
		commenti = parse_commenti(post)
	
	rimozione = [LISTA_IMMAGINI, LISTA_VIDEO, LISTA_GIFV, DOPPIONI]
	
	#PROVA CON UN ELEMENTO SOLO ALLA VOTLA:
	remove_upvote(DOPPIONI[-1])
	
	#for lista in rimozione:
	#	for el in lista:
	#		remove_upvote(el)

def parse_commenti(post):
	patt_imgur = re.compile(regex)
	post.comments.replace_more(limit=0)
	comment_queue = post.comments[:]  # Seed with top-level
	while comment_queue:
		comment = comment_queue.pop(0)
		bytestring = comment.body.encode('utf-8', 'replace')
		#comment =  comment.encode('ascii', 'replace')
		cerca = patt_imgur.search(str(bytestring, 'utf-8'))
		if cerca:
			#print (type(cerca))
			print (cerca.group(0))
			try:
				print(cerca.group(1))
			except:
				pass
		comment_queue.extend(comment.replies)
	#TODO legge i commenti in cerca di album ed affini
	
def remove_upvote(el):
	print('sto per togliere l\'upvote a: ', el.subreddit, el.title.encode(errors='replace'), el.url, el.shortlink)
	while True:
		opzione = input("posso togliere gli upvote dai post oramai salvati? [s/n]")
		if opzione.lower() not in ['s', 'n']:
			print('risposta errata')
			continue
		elif opzione.lower() == 's':
			print("mò levo tutto! ADDIO ", el)
			el.clear_vote()
			break
			
def selezione_post (lista_upvotes, sub_scelte):
	'''prende la lista con gli upvotes dell'utente, e le sub indicate 
	restituisce una lista contenente dei post upvotati provenienti solo 
	da quelle sub'''

	post_selezionati = list()
	for up in lista_upvotes:
		#url = up.url
		sub = up.subreddit
		if sub in sub_scelte:
			post_selezionati.append(up)	
	return post_selezionati
	
def crea_lista_up(redditore):
	'''Restituisce una lista contenente	i post upvotati dal redditor. 
	Per accedere alla subreddit di ogni elemento si fa:
	lista[el].subreddit'''
	
	lista_up = list()
	
	#.upvoted() Return a ListingGenerator for items the user has upvoted.
	upvoted = redditore.upvoted()
	
	#crea la lista
	for upvote in upvoted:
		lista_up.append(upvote)
	return lista_up

def prepara_sub(lista_upvotes):
	'''Prende la lista degli upvotes dell'utente e restituisce un set 
	che contiene le sub di origine dei post upvotati'''
	print("siamo in prepara_sub")
	sub_origine = set()
	for el in lista_upvotes:
		sub_origine.add((str(el.subreddit)))
	return sub_origine
		
def printa_up(numero, post):
	sub = str(post.subreddit)
	lunghezza = len(sub)
	if lunghezza > 12:
		spazi = '\t'
	elif lunghezza > 6:
		spazi = '\t\t'
	else:
		spazi = '\t\t\t'
	print (str(numero) + ') /r/',post.subreddit, spazi, post.title.encode(errors='replace'))

def scelta_subreddit(cartella_user, upvoted):
	'''Chiede le subreddit in cui si trovano i post_upvotati che vuoi salvare
	passando la path della cartella user e la lista di upvotes
	restituisce una tupla contenente: 
	1)il percorso della cartella e la 	lista delle sub scelte, oppure 
	2)il percorso per il file txt ed la	variabile file.read() se già esistente'''
		
	while True:
		print('\n\n***Hai due possibilità per salvare i file:' +
		'\n[1]Importare un file di subreddit dalla cartella:' +
		'\n%s' %cartella_user +
		'\n[2] scegliere manualmente i subreddit \t***' )
		
		scelta = int(input())
		
		#TODO L'idea è di mettere questi dati in un file config
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
	'''crea o legge, poi restituisce il file txt che conterrà/contiene
	l'url dei vecchi post upvotati'''
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
	
def check_doppione(url, lista_passato, file_passato):
	print('\ncheck doppione: ', url)
	for rigo in lista_passato:
		#Se l'url che sto controllando è già nella lista di upvote vecchi allora controllo se il file esiste effettivamente
		if url in rigo:
			nome = os.path.basename(url)
			
			immag = os.path.isfile(os.path.join(PATH_SLUT_IMG, nome))
			singola_immag = os.path.isfile(os.path.join(PATH_SLUT_IMG, nome + '.jpg'))
			vid = os.path.isfile(os.path.join(PATH_SLUT_VID, nome))
			gfy = os.path.isfile(os.path.join(PATH_SLUT_VID, nome + '.mp4'))
			gifv = os.path.isfile(os.path.join(PATH_SLUT_VID, nome[:-4] + 'mp4'))
			print (immag, singola_immag, vid,  gfy, gifv)
			
			#controlla se il file esiste
			if not (immag or vid or gfy or gifv or singola_immag):
				print('Url già presente in lista, ma file assente!')
				while True:
					scelta = input('vuoi salvare il file: ' + str(url) +'? S/N\n')
					if scelta.lower() in ['n', 's']:
						break
				if scelta.lower() == 's':
					return False
				elif scelta.lower() == 'n':
					DOPPIONI.append(url)
					return True			
			else:
				print(url + ' già presente, con relativo file. DOPPIONISSIMO!')
				DOPPIONI.append(url)
				return True	
		
		else: continue
			#cerca nel prossimo rigo
			
	print (url + ' è nuovo! SLURP')
	file_passato.write(url + '\n')
	return False
	
def smista_formato(post, sfigatto):
	'''smista i post tra i vari formati e restituisce liste contenente 
	l'url finali da avviare al check_doppione'''
	
	print('siamo in smista_formato')
	
	pre_url = post.url
	url = str(pre_url)
	
	if url.endswith('.jpg') or url.endswith('.png') or url.endswith('.gif'):
		print ('abbiamo a che fare con una immagine!\n' + url)
		#da_salvare(url, PATH_SLUT_IMG)
		LISTA_IMMAGINI.append(url)
		
	elif url.startswith('http://imgur.com/a/'):
		#BISOGNA TENERE CONTO NELLE LISTE sia delle immagini che dell'url del post???
		#COME LO GIOSTRO?
		print ('abbiamo a che fare con ALBUM IMGUR!\n' + url)
		album_imgur(url) 
		#url = album_imgur(url) 
		#LISTA_ALBUM.append(url)
		
	elif url.startswith('http://imgur.com'):
		print ('abbiamo a che fare con una immagine IMGUR!\n')
		url = 'https://i.imgur.com//' + os.path.basename(url) + '.jpg'
		print (str(url))
		#da_salvare(url, PATH_SLUT_IMG)
		LISTA_IMMAGINI.append(url)
		
	elif url.startswith('https://imgur.com'):
		print ('HTTPS IMGUR!\n' + url)
		url = decifra_imgur_https(url)
		print(url)
		#da_salvare(url, PATH_SLUT_IMG)
		if url.endswith('.jpg') or url.endswith('.png') or url.endswith('.gif'):
			LISTA_IMMAGINI.append(url)
		elif url.endswith('.mp4'):
			LISTA_VIDEO.append(url)
			
	elif url.startswith('https://gfycat.com/') or url.startswith('https://giant.gfycat.com/'):
		print ("siamo su gfycat!", url)
		sfnome = os.path.basename(url)
		sfinfo = sfigatto.query_gfy(sfnome)
		#pprint.pprint (sfinfo)
		sfurl = sfinfo['gfyItem']['mp4Url']
		print(sfurl)
		#da_salvare(sfurl, PATH_SLUT_VID)
		LISTA_VIDEO.append(sfurl)
		
	elif url.endswith('.gifv'):
		print ("siamo su imgur con una GIFV!", url)
		#down_gifv(url)
		LISTA_GIFV.append(url)
		
	else:
		print ('***********ODDIO!!! dove siamo?!?********', url)
		IRRISOLTI.append(post)		

	return LISTA_IMMAGINI, LISTA_VIDEO, LISTA_GIFV, IRRISOLTI

def album_imgur(url):
	res = requests.get(url)
	res.raise_for_status()
	soup = bs4.BeautifulSoup(res.text, "html.parser")
	album = soup.select("a img[src]")#("[class==post-image-container]")
	for num in range(len(album)):	
		foto = 'http:' + album[num]['src']
		if foto.endswith('.jpg') or foto.endswith('.png') or foto.endswith('.gif'):
			print('foto dell album', foto)
			LISTA_IMMAGINI.append(foto)
			#da_salvare(foto, PATH_SLUT_IMG)
		if foto.endswith('.gifv'):
			LISTA_GIFV.append(foto)
			#down_gifv(url)
					
def decifra_imgur_https (url):
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
	
def down_gifv (url):
	#UNICO CHE NON RICEVE UNA LISTA MA UN URL, UNIFORMARE???
	#Questo vale solo per le gifv del sito IMGUR.COM
	print('FIGVVVAFA?')
	res = requests.get(url)
	res.raise_for_status()
	soup = bs4.BeautifulSoup(res.text, "html.parser")
	elem = soup.select("body div source")
	print(elem)
	#print(url)
	#print(len(elem))
	#print (elem)
	ind = 'http:' + (elem[0]['src'])
	#print(elem[0]['src'])
	da_salvare(ind, PATH_SLUT_VID)
	#if os.path.isfile(os.path.join(PATH_SLUT_VID, os.path.basename(ind))):
	#	print('File già esistente!: ', ind)
	#	return
	#res = requests.get(ind)
	#res.raise_for_status()	
	#vidFile = open(os.path.join(PATH_SLUT_VID, os.path.basename(ind)) , 'wb')
	#salva (vidFile, res)
	
	#return elem[0]['src']
	
def da_salvare (url, cartella_file):
	if os.path.isfile(os.path.join(cartella_file, os.path.basename(url))):
		print('File già esistente!: ', url)
		return
	res = requests.get(url)
	res.raise_for_status()
	salvato = open(os.path.join(cartella_file, os.path.basename(url)), 'wb')
	salva(salvato, res)
		
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

