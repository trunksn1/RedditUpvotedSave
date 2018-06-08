"""Tutta Roba Vecchia
# Crea/Legge il file dove sono segnati tutti gli url dei vecchi post upvotati; servirà per il controllo dei doppioni
    #file_old_up = txt_upvote_passati(PATH_SLUT)
    #lista_old_up = file_old_up.readlines()

    # A questo punto per ogni lista nel megalistone, guarda se gli elementi sono dei doppioni
    for lista_formato in LISTE:

        # Perchè lista_formato[:]???
        # Perchè così iteri su una copia della lista, in modo che quando
        # modfichi la lista orginale non stai modificando la copia che stai usando per iterare nel ciclo!

        for elemento in lista_formato[:]:
            # Se l'elemento è un doppione lo toglie dalla sua lista di appartenenza
            if check_doppione(elemento, lista_old_up, file_old_up):
                lista_formato.remove(elemento)

    # Andiamo a salvare:
    for immagine in LISTA_IMMAGINI:
        da_salvare(immagine, PATH_SLUT_IMG)
    for video in LISTA_VIDEO:
        da_salvare(video, PATH_SLUT_VID)
    for gifvideo in LISTA_GIFV:
        down_gifv(gifvideo, cartella_file=PATH_SLUT_VID)

    print('RECAP POST')
    print(len(LISTA_IMMAGINI), 'immagini salvate')
    print(len(LISTA_VIDEO), 'video salvati')
    print(len(LISTA_GIFV), 'GIFV salvati')
    print(len(IRRISOLTI), 'irrisolti!!!')
    print(len(DOPPIONI), "doppioni")
    print(len(IRRISOLTI), "IRRISOLTI")
    print(len(DIZ_CLEANER), "DIZ_CLEANER")
    pprint.pprint(DIZ_CLEANER)

    # TODO ADESSO PULIRE GLI UPVOTE E AZZERARE LE LISTE PER I COMMENTI!!!
    DA_RIMUOVERE = LISTA_GIFV[:] + LISTA_VIDEO[:] + LISTA_IMMAGINI[:] + DOPPIONI[:]
    print(len(DA_RIMUOVERE))
    #pausa = input("aspetto un tuo segnale per continuare...\n")
    del LISTA_IMMAGINI[:]
    del LISTA_VIDEO[:]
    del LISTA_GIFV[:]

    # Cerchiamo di pescare golosità nei commenti
    print("smistiamo i commenti!!!!")
    for commento in COMMENTI:
        try:
            smista_formato(SFIGATTO, commento=commento)
        except:
            print("ERRORE DI RECUPERO!!")
            COMM_IRR.append(commento)
            continue

    #pausa = input("PAUSA")

    file_old_comm = txt_upvote_passati(PATH_SLUT_COM)
    lista_old_comm = file_old_comm.readlines()

    for lista_commenti in LISTE:
        for elemento in lista_commenti[:]:
            # Se l'elemento è un doppione lo toglie dalla sua lista di appartenenza
            if check_doppione(elemento, lista_old_comm, file_old_comm):
                lista_commenti.remove(elemento)

    for immagine in LISTA_IMMAGINI:
        da_salvare(immagine, PATH_SLUT_COM)
    for video in LISTA_VIDEO:
        da_salvare(video, PATH_SLUT_COM)
    for gifvideo in LISTA_GIFV:
        down_gifv(gifvideo, cartella_file=PATH_SLUT_COM)
    rimozione = [LISTA_IMMAGINI, LISTA_VIDEO, LISTA_GIFV, DOPPIONI]

    print('RECAP2: COMMENTI')
    print(len(LISTA_IMMAGINI), 'immagini salvate')
    print(len(LISTA_VIDEO), 'video salvati')
    print(len(LISTA_GIFV), 'GIFV salvati')
    print(len(IRRISOLTI), 'irrisolti!!!')
    pprint.pprint(IRRISOLTI)
    print(len(DOPPIONI), "doppioni")
    print(len(DIZ_CLEANER), "DIZ_CLEANER")
    print(LISTE)
    print('commenti irrecuperabili\n', COMM_IRR)
    pprint.pprint(COMM_IRR)

    file_old_up.close()
    file_old_comm.close()
    db.close()

    for lista in (DA_RIMUOVERE):
        for post in DIZ_CLEANER:
            if DIZ_CLEANER[post] in lista:
                print("andiamo a rimuovere")
                remove_upvote(post)"""


