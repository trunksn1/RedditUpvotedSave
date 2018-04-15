# x = reddit.subreddit('redditdev')
# print(x)

# print(x.display_name)  # Output: redditdev
# print(x.title)         # Output: reddit Development
# print(x.description)   # Output: A subreddit for discussion of ...

# for i in range(len(lista)):
#	res = requests.get(lista[i])
#	res.raise_for_status()
#	imageFile = open(os.path.join('nsfw_img', os.path.basename(lista[i])) , 'wb')
#	for pezzo in res.iter_content(100000):
#		imageFile.write(pezzo)
#	imageFile.close()


#	soup = bs4.BeautifulSoup(res.text , "html.parser")
#	imag = soup.select('img src')
# try:
#	print(imag)
#	url = 'http:' + imag[0].get('src')
#	res = raise_for_status()
# except:
#	print('cazzi')
# pprint.pprint(lista_upvote)
# pprint.pprint(dir(upvote))
#		print(upvote.title)
#		print(upvote.subreddit)
#		print(upvote.thumbnail)
#		print(str(upvote.thumbnail_height) + '*' + str(upvote.thumbnail_width))
