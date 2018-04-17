#!/usr/bin/python 3.6
# -*- coding: utf-8 -*-

import os, requests
from gfycat.client import GfycatClient
from imgurpython import ImgurClient

def gfycazz():
    print(os.getcwd())
    input()
    sfi = GfycatClient()

    gif = "oldslipperybuckeyebutterfly"

    x = sfi.query_gfy(gif)['gfyItem']['mp4Url']
    print(x)
    res = requests.get(x)
    file_salvato = open(os.path.basename(x), 'wb')
    for pezzo in res.iter_content(100000):
        file_salvato.write(pezzo)
    file_salvato.close()
    return 200

def imagur():
    #TODO: Come nascondere queste che sono info sensibili?
    client_id = '4c1fda5cda15b81'
    client_secret = 'a4733cf4766bc9adf014563439400a40bc880c5f'

    client = ImgurClient(client_id, client_secret)

    album = "https://imgur.com/a/psDgs"
    album_id = os.path.basename(album)
    print(album_id)
    y = client.get_album_images(album_id)
    for img in y:
        x = img.link
        res = requests.get(x)
        file_salvato = open(os.path.basename(x), 'wb')
        for pezzo in res.iter_content(100000):
            file_salvato.write(pezzo)
        file_salvato.close()

    """items = client.gallery()
    for item in items:
        print(item.link)"""


if __name__ == "__main__":
    #gfycazz()
    imagur()
