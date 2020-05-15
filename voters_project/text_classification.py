import numpy as np,pandas as pd,os,re,io,sys
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_selection import chi2
from sklearn.naive_bayes import MultinomialNB as MNB
from sklearn.linear_model import LogisticRegression as LR
from sklearn.ensemble import RandomForestClassifier as RFC
from sklearn.svm import LinearSVC as LSVC


models = [LSVC(), MNB(), LR(), RFC()]
modelNames = ['Linear SVC', 'MultinomialNB','LogisticRegression','RandomForestClassifier']
stats_name = 'stats_ML_models.txt'
########################## TRAIN AND TEST ON MODELS ###########################  
###############################################################################
def perform_train_test(pd_df,dataName,f_obj,X,y):
	pd_df['cat_id']=pd.Series(pd_df[y].factorize()[0]).astype(int)
	id_label_map = dict(pd_df[['cat_id',y]].drop_duplicates().sort_values('cat_id').values)
	f_obj.write('Stats for dataset {}:\n'.format(dataName))
	for (index,model) in enumerate(models):
		X_train,X_test,y_train,y_test=train_test_split(pd_df[X],pd_df['cat_id'],test_size=0.2,random_state=0)
		X_train_obj=TfidfVectorizer().fit(X_train) #returns TFIDF object FITTED TO TRAINING PARTITION
		X_train_tfidf=X_train_obj.transform(X_train)
		clf = model.fit(X_train_tfidf,y_train)
		X_test_tfidf=X_train_obj.transform(X_test)
		accuracy=clf.score(X_test_tfidf,y_test)
		pred_lab = [id_label_map[int(id_index)] for id_index in clf.predict(X_test_tfidf)]
		pred_df = pd.DataFrame(data={'Review Test':X_test, 'Label Test':pred_lab},columns=['Review Test','Label Test'])
		pred_df.to_csv('pred_{}_for{}.csv'.format(dataName,modelNames[index]))
		f_obj.write('\tAccuracy of model {} with data {}: {}\n'.format(modelNames[index],dataName,accuracy))
	f_obj.write('\n')
	return 

###############################################################################
###############################################################################


## main shell that loads all CSV files into pandas dataframes ##
def main_shell():
	BS_Oil_NRet = pd.read_csv('BS_Oil_Non_Return_27June2017.csv',error_bad_lines=False,names=['Review','Label']).reset_index()
	BS_Oil_Ret = pd.read_csv('BS_Oil_Return_27June2017.csv',error_bad_lines=False,names=['Review','Label']).reset_index()
	BS_RM_NRet = pd.read_csv('BS_RM_Non_Return_27June2017.csv',error_bad_lines=False,names=['Review','Label']).reset_index()
	Core_Oil_NRet = pd.read_csv('Core_Oil_Non_Return_27June2017.csv',error_bad_lines=False,names=['Review','Label']).reset_index()
	Core_Oil_Ret = pd.read_csv('Core_Oil_Return_27June2017.csv',error_bad_lines=False,names=['Review','Label']).reset_index()
	Core_RM_NRet = pd.read_csv('Core_RM_Non_Return_27June2017.csv',error_bad_lines=False,names=['Review','Label']).reset_index()
	## TRAIN A CLASSIFIER FOR EACH UNIQUE Pandas Dataframe ##
	f_obj=open(stats_name,'w')
	perform_train_test(BS_Oil_NRet, 'BS_Oil_NRet',f_obj,'Review','Label')
	print('done1')
	perform_train_test(BS_Oil_Ret, 'BS_Oil_Ret',f_obj,'index','Review')
	print('done2')
	perform_train_test(BS_RM_NRet,'BS_RM_NRet',f_obj,'index','Review')
	print('done3')
	perform_train_test(Core_Oil_NRet,'Core_Oil_NRet',f_obj,'Review','Label')
	print('done4')
	perform_train_test(Core_Oil_Ret, 'Core_Oil_Ret',f_obj,'Review','Label')
	print('done5b')
	perform_train_test(Core_RM_NRet, 'Core_RM_NRet',f_obj,'index','Review')
	f_obj.close()
	return

main_shell()

