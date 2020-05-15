import argparse,requests,os,sys,pprint,re,nltk,string
import pandas as pd, sklearn as skt, matplotlib.pyplot as plt
from bs4 import BeautifulSoup
from nltk.stem import WordNetLemmatizer,PorterStemmer
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from statistics import mean,median,mode,stdev
from collections import Counter
import warnings
warnings.filterwarnings(action='ignore', category=UserWarning, module='gensim')
from gensim.parsing.preprocessing import preprocess_string


pp = pprint.PrettyPrinter()
sia = SentimentIntensityAnalyzer()

##function that parses command line argument and returns a dictionary containing those args
def arg_parser():
	parser = argparse.ArgumentParser()
	parser.add_argument('--term', help='''Search term (e.g. "food", "restaurants"). 
		If term isn't included we search everything. The term keyword also accepts 
		business names such as "Starbucks" and defaults to "restaurants".''',
		default='starbucks')
	parser.add_argument('--location', help='''Specifies the combination of "address,
		neighborhood, city, state or zip, optional country" to be used 
		when searching for businesses, and defaults to "Seattle".''', default="seattle")
	parser.add_argument('--plot',help='''output plot or not?[True/False]''',
		choices=['True', 'False'], default='True')
	parser.add_argument('--stats',help='''output stats or not?[True/False]''',
		choices=['True','False'], default='True')
	parser.add_argument('--csv',help='''output external csv file?[True/False]''',
		choices=['True','False'], default='True')
	args = parser.parse_args()
	print('arguments: %s'%vars(args))
	return vars(args)

##GIVEN Unique API_KEY and command line arguments, return JSON payload w/ URLs
def churn_unique_JSON(arg_dict, offset, API_KEY):
	term_str, loc_str = arg_dict['term'], arg_dict['location']
	headers = {'Authorization' : "Bearer "+API_KEY, 'content-type': "application/json"}
	url = "https://api.yelp.com/v3/businesses/search?term={}&location={}".format(term_str,loc_str)
	req = requests.get(url, headers=headers)
	if(req.status_code!=200):
		print("URL requested is not parsing - returning None")
		return 
	return req.json()

#return a random business HTML page given search parameters
	#will use beautifulSoup to churn out relevant reviews
def find_api_reviews(api_data, offset):
	rand_url_stem = api_data['businesses'][0]['url']
	rand_url_stem = rand_url_stem[:rand_url_stem.index('?')] #cut off everything after '?'
	rand_url = rand_url_stem+'?start={}'.format(offset) #add the '?start' offset...

	addr = api_data['businesses'][0]['location']['display_address'][0]
	city = api_data['businesses'][0]['location']['city']
	zipcode = api_data['businesses'][0]['location']['zip_code']
	print('rand_url: %s'%rand_url)
	rev = requests.get(rand_url)
	return rev.text,addr,city,zipcode

####################################################################################
 # PUT USERNAME,RATING,REVIEW,SENTIMENT,TOPIC INTO ONE DF (5 COLS)
####################################################################################

##clean & lowercase text - perform sentient analysis
def perform_sentient_analysis(raw_text):
	ss_temp = sia.polarity_scores(raw_text)
	return float(ss_temp['compound'])

#determine topic of text given text...
def determine_topic(text):
	text_list = preprocess_string(text)
	freq_dict = Counter(text_list)
	return freq_dict.most_common(1)[0][0]

##Returns populated dictionary delineating 4 columns of inforation (to be turned to dict)
def pop_pddict(api_random_html):
	pd_ratings = dict() #load into dictionary - convert to dataframe
	pd_ratings['username'],pd_ratings['ratings'] = [],[]
	pd_ratings['text'],pd_ratings['sentScore'],pd_ratings['topic'] = [],[],[] 
	soup = BeautifulSoup(api_random_html, 'html.parser')
	reviews = soup.find_all('div', 'review review--with-sidebar')
	for review in reviews:
		pd_ratings['username'].append(review.find('a', id='dropdown_user-name').get_text())
		pd_ratings['text'].append(review.find('p', lang='en').get_text()
			.encode('utf-8').replace('\xc2\xa0','')) #find text and root out garbage bytes...
		pd_ratings['sentScore'].append(perform_sentient_analysis(pd_ratings['text'][-1]))
		raw_rat_tag = review.find('div', title=re.compile('\w star rating'))
		pd_ratings['ratings'].append(re.findall('\d',raw_rat_tag['title'])[0])
		pd_ratings['topic'].append(determine_topic(pd_ratings['text'][-1]))
	return pd_ratings

#######################################################################################
 # PUT 5 columns delineated above into a dictionary 
#######################################################################################



