#!/usr/bin/python 3.6
# -*- coding: utf-8 -*-
import re
import os, requests
from gfycat.client import GfycatClient
from imgurpython import ImgurClient
import config as cg

def gfycazz(client, url):
    link_oggetto = client.query_gfy(os.path.basename(url))['gfyItem']['mp4Url']
    return link_oggetto


def imagur(client, url):

    id = os.path.basename(url)
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

        # TODO: i link degli album possono avere degli # che indirizzano per specifiche immagini dell'album sputtanando tutto: https://imgur.com/a/PAwPd#anhSYOW
        try:
            album = client.get_album_images(album_id)
        except TypeError:
            print("il link è una merda, va tolto il #")
            return 404
        for img in album:
            link_oggetto = img.link
            print(link_oggetto)
            lista_link_immagini.append(link_oggetto)
        return lista_link_immagini
    else:
        print("immagine imgur")
        try:
            oggetto = client.get_image(id)
        except:
            print("Problema ad ottenere il get_image(id)")
            return 404
        else:
            link_oggetto = oggetto.link
            return link_oggetto

if __name__ == "__main__":
    IMGUR = ImgurClient(cg.imgur_client_id, cg.imgur_client_secret)
    imagur(IMGUR, 'http://imgur.com/gallery/WMzTb0t')