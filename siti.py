#!/usr/bin/python 3.6
# -*- coding: utf-8 -*-
import re
import os, requests
from gfycat.client import GfycatClient
from imgurpython import ImgurClient
import config as cg

def gfycazz(client, url):
    #sfi = GfycatClient()

    #gif = "oldslipperybuckeyebutterfly"

    link_oggetto = client.query_gfy(url)['gfyItem']['mp4Url']
    print(link_oggetto)
    return link_oggetto
    """
    res = requests.get(x)
    file_salvato = open(os.path.basename(x), 'wb')
    for pezzo in res.iter_content(100000):
        file_salvato.write(pezzo)
    file_salvato.close()
    input()
    return 200"""

def imagur(client, url):
    """client_id = cg.imgur_client_id
    client_secret = cg.imgur_client_secret
    client = ImgurClient(client_id, client_secret)"""
    id = os.path.basename(url)
    print(os.getcwd())
    print(url)
    # Cerchiamo se l'url contiene un album
    pattern = re.compile(r'.*?/a/.*?')
    match = pattern.match(url)
    # Se è effettivamente un album, restituiamo una lista dei link di ogni singola immagine
    if match:
        lista_link_immagini = list()
        if url.endswith('?'): #non sò perchè ma ad alcuni post di reddit, il link per l'album termina con ? che sballa tutto
            url = url[:-1]
        print("album imgur")
        album_id = os.path.basename(url)
        print(album_id)
        album = client.get_album_images(album_id)
        for img in album:
            link_oggetto = requests.get(img.link)
            print(link_oggetto)

            lista_link_immagini.append(link_oggetto)
            """
            file_salvato = open(os.path.basename(img.link), 'wb')
            for pezzo in link_oggetto.iter_content(100000):
                file_salvato.write(pezzo)
            file_salvato.close()"""
            return lista_link_immagini
    else:
        print("immagine imgur")
        oggetto = client.get_image(id)
        link_oggetto = requests.get(oggetto.link)
        return link_oggetto

        """file_salvato = open(os.path.basename(oggetto.link), 'wb')
        for pezzo in link_oggetto.iter_content(100000):
            file_salvato.write(pezzo)
        file_salvato.close()"""


if __name__ == "__main__":
    #gfycazz()
    re.compile(r'imgur|reddit|gfycat')


    #imagur()
