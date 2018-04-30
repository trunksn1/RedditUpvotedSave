#!/usr/bin/python 3.6
# -*- coding: utf-8 -*-
import re
import os, requests
from gfycat.client import GfycatClient
from imgurpython import ImgurClient
import config as cg

def gfycazz(client, url):
    link_oggetto = client.query_gfy(url)['gfyItem']['mp4Url']
    print(link_oggetto)
    return link_oggetto


def imagur(client, url):

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
        print("ID dell'album: ", album_id)
        album = client.get_album_images(album_id)
        for img in album:
            link_oggetto = img.link
            print(link_oggetto)
            lista_link_immagini.append(link_oggetto)
        return lista_link_immagini
    else:
        print("immagine imgur")
        oggetto = client.get_image(id)
        link_oggetto = requests.get(oggetto.link)
        return link_oggetto