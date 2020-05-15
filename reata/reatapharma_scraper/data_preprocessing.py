import requests, pandas as pd, numpy as np, urllib, sys, warnings, string
from matplotlib import pyplot as plt
from collections import Counter
from bs4 import BeautifulSoup as BS
from postmen import Postmen, PostmenException
from random import choice
warnings.filterwarnings(action='ignore', category=UserWarning, module='gensim')
from gensim.parsing.preprocessing import preprocess_string



TOKEN_LEN = 32 #Static magic number

#generate the postman headers randomly...
def spawn_postman_header():
	strTok = ''.join([choice(string.hexdigits).lower() for _ in range(TOKEN_LEN)])
	strTok="{}-{}-{}-{}-{}".format(strTok[:8],strTok[8:12],
		strTok[12:16],strTok[16:20],strTok[20:])
	headers = {'Accept': '*/*' , 'accept-encoding' : ('gzip','deflate') , 
		'Content-Type': "application/json",'cache-control':"no-cache",
		'Postman-Token': '35df8e6e-8049-4f94-8940-71f11ee2faad',
		'cookie' : 'PHPSESSID=a3aa6db0c28eb8f38fd7205b6feb2aac',
		'Host':'reatapharma.com','User-Agent' : 'PostmanRuntime/7.2.0' }
	return headers

#returns Counter object with words arranged by frequency...
def url_word_counter(url):
	rev = requests.get(url, headers=spawn_postman_header())
	soup = BS(rev.text,'lxml') #turn text html output into beautifulsoup object
	cntr = Counter()
	for p_txt in soup.find_all('p'):
		tmp_cntr = Counter(preprocess_string(p_txt.get_text()))
		cntr+=tmp_cntr
	return cntr

# scrape the words from each of the hyperlinks, and pop into Counter
def scrape_words(links_pd):
	vis_set,agg_counter,domain = set(),Counter(),'reatapharma.com'
	for index,row in links_pd.iterrows():
		if(index%100==0): print(index)
		url_from,url_to = row['url_from'],row['url_to']
		if((url_from not in vis_set) and (domain in url_from)):
			frm_cntr = url_word_counter(url_from)
			agg_counter+=frm_cntr
			vis_set.add(url_from)
		if((url_to not in vis_set) and (domain in url_to)):
			to_cntr = url_word_counter(url_to)
			agg_counter+=to_cntr
			vis_set.add(url_to)
	return agg_counter


#plots most common words w.r.t. their relative frequencies
def plot_and_txt(agg_counter,total,n=20):
	most_common = agg_counter.most_common(n)
	words,freqs = zip(*most_common)
	words = np.asarray(words)
	freqs = np.true_divide(np.asarray(freqs),total)
	plt.bar(words, freqs)
	plt.xlabel('most common words'),plt.ylabel('relative frequencies of words')
	plt.title('Most Common Words vs. Relative Frequency')
	plt.rcParams['figure.figsize'] = [12,9]
	plt.savefig('reata=most_freq_words_vs_rel_freqs.png')
	freq_obj = open('reata=most_freq_words_vs_rel_freqs.txt','w')
	freq_obj.write('Top words: relative frequencies\n')
	assert(len(words)==len(freqs))
	for (index,word) in enumerate(words):
		freq=freqs[index]
		freq_obj.write('\t{}: {}\n'.format(word,freq))
	freq_obj.close()
	return

# create main shell that loops through all sublinks.. 
def main_shell():
	links_pd = pd.read_csv('links.csv')
	#scrape words and aggregate counter...
	agg_counter = scrape_words(links_pd)
	print(agg_counter)
	total = sum(list(dict(agg_counter).values()))
	plot_and_txt(agg_counter,total)
	return


#calls the main shell, which calls all the other subsidiary functions...
main_shell()




