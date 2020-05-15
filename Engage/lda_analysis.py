import warnings
warnings.filterwarnings(action='ignore', category=UserWarning, module='gensim')
import gensim,graphlab as gl,pandas as pd,numpy as np,lda,sys,pyLDAvis
from yelp_api import *
from sklearn.decomposition import NMF, LatentDirichletAllocation as skLDA
from sklearn.feature_extraction import DictVectorizer
from collections import Counter
from gensim.test.utils import common_texts
from gensim.models import LdaModel
from gensim.corpora.dictionary import Dictionary
from gensim.parsing.preprocessing import preprocess_string

##argument parser when run from cmd - defaults to 'term=starbucks' and 'location=seattle'
def arg_parser():
	parser = argparse.ArgumentParser()
	parser.add_argument('--term', help='''Search term (e.g. "food", "restaurants"). 
		If term isn't included we search everything. The term keyword also accepts 
		business names such as "Starbucks" and defaults to "restaurants".''',
		default='starbucks')
	parser.add_argument('--location', help='''Specifies the combination of "address,
		neighborhood, city, state or zip, optional country" to be used 
		when searching for businesses, and defaults to "Seattle".''', default="seattle")
	parser.add_argument('--plot',help='''output plot or not? [True/False]''',
		choices=['True','False'], default='True')
	parser.add_argument('--stats',help='''output stats or not?[True/False]''',
		choices=['True','False'], default='True')
	parser.add_argument('--csv',help='''output external csv file?[True/False]''',
		choices=['True','False'], default='True')
	args = vars(parser.parse_args())
	print('arguments: %s'%args)
	return args['term'],args['location'],args['plot'],args['stats'],args['csv']

#gensim implementation
def gensim_lda(pd_df_yelp, text_rev): #gensim lda
	common_dict = Dictionary(text_rev)
	common_corpus = [common_dict.doc2bow(text) for text in text_rev]
	lda = LdaModel(common_corpus)
	topics = [lda.get_document_topics(doc) for doc in common_corpus]
	topicIDs = [topic[0][0] for topic in topics]
	topic_prob_list = [lda.show_topic(topicID) for topicID in topicIDs]
	topic_prob_list_split = [zip(*item) for item in topic_prob_list]
	topic_prob_list_words = [list(map(lambda topID: dict(common_dict)[int(topID)],item[0]))\
		for item in topic_prob_list_split]
	topic_prob_list_prob = list(map(lambda item: list(item[1]), topic_prob_list_split))
	return (topic_prob_list_words,topic_prob_list_prob)


#graphlab implementation
def graphlab_lda(pd_df_yelp, text_rev): #graphlab lda
	bow_text_rev = [dict(Counter(doc)) for doc in text_rev]
	bow_gl_text_rev = gl.SArray(bow_text_rev)
	gl_lda = gl.topic_model.create(bow_gl_text_rev)
	return gl_lda.get_topics().to_numpy()
	
#sklearn implementation
def sklearn_lda(pd_df_yelp, text_rev): #scikit-learn lda
	text_rev_bow = [dict(Counter(doc)) for doc in text_rev]
	text_v = DictVectorizer(sparse=False)
	text_X = text_v.fit_transform(text_rev_bow)
	skLDA_fit = skLDA().fit_transform(text_X)
	return skLDA_fit,-1

#python lda implementation
def lda_lda(pd_df_yelp,text_rev): #standard lda package
	flat_text_rev = [word for text in text_rev for word in text]
	dict_v = DictVectorizer(sparse=False)
	#little bit of sklearn in preprocessing
	bow_array = dict_v.fit_transform([dict(Counter(text)) for text in text_rev]).astype(int)
	pyLDA = lda.LDA(n_topics=10)
	X_array = pyLDA.fit_transform(bow_array)
	return(X_array, pyLDA.nz_) #determine how to find topic words...

#here is the main lda shell
def main_lda_shell():
	term,location,plot,stats,csv= arg_parser()
	preprocsplit = (lambda rev: np.asarray(preprocess_string(rev)))
	pd_df_yelp = main_shell(1000,term,location,plot,stats,csv) #run yelp_api.py - limit to 1000 reviews MAX
	text_rev = pd_df_yelp['text'].apply(preprocsplit).values #preprocess text and numpy array up code...

	###gensim lda, graphlab lda, sklearn lda, builtin lda (in that order)
	(gensim_topic_prob_list_words, gensim_topic_prob_list_prob) = gensim_lda(pd_df_yelp, text_rev) #apply lda of gensim...

	gra_lda_topics = graphlab_lda(pd_df_yelp, text_rev) #(BEST ONE)!
	skLDA_fit,_ = sklearn_lda(pd_df_yelp,text_rev) #determine how to find actual words associated w/ topics
	(X_array,indices) = lda_lda(pd_df_yelp, text_rev)
	
	return

main_lda_shell()