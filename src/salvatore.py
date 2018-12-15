from os import path, makedirs
import glob, re, requests
import praw
from gfycat.client import GfycatClient
from imgurpython import ImgurClient
from src import config as cg
from src.siti import gfycazz, imagur
from src.helpers import link_gifv, aggiungi_a_db, aggiungi_non_salvato
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import QThread, pyqtSignal


class Salvatore():
    POST = []
    COMMENTI = []
    DOPPIONI = []

    def __init__(self, utente, post_da_salvare, sub_txt, mostratore, dir_per_salvare=cg.PATH_SLUT, app=''):
        self.app = app
        self.utente = utente
        self.post = post_da_salvare
        self.dir_salvare = dir_per_salvare
        self.sub_txt = sub_txt
        self.mostratore = mostratore
        self.IMGUR = ImgurClient(cg.imgur_client_id, cg.imgur_client_secret)
        self.SFIGATTO = GfycatClient()
        self.imposta_path()
        self.analizza_post()

    def imposta_path(self):
        dir = ("{},{},{}".format(self.dir_salvare, self.utente.username, self.sub_txt)).split(',')
        self.dir_salvare = path.join(*dir)
        print(self.dir_salvare)
        self.PATH_SLUT_IMG = path.join(self.dir_salvare, 'img')
        self.PATH_SLUT_COM = path.join(self.dir_salvare, 'comm')
        self.PATH_SLUT_VID = path.join(self.dir_salvare, 'vid')
        print('{}{}{}'.format(self.PATH_SLUT_IMG, self.PATH_SLUT_COM, self.PATH_SLUT_VID))

    def analizza_post(self):
        print('analizzatore')
        self.si_a_tutti = ''
        self.mostratore.show()
        self.mostratore.progressBar.setRange(0, 0)

        for post in self.post:
            print('\n******NUOVO POST******')
            stato = self.is_doppione(post)
            self.lavoratore = SalvaThread(self, post, stato)
            self.lavoratore.start()
            """
            if not self.is_doppione(post):
                pass            
                self.smista_e_salva(post)
                #salva il post
            #parse dei commenti
            #smista i commenti
            #salva i commenti
        """
        self.lavoratore.finito.connect(self.aggiorna_barra)

    def aggiorna_barra(self):
        self.progressBar.setRange(0, 1)

    def is_doppione(self, post):
        """Se il post è già presente nel database -> è un doppione -> TRUE
        Se tuttavia il file non c'è chiede all'utente se salvarlo!
        Se il post è assente nel database, o se l'utente decide di salvarlo comunque -> return FALSE
        Aggiorna poi il database sia se il post è stato salvato che se non lo è stato"""
        print("post? ", type(post) == praw.models.reddit.submission.Submission)
        try:
            url = str(post.url)
        except:
            url = str(post)
        print("{}\tDOPPIONE?".format(url))
        in_tabella = self.is_in_db(url)

        # Se il post già esiste nel database: controlliamo se esiste il file
        if in_tabella:
            print('in tabella')
            if self.is_in_dir(url):
                print('nella cartella')
                return True
        print('da nessuna parte! NON Doppione')
        return False

        #TODO:sto dividendo questa funzione in due: la parte sottoscritta è nella funzione is_in_db()
        """
        self.cursore = self.utente.db.cursor()
        self.cursore.execute('SELECT percorso FROM file_salvati WHERE url=?', (url,))
        selezioni_percorso = self.cursore.fetchone()
        

        
            # Controllo se il file è nella cartella commenti
            if glob.glob(path.join(self.PATH_SLUT_COM, nome) + '.*'):
                print("Commento già in lista. Saltato!\n{}".format(glob.glob(path.join(self.PATH_SLUT_COM, nome) + '.*')))
                return True
            # Controllo se il file è tra la cartella immagini o video, Se non viene trovato chiederò di risalvarlo
            elif not (glob.glob(path.join(self.PATH_SLUT_IMG, nome) + '.*') or glob.glob(
                        path.join(self.PATH_SLUT_VID, nome) + '.*')):
                if self.si_a_tutti:
                    print('Sto Risalvando TUTTI come detto BADRONE')
                    return False
                risp = self.chiedi(url)
                if risp == self.domanda.Yes:
                    print('Risalviamo')
                    return False
                elif risp == self.domanda.YesToAll:
                    self.si_a_tutti = True
                    print('Risalveremo TUTTI')
                    return False
                else:
                    print('ok no. Fottiti')
                    return True
            #Controlla se l'url puntava a una cartella
            elif(glob.glob(path.join(self.dir_salvare, '**', nome), recursive=True)):
                print(glob.glob(path.join(self.dir_salvare, '**', nome), recursive=True))
            #elif (glob.glob(path.join(self.PATH_SLUT_IMG, nome)) or glob.glob(
                    #path.join(self.PATH_SLUT_VID, nome)) or glob.glob(path.join(self.PATH_SLUT_COM, nome))):
                print("Cartella presente, probabilmente un album")
                return True
            else:
                print("Confermato DOPPIONE")
                return True
        # Se l'url non è presente nel database restituisci False
        else:
            print("NUOVO, SLURP")
            return False
        """

    def is_in_db(self, url):
        # Vediamo se l'url del post è già nella tabella file_salvati
        # Seleziono percorso perchè mi serve dopo per ottenere la cartella dove andare a cercare il file.
        self.cursore = self.utente.db.cursor()
        self.cursore.execute('SELECT percorso FROM file_salvati WHERE url=?', (url,))
        selezioni_percorso = self.cursore.fetchone()
        if selezioni_percorso:
            return True
        return False

    def is_in_dir(self, url):
        #TODO: Valutare questa correzzione a che cazzo serve
        #Serve perchè i file .gifv vengono salvati come file .mp4
        if url.endswith('.gifv'):
            url = url[:-4] + 'mp4'
        nome = path.basename(url)

        if glob.glob(path.join(self.PATH_SLUT_COM, nome) + '.*'):
            print("Commento già in lista. Saltato!\n{}".format(glob.glob(path.join(self.PATH_SLUT_COM, nome) + '.*')))
            return True
        # Controllo se il file è tra la cartella immagini o video, Se non viene trovato chiederò di risalvarlo
        elif not (glob.glob(path.join(self.PATH_SLUT_IMG, nome) + '.*') or glob.glob(
                    path.join(self.PATH_SLUT_VID, nome) + '.*')):
            if self.si_a_tutti:
                print('Sto Risalvando TUTTI come detto BADRONE')
                return False
            risp = self.chiedi(url)
            if risp == self.domanda.Yes:
                print('Risalviamo')
                return False
            elif risp == self.domanda.YesToAll:
                self.si_a_tutti = True
                print('Risalveremo TUTTI')
                return False
            else:
                print('ok no. Fottiti')
                return True
        # Controlla se l'url puntava a una cartella
        elif (glob.glob(path.join(self.dir_salvare, '**', nome), recursive=True)):
            print(glob.glob(path.join(self.dir_salvare, '**', nome), recursive=True))
            # elif (glob.glob(path.join(self.PATH_SLUT_IMG, nome)) or glob.glob(
            # path.join(self.PATH_SLUT_VID, nome)) or glob.glob(path.join(self.PATH_SLUT_COM, nome))):
            print("Cartella presente, probabilmente un album")
            return True
        else:
            print("Confermato DOPPIONE")
            return True

    def chiedi(self, url):
        self.domanda = QMessageBox()
        mess = "Url nel database ma file non esistente! Vuoi salvare il file: {}?".format(url)
        res = self.domanda.question(self.domanda, 'Ciao', mess, self.domanda.Yes | self.domanda.No | self.domanda.YesToAll)
        return res

    def smista_e_salva(self, post):
        print("\nSMISTO POST")
        url = ''
        # Ho un post o un commento? In base a questo scelgo la cartella in cui salvare tutto.
        try:
            url = str(post.url)
            path_img = self.PATH_SLUT_IMG
            path_vid = self.PATH_SLUT_VID
        except:
        # Per salvare nella cartella dei commenti
            url = str(post)
            path_img, path_vid = self.PATH_SLUT_COM, self.PATH_SLUT_COM
        print(url, end='\t')

        # if url.endswith(('.jpg', '.png', '.gif')):
        if url.endswith(('.jpg', '.png', '.gif')):
            print('abbiamo a che fare con una immagine!\n')
            return self.da_salvare(url, path_img)

        elif url.endswith('.gifv'):
            print("siamo su imgur con una GIFV!")
            link = link_gifv(url)
            if link:
                return self.da_salvare(link, path_vid)

        elif url.endswith('.mp4'):
            print("è un video!")
            return self.da_salvare(url, path_vid)

        pattern = re.compile(r'(.*?imgur.*)|(.*?redd.*)|(.*?gifsound.*)|(.*?gfycat.*)')
        v = pattern.search(url)
        try:
            tupla_search = v.groups()
        except:
            print("non da imgur reddit o gfycat")
            aggiungi_non_salvato(self.utente.db, self.cursore, post)
        else:
            if tupla_search[0]:  # imgur
                print("imgur")

                link = imagur(self.IMGUR, url)
                print(link)
                if isinstance(link, list):
                    path_album = path.join(path_img, path.basename(url))
                    print(path_album)
                    try:
                        makedirs(path_album)
                    except FileExistsError:
                        print("album già esistente")
                        #return 'None'  # Se l'album già esiste non va risalvato!
                        #TODO:forse se l'album già esiste non va nemmeno inserito nel db come non salvato
                        aggiungi_non_salvato(self.utente.db, self.cursore, post)
                    for el in link:
                        self.da_salvare(el,
                                   path_album)  # in questo caso non gli faccio restituire niente o non salvo le singole immagini
                elif type(link) == None:
                    print("Problemi ad ottenere le immagini dal link: ", link)
                    aggiungi_non_salvato(self.utente.db, self.cursore, post)
                    #return 'None'
                elif link == 404:
                    print("Problemi ad ottenere le immagini dal link: ", link)
                    aggiungi_non_salvato(self.utente.db, self.cursore, post)
                    #return 'None'
                else:
                    #TODO e se non sono immagini ma gifv?
                    return self.da_salvare(link)

            elif tupla_search[1]:  # forse reddit
                print("reddit")
                # input("Quali sono le possibilità? STOP")
                aggiungi_non_salvato(self.utente.db, self.cursore, post)
                #return 'None'
            elif tupla_search[2]:  # forse reddit
                print("gifsound")
                # non sò come usarlo
                aggiungi_non_salvato(self.utente.db, self.cursore, post)
                #return 'None'
            elif tupla_search[3]:  # gfycat
                print("gfycat")
                try:
                    link = gfycazz(self.SFIGATTO, url)
                except Exception as e:
                    print(e)
                if (type(link) == None or link == 404):
                    print("Problemi ad ottenere le immagini dal link: ", link)
                    #sospeto(...)
                    aggiungi_non_salvato(self.utente.db, self.cursore, post)
                    #return 'None'
                else:
                    return self.da_salvare(link)
            else:
                # TODO: Da aggiungere alla tabella non_salvati
                print("non riconosciuto")
                # sospeto(...)
                aggiungi_non_salvato(self.utente.db, self.cursore, post)
                #return 'None'

    def parse_commenti(self, cursore, post):
        """Se ho un post, ho un oggetto specifico di reddit, se ho un commento invece maneggio un URL"""
        print("parse commenti del post: ", post.shortlink)
        regex = r'http[^\s()]*'  # |www).*'
        # Se capisco bene questo try/except serve solo a ME per capire se sto trattando un post o un commento
        try:  # se ho un post
            post.comments.replace_more(limit=0)
            #post.comments.replace_more(limit=None, threshold=0)
        except:  # se ho un commento
            post.replace_more(limit=0)
            #post.comments.replace_more(limit=None, threshold=0)

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
                #controllare adesso se il commento è un doppione...
                if not self.is_doppione(elem):
                    self.COMMENTI.add(elem)

    def da_salvare(self, url, cartella_file=''):
        # Se il programma funziona bene, questo check qua è inutile
        """if os.path.isfile(os.path.join(cartella_file, os.path.basename(url))):
            print('File già esistente!: ', url)
            return il percorso di dove va a salvare il file"""
        if url is None:
            print("C'è stato un errore a ricavare il file da salvare")
            return
        if not cartella_file:
            if url.endswith(('.jpg', '.png', '.gif')):
                cartella_file = self.PATH_SLUT_IMG

            elif url.endswith(('.gifv', '.mp4', '.webm')):
                cartella_file = self.PATH_SLUT_VID

        res = requests.get(url)
        stato = res.status_code
        if stato != 200:
            print("qualcosa è andato storto.")
            print(stato)
            print(url)
            return stato
        else:
            try:
                salvato = open(path.join(cartella_file, path.basename(url)), 'wb')
                self.salva(salvato, res)
                print("Salvato: ", url)
                return cartella_file
            except:
                # TODO piazzare l'url salvato da qualche parten
                print("qualcosa è andato storto al salvataggio dell'url: " + str(url))
                return 505

    def salva(self, path, res):
        for pezzo in res.iter_content(100000):
            path.write(pezzo)
        path.close()