def txt_upvote_passati(percorso):
    '''crea o legge, poi restituisce il file txt che conterrà/contiene
    l'url dei vecchi post upvotati'''
    # TODO: cerca la lista dei doppioni in PATH_SLUT. Se c'è l'apre e si prepara ad
    # controllare se i post dell'utente già ci sono e nel caso li salto (e toglie l'upvote)
    # aggiunge i post mancanti
    os.chdir(percorso)
    print('percorso per il txt', percorso)
    if not os.path.isfile(os.path.join(percorso, 'lista_upvote.txt')):
        modo = 'w+'
    else:
        modo = 'r+'
    #print('modo del listone: ', modo)
    lista = open('lista_upvote.txt', modo)
    return lista

def check_doppione(url, lista_passato, file_passato):
    print('\ncheck doppione: ', url)

    # Se l'url che sto controllando è già nella lista di upvote vecchi allora controllo se il file esiste effettivamente
    if url in lista_passato:
        nome = os.path.basename(url)

        immag = os.path.isfile(os.path.join(PATH_SLUT_IMG, nome))
        singola_immag = os.path.isfile(os.path.join(PATH_SLUT_IMG, nome + '.jpg'))
        vid = os.path.isfile(os.path.join(PATH_SLUT_VID, nome))
        gfy = os.path.isfile(os.path.join(PATH_SLUT_VID, nome + '.mp4'))
        gifv = os.path.isfile(os.path.join(PATH_SLUT_VID, nome[:-4] + 'mp4'))
        commento = os.path.isfile(os.path.join(PATH_SLUT_COM, nome))

        # controlla se il file esiste
        if commento:
            print("Commento già in lista. Saltato!")
            DOPPIONI.append(url)
            return True

        elif not (immag or vid or gfy or gifv or singola_immag):
            print('Url già presente in lista, ma file assente!')

            mess = 'vuoi salvare il file: ' + str(url) + '? S/N\n'
            opz = scelta(mess)
            if opz:
                return False
            elif not opz:
                DOPPIONI.append(url)
                return True

        # Poichè la cartella dei commenti è lì giusto per lo smistamento se l'url del file è presente nel txt, lo dò già per doppione.
        else:
            print(url + ' già presente, con relativo file. DOPPIONISSIMO!')
            DOPPIONI.append(url)
            return True

    # cerca nel prossimo rigo
    print(url + ' è nuovo! SLURP')
    file_passato.write(url + '\n')
    return False


def smista_formato(sfigatto, **kwargs):
    '''smista i post tra i vari formati e restituisce liste contenenti gli url finali da avviare al check_doppione
    il kwargs serve a far si che la funzione possa usare sia i post che gli url dei post (quando studi i commenti)'''
    #SI PUO REFACTORIARE! E Forse semplificare togliendo il **kwargs.

    print('\nsiamo in smista_formato')
    """print(kwargs)
    print(type(kwargs))
    input("ENTER per continuare")"""
    url = ''
    try:
        # Se hai un post da cui estrarre l'url
        for k in kwargs:
            pre_url = kwargs[k].url
            url = str(pre_url)
    except:  # va specificato l'except o si fanno errori sciocchi!!! basta che sia sbagliato un print nel try per finire nell'except aspecifico e perdersi l'errore!
        # Se hai un url direttamente
        for k in kwargs:
            pre_url = kwargs[k]
            url = str(pre_url)
    print(url)

    if url.startswith('https://www.reddit.com/r/') or url.startswith('https://np.reddit.com/r/'):
        try:
            parse_commenti2(url)
        # print(url)
        # pausa = input("fermo GUARDA!")
        except:
            print("SMISTA: Errore nel recuperare il link da reddit")

    if url.endswith('.jpg') or url.endswith('.png') or url.endswith('.gif'):
        print('abbiamo a che fare con una immagine!\n')
        formato(LISTA_IMMAGINI, url, kwargs, k)

    elif url.startswith('http://imgur.com/a/'):
        print('abbiamo a che fare con ALBUM IMGUR!\n')
        album_imgur(url, kwargs, k)

    elif url.startswith('http://imgur.com'):
        print('abbiamo a che fare con una immagine IMGUR!\n')
        url = 'https://i.imgur.com//' + os.path.basename(url) + '.jpg'
        formato(LISTA_IMMAGINI, url, kwargs, k)

    elif url.startswith('https://m.imgur.com'):
        res = requests.get(url)
        res.raise_for_status()
        soup = bs4.BeautifulSoup(res.text, "html.parser")
        m = soup.select("div img[src]")
        print(m)
        print(type(m))
        print(len(m))
        #pausa = input("IMGUR MMMMM")
        for num in range(len(m)):
            url = 'http:' + m[num]['src']
            print(url)
            #pausa = input("IMGUR MMMMM")
            if url.endswith('.jpg') or url.endswith('.png') or url.endswith('.gif'):
                formato(LISTA_IMMAGINI, url, kwargs, k)
                #pausa = input("IMGUR MIMG")
            if url.endswith('.gifv'):
                formato(LISTA_GIFV, url, kwargs, k)
                #pausa = input("IMGUR MGIFV")

    elif url.startswith('https://imgur.com'):
        print('HTTPS IMGUR!\n')
        url = decifra_imgur_https(url)
        print(url)
        if url.endswith('.jpg') or url.endswith('.png') or url.endswith('.gif'):
            formato(LISTA_IMMAGINI, url, kwargs, k)
        elif url.endswith('.mp4'):
            formato(LISTA_VIDEO, url, kwargs, k)

    elif url.endswith('.gifv'):
        print("siamo su imgur con una GIFV!")
        formato(LISTA_GIFV, url, kwargs, k)

    elif url.startswith('https://gfycat.com/') or url.startswith('https://giant.gfycat.com/') or url.startswith(
            'https://fat.gfycat.com/'):
        print("siamo su gfycat!\n")
        sfnome = os.path.basename(url)
        sfinfo = sfigatto.query_gfy(sfnome)
        # pprint.pprint (sfinfo)
        sfurl = sfinfo['gfyItem']['mp4Url']
        print(sfurl)
        formato(LISTA_VIDEO, sfurl, kwargs, k)
        """

    pattern = re.compile(r'.*?imgur.*')
    match = pattern.match(url)
    if match:
        siti.imagur(url)

    pattern = re.compile(r'.*?gfycat.*')
    match = pattern.match(url)
    if match:
        siti.gfycazz(url)"""




    else:
        print('***********ODDIO!!! dove siamo?!?********\n')
        IRRISOLTI.append(kwargs[k])

    return LISTA_IMMAGINI, LISTA_VIDEO, LISTA_GIFV, IRRISOLTI

