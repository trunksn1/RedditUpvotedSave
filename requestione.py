import os, pprint, re, requests

elem = ['https://i.redd.it/kfc02ub2amb01.jpg', 'https://i.imgur.com/tBdWHri.jpg']

for url in elem:
    print('ciao')
    res = requests.get(url)
    print(res.status_code)
    res.raise_for_status()
    print(url)

    path = open(os.path.join('C:\\Users\\Jacopo-Sk\\Desktop', os.path.basename(url)), 'wb')

    for pezzo in res.iter_content(100000):
        path.write(pezzo)
    path.close()