####################### MAIN REVIEW RUN LOOP ##########################################
#######################################################################################

##RUN through all the reviews for particular place - stop at 1000
def run_review_loop(f_API_KEY,arg_dict,limit):
	offset = 0
	cum_yelp_dict = {'username':[], 'text':[], 'sentScore':[], 'ratings':[], 'topic':[]} 
	api_data,api_random_html = churn_unique_JSON(arg_dict, offset, f_API_KEY.read()),-1
	rev_count = int(api_data['businesses'][0]['review_count'])
	while(offset<=limit and offset<=rev_count): #we'll stop at a limit or num_reviews
		api_random_html,addr,city,zipcode = find_api_reviews(api_data, offset)
		yelp_dict = pop_pddict(api_random_html)
		for y_key in cum_yelp_dict:
			cum_yelp_dict[y_key].extend(yelp_dict[y_key])
		offset+=20
	return cum_yelp_dict,addr,city,zipcode

######################## MAIN REVIEW RUN LOOP ##########################################
########################################################################################

#load data from python dictionary to pandas dataframe...
def load_from_dict(cum_yelp_dict,addr,city,zipcode,csvbool):
	pd_df = pd.DataFrame(data=cum_yelp_dict)
	pd_df.head()
	csv_name = 'yelp_data_addr={}_city={}_zip={}.csv'.format(addr,city,zipcode)
	if(csvbool): pd_df.to_csv(csv_name)
	return pd_df

#scribe statistics about the ratings and sentiment score
	# generate scatter plot of sentiment score vs. rating & heat map correlation 
def run_plots(pd_df_yelp,addr,city,zipcode):
	rel_rats, sentScores = pd_df_yelp['ratings'], pd_df_yelp['sentScore']
	plt.scatter(rel_rats.values, sentScores.values)
	plt.xlabel('1-5 user inputted rating'),plt.ylabel('NLP compounded sentiment score')
	plt.title('Scatterplot User Rating vs. Sentiment Score')
	plt.savefig('rat_vs_sentScore_addr={}_city={}_zip={}.png'.format(addr,city,zipcode))
	return

##will output statistics relating to the pandas dataframe ratings
def run_stats(pd_df_yelp,addr,city,zipcode):
	rat_list= pd_df_yelp['ratings'].values.astype(float) #cast array to float
	sent_list = pd_df_yelp['sentScore'].values.astype(float) #cast array to float
	f_name = 'stats_addr={}_city={}_zip={}.txt'.format(addr,city,zipcode)

	f_obj = open(f_name, 'w') #open the actual file (file object datatype)
	f_obj.write('statistics for ratings in given location:\n')
	f_obj.write('\tmedian rating: {}\n'.format(median(rat_list)))
	f_obj.write('\tmean rating: {}\n'.format(mean(rat_list)))
	try: f_obj.write('\tmode rating: {}\n'.format(mode(rat_list)))
	except: f_obj.write('\tmode rating: no unique mode\n')
	f_obj.write('\tstandard deviation rating: {}\n\n'.format(stdev(rat_list)))

	f_obj.write('statistics for sentiment score in given location:\n')
	f_obj.write('\tmedian sentiment score: {}\n'.format(median(sent_list)))
	f_obj.write('\tmean sentiment score: {}\n'.format(mean(sent_list)))
	f_obj.write('\tstandard deviation sentiment score: {}'.format(stdev(sent_list)))
	f_obj.close()
	return

##MAIN FUNCTION THAT CALL ALL THE ABOVE FUNCTIONS!
def main_shell(limit=1000,term=None,location=None,plot='True',stats='True',csv='True'):
	if(term==None or location==None): arg_dict = arg_parser()	
	else: arg_dict = {'term':term,'location':location,'plot':plot,'stats':stats,'csv':csv}
	try: f_API_KEY = open('yelp_API_key.txt', 'r')
	except: 
		print('input valid Yelp API_Key in file named exactly "yelp_API_key.txt" in the same folder as Python script')
		return
	cum_yelp_dict,addr,city,zipcode = run_review_loop(f_API_KEY, arg_dict, limit)
	f_API_KEY.close()
	pd_df_yelp = load_from_dict(cum_yelp_dict,addr,city,zipcode,eval(arg_dict['csv']))
	if(eval(arg_dict['plot'])): run_plots(pd_df_yelp,addr,city,zipcode)
	if(eval(arg_dict['stats'])): run_stats(pd_df_yelp,addr,city,zipcode)
	return pd_df_yelp #main_shell also returns 5 column pandas dataframe

if __name__=='__main__':
	main_shell() #when called from CMD, we don't store any pandas dataframe, but output it to CSV...