class SalvaThread(QThread):
    finito = pyqtSignal()
    def __init__(self, salvatore, post, doppione):
        QThread.__init__(self)
        self.salvatore = salvatore
        self.post = post
        self.doppione = doppione

        print('STO AVVIANDO IL SALVATANDOO!1')

    def run(self):
        # print('Pre-RUNNANDO')
        self.lavora()

    def lavora(self):
        print('Salvatando!')

        if not self.doppione:
            self.smista_e_salva(self.post)
        #self.parse_commenti()
                #salva il post
            #parse dei commenti
            #smista i commenti
            #salva i commenti

    def is_doppione(self, post):
        """Se il post è già presente nel database -> è un doppione -> TRUE
        Se tuttavia il file non c'è chiede all'utente se salvarlo!
        Se il post è assente nel database, o se l'utente decide di salvarlo comunque -> return FALSE
        Aggiorna poi il database sia se il post è stato salvato che se non lo è stato"""
        print(type(post) == praw.models.reddit.submission.Submission)
        try:
            url = str(post.url)
        except:
            url = str(post)
        print("\n{}\nDOPPIONE?".format(url))

        # Vediamo se l'url del post è già nella tabella file_salvati
        # Seleziono percorso perchè mi serve dopo per ottenere la cartella dove andare a cercare il file.
        # Se il file esiste nella cartella è certamente un doppione e si salta, se manca, si chiede all'utente se salvarlo.
        #self.utente.db.execute('SELECT percorso FROM file_salvati WHERE url=?', (url,))
        #selezioni_percorso = self.utente.db.fetchone()
        self.cursore = self.salvatore.utente.db.cursor()
        self.cursore.execute('SELECT percorso FROM file_salvati WHERE url=?', (url,))
        selezioni_percorso = self.cursore.fetchone()

        #TODO: Valutare questa correzzione a che cazzo serve
        #Serve perchè i file .gifv vengono salvati come file .mp4
        if url.endswith('.gifv'):
            url = url[:-4] + 'mp4'
        nome = path.basename(url)

        # Se il post già esiste nel database: controlliamo se esiste il file
        if selezioni_percorso:
            # Controllo se il file è nella cartella commenti
            if glob.glob(path.join(self.PATH_SLUT_COM, nome) + '.*'):
                print("Commento già in lista. Saltato!\n{}".format(glob.glob(path.join(self.salvatore.PATH_SLUT_COM, nome) + '.*')))
                return True
            # Controllo se il file è tra la cartella immagini o video, Se non viene trovato chiederò di risalvarlo
            elif not (glob.glob(path.join(self.salvatore.PATH_SLUT_IMG, nome) + '.*') or glob.glob(
                        path.join(self.salvatore.PATH_SLUT_VID, nome) + '.*')):
                if self.si_a_tutti:
                    print('Sto Risalvando TUTTI come detto BADRONE')
                    return False
                risp = self.chiedi(url)
                if risp == self.domanda.Yes:
                    print('Risalviamo')
                    return False
                elif risp == self.domanda.YesToAll:
                    self.si_a_tutti = True
                    print('Risalveremo TUTTI')
                    return False
                else:
                    print('ok no. Fottiti')
                    return True
            #Controlla se l'url puntava a una cartella
            elif(glob.glob(path.join(self.salvatore.dir_salvare, '**', nome), recursive=True)):
                print(glob.glob(path.join(self.salvatore.dir_salvare, '**', nome), recursive=True))
            #elif (glob.glob(path.join(self.PATH_SLUT_IMG, nome)) or glob.glob(
                    #path.join(self.PATH_SLUT_VID, nome)) or glob.glob(path.join(self.PATH_SLUT_COM, nome))):
                print("Cartella presente, probabilmente un album")
                return True
            else:
                print("Confermato DOPPIONE")
                return True
        # Se l'url non è presente nel database restituisci False
        if not selezioni_percorso:
            print("NUOVO, SLURP")
            return False

    def chiedi(self, url):
        self.domanda = QMessageBox()
        mess = "Url nel database ma file non esistente! Vuoi salvare il file: {}?".format(url)
        res = self.domanda.question(self.domanda, 'Ciao', mess, self.domanda.Yes | self.domanda.No | self.domanda.YesToAll)
        return res

    def smista_e_salva(self, post):
        print("\nSMISTO POST")
        url = ''
        # Ho un post o un commento? In base a questo scelgo la cartella in cui salvare tutto.
        try:
            url = str(post.url)
            path_img = self.salvatore.PATH_SLUT_IMG
            path_vid = self.salvatore.PATH_SLUT_VID
        except:
        # Per salvare nella cartella dei commenti
            url = str(post)
            path_img, path_vid = self.salvatore.PATH_SLUT_COM, self.salvatore.PATH_SLUT_COM
        print(url, end='\t')

        # if url.endswith(('.jpg', '.png', '.gif')):
        if url.endswith(('.jpg', '.png', '.gif')):
            print('abbiamo a che fare con una immagine!\n')
            return self.da_salvare(url, path_img)

        elif url.endswith('.gifv'):
            print("siamo su imgur con una GIFV!")
            link = link_gifv(url)
            if link:
                return self.da_salvare(link, path_vid)

        elif url.endswith('.mp4'):
            print("è un video!")
            return self.da_salvare(url, path_vid)

        pattern = re.compile(r'(.*?imgur.*)|(.*?redd.*)|(.*?gifsound.*)|(.*?gfycat.*)')
        v = pattern.search(url)
        try:
            tupla_search = v.groups()
        except:
            print("non da imgur reddit o gfycat")
            aggiungi_non_salvato(self.salvatore.utente.db, self.cursore, post)
        else:
            if tupla_search[0]:  # imgur
                print("imgur")

                link = imagur(self.salvatore.IMGUR, url)
                print(link)
                if isinstance(link, list):
                    path_album = path.join(path_img, path.basename(url))
                    print(path_album)
                    try:
                        makedirs(path_album)
                    except FileExistsError:
                        print("album già esistente")
                        #return 'None'  # Se l'album già esiste non va risalvato!
                        #TODO:forse se l'album già esiste non va nemmeno inserito nel db come non salvato
                        aggiungi_non_salvato(self.salvatore.utente.db, self.cursore, post)
                    for el in link:
                        self.da_salvare(el,
                                   path_album)  # in questo caso non gli faccio restituire niente o non salvo le singole immagini
                elif type(link) == None:
                    print("Problemi ad ottenere le immagini dal link: ", link)
                    aggiungi_non_salvato(self.salvatore.utente.db, self.cursore, post)
                    #return 'None'
                elif link == 404:
                    print("Problemi ad ottenere le immagini dal link: ", link)
                    aggiungi_non_salvato(self.salvatore.utente.db, self.cursore, post)
                    #return 'None'
                else:
                    #TODO e se non sono immagini ma gifv?
                    return self.da_salvare(link)

            elif tupla_search[1]:  # forse reddit
                print("reddit")
                # input("Quali sono le possibilità? STOP")
                aggiungi_non_salvato(self.salvatore.utente.db, self.cursore, post)
                #return 'None'
            elif tupla_search[2]:  # forse reddit
                print("gifsound")
                # non sò come usarlo
                aggiungi_non_salvato(self.salvatore.utente.db, self.cursore, post)
                #return 'None'
            elif tupla_search[3]:  # gfycat
                print("gfycat")
                try:
                    link = gfycazz(self.salvatore.SFIGATTO, url)
                except Exception as e:
                    print(e)
                if (type(link) == None or link == 404):
                    print("Problemi ad ottenere le immagini dal link: ", link)
                    #sospeto(...)
                    aggiungi_non_salvato(self.salvatore.utente.db, self.cursore, post)
                    #return 'None'
                else:
                    return self.da_salvare(link)
            else:
                # TODO: Da aggiungere alla tabella non_salvati
                print("non riconosciuto")
                # sospeto(...)
                aggiungi_non_salvato(self.salvatore.utente.db, self.cursore, post)
                #return 'None'

    def parse_commenti(self, cursore, post):
        """Se ho un post, ho un oggetto specifico di reddit, se ho un commento invece maneggio un URL"""
        print("parse commenti del post: ", post.shortlink)
        regex = r'http[^\s()]*'  # |www).*'
        # Se capisco bene questo try/except serve solo a ME per capire se sto trattando un post o un commento
        try:  # se ho un post
            post.comments.replace_more(limit=0)
            #post.comments.replace_more(limit=None, threshold=0)
        except:  # se ho un commento
            post.replace_more(limit=0)
            #post.comments.replace_more(limit=None, threshold=0)

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
                #controllare adesso se il commento è un doppione...
                if not self.is_doppione(elem):
                    self.salvatore.COMMENTI.add(elem)

    def da_salvare(self, url, cartella_file=''):
        # Se il programma funziona bene, questo check qua è inutile
        """if os.path.isfile(os.path.join(cartella_file, os.path.basename(url))):
            print('File già esistente!: ', url)
            return il percorso di dove va a salvare il file"""
        if url is None:
            print("C'è stato un errore a ricavare il file da salvare")
            return
        if not cartella_file:
            if url.endswith(('.jpg', '.png', '.gif')):
                cartella_file = self.salvatore.PATH_SLUT_IMG

            elif url.endswith(('.gifv', '.mp4', '.webm')):
                cartella_file = self.salvatore.PATH_SLUT_VID

        res = requests.get(url)
        stato = res.status_code
        if stato != 200:
            print("qualcosa è andato storto.")
            print(stato)
            print(url)
            return stato
        else:
            try:
                salvato = open(path.join(cartella_file, path.basename(url)), 'wb')
                self.salva(salvato, res)
                print("Salvato: ", url)
                return cartella_file
            except:
                # TODO piazzare l'url salvato da qualche parten
                print("qualcosa è andato storto al salvataggio dell'url: " + str(url))
                return 505

    def salva(self, path, res):
        for pezzo in res.iter_content(100000):
            path.write(pezzo)
        path.close()
