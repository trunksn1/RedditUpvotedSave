import os, pprint, requests, shelve, sys
import bs4, praw

from gfycat.client import GfycatClient

FILE_PRAW = 'praw.ini'
PATH_SLUT_IMG = 'Y:\\Giochi\\Mega\\nsfw_img'
PATH_SLUT_VID = 'Y:\\Giochi\\Mega\\nsfw_vid'

def main():
	#TODO: vedi se il file praw.ini esiste
	#se non esiste crealo
	#altrimenti fai subito il login
	
	os.chdir(inizializza())
	
	reddit = praw.Reddit('rus', user_agent='RedditUpvotedSave (by /u/jacnk3)')
	
	sfigatto = GfycatClient()
	
	lista_imgup, lista_vidup = upvote_redditore(reddit, sfigatto)
	
	img(lista_imgup) 
	vid(lista_vidup)
	
def inizializza():
	"""Cerca nella cwd la cartella col nome dell'username fornito
	se non la trova la crea, crea le cartelle in Y per i file
	crea il file config per fare dopo il praw.ini, e lo apre
	Se la trova, cerca e apre il file config.
	Restituisce la cartella dell'utente """
	
	username = input('what\'s your reddit username?\n')
	cartella = os.path.join(os.sys.path[0], username)
	print(cartella)
	if not os.path.exists(cartella):
		os.makedirs(cartella, exist_ok=True)
		configFile = shelve.open(os.path.join(cartella, 'config'))
		configFile['username'] = username
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
		

#x = reddit.subreddit('redditdev')
#print(x)

#print(x.display_name)  # Output: redditdev
#print(x.title)         # Output: reddit Development
#print(x.description)   # Output: A subreddit for discussion of ...

def upvote_redditore (reddit, sfigatto):
	redditore = reddit.user.me()             
	lista_immagini = list()
	lista_video = list()
	listone = list()
	for upvote in redditore.upvoted():
		#TODO: piuttosto che questo check sciocco
		#creare un file con una lista di tutti i subreddit interessanti
		if upvote.over_18 and upvote.subreddit != 'dwarffortress':
			listone.append(upvote.url.rstrip('?1'))
			if str(upvote.url).endswith('.jpg') or str(upvote.url).rstrip('?1').endswith('.png') or str(upvote.url).endswith('.gif'):
				lista_immagini.append(upvote.url.rstrip('?1'))
			elif str(upvote.url).startswith('https://gfycat.com/'):
				sfnome = os.path.basename(upvote.url)
				sfinfo = sfigatto.query_gfy(sfnome)
				pprint.pprint (sfinfo)
				sfurl = sfinfo['gfyItem']['mp4Url']
				#video = 'https://giant.gfycat.com/' + str(upvote.url)[18:] + '.webm'
				lista_video.append(sfurl)
			else:
				lista_immagini.append(upvote.url.rstrip('?1'))
	pprint.pprint(listone)
	return (lista_immagini, lista_video)
#client_id: 2_C4C9qX
#client_secret: cVT6HYz_9SxNirYk49kNHJcfTqdiy6qDlNtvqO-TOwR7-WKtrNTxNoyC2U-juJJ5

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
	#for i in range(len(lista)):
	#	res = requests.get(lista[i])
	#	res.raise_for_status()
	#	imageFile = open(os.path.join('nsfw_img', os.path.basename(lista[i])) , 'wb')
	#	for pezzo in res.iter_content(100000):
	#		imageFile.write(pezzo)
	#	imageFile.close()
		
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

if __name__ == "__main__":
	main()