def formato(lista, url, dizkw, kwk):
    lista.append(url)
    DIZ_CLEANER[dizkw[kwk]] = url

def album_imgur(url, dizkw, kwk):
    # TODO bisogna cercare se la pagina contiene il bottone per caricare più foto,
    # se si: caricare il file in modalità grid aggiungendo alla fine dell'url "/a/imageid/all" e scaricare tutte le foto
    #che non funziona, forse con ?grid
    #se no scarica l'album come è
    url += "?grid"
    print (url)
    #input("pausa")
    res = requests.get(url)
    res.raise_for_status()
    soup = bs4.BeautifulSoup(res.text, "html.parser")
    #album = soup.select("a img[src]")  # ("[class==post-image-container]")
    album = soup.select(".post-image")
    print(album)
    print(str(len(album)) + ' foto trovate nell album url: ' + url)
    #input("pausa")
    for num in range(len(album)):
        foto = 'http:' + album[num]['src']
        if foto.endswith('.jpg') or foto.endswith('.png') or foto.endswith('.gif'):
            print('foto dell album', foto)
            formato(LISTA_IMMAGINI, foto, dizkw, kwk)
        if foto.endswith('.gifv'):
            formato(LISTA_GIFV, foto, dizkw, kwk)

def decifra_imgur_https(url):
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

def down_gifv(url, cartella_file=PATH_SLUT_VID):
    # Questo vale solo per le gifv del sito IMGUR.COM
    try:
        res = requests.get(url)
        res.raise_for_status()
        soup = bs4.BeautifulSoup(res.text, "html.parser")
        elem = soup.select("body div source")
        ind = 'http:' + (elem[0]['src'])
        # print(elem[0]['src'])
        da_salvare(ind, cartella_file)
    except:
        print("c'è stato un problema con le gifv di imgur")





def prova_regex(lista):
    pattern = re.compile(r'(.*?imgur.*)|(.*?redd.*)|(.*?gfycat.*)') #(.*?png$|.*?jp(e)?g$)|((.*?imgur.*)|(.*?redd.*)|(.*?gfycat.*))')
                         #r'((http)(s)?(://))?(imgur.com).*')
    x = list()
    y= list()
    for url in lista:
        """if url.endswith('.jpg') or url.endswith('.png') or url.endswith('.gif'):
            print('abbiamo a che fare con una immagine!\n')
            # TODO
        print(url)"""
        x = pattern.findall(url)
        v = pattern.search(url)
        match = pattern.match(url)

        if match:
            x.append(match[0])
            print(url)
            print(pattern)
            print(x)
            print(v.groups())
            print(match)
            input("Input, pattern, findall, groups, e match")
            print()
        else:
            y.append(url)
        """try:
            print(x)
        except:
            print("non riesco a mostrarti i groups di: " + url)"""
    return x, y


class ImgurClient(object):
    def get_gallery_images(self, gallery_id):
        # LA STO SCRIVENDO IO JACOPO
        images = self.make_request('GET', 'gallery/%s/images' % gallery_id)
        return [Image(image) for image in images]