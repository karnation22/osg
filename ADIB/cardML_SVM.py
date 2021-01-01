import numpy as np  
import pandas as pd 
import matplotlib.pyplot as plt
import csv, time
from sklearn import svm
from sklearn.feature_extraction.text import TfidfVectorizer


#inputs csv file - outputs train/test dataframes as well as column index for revolver flag
def read_files_train_test_PD(csv_card):
    dataCard = open(csv_card, 'r')
    dataFrame = list(csv.reader(dataCard))
    ##FLAG THE INDEX COLUMN OF THE REVLFLAG(DATA WE ARE TRYING TO DETERMINE...)
    REV_FLAG_INDEX = dataFrame[0].index('RevlFlag')
    ###DELETE INCOMPLETE DATA - NOT AN IDEAL WAY TO DEAL WITH SITUATION (~60% of data was lost)###
    pdDataFrame = pd.DataFrame(dataFrame)[1:].drop(columns=[0,1,2,3]).replace(r"", np.nan).dropna()
    return (pdDataFrame, REV_FLAG_INDEX)

def partition_data(pdDataFrame, train_part=0.8):
    ##Partition data 80/20 with train/test respective##
    trainPD = pdDataFrame[:int(train_part*len(pdDataFrame))+1]
    testPD = pdDataFrame[int(train_part*len(pdDataFrame)):]
    return(trainPD, testPD)

#turn all string data into TFIDF float data
# leave all numericals as floats, but cast string floats into real flaots...
def numerisize_data(param_train):
    # numerical columns - cast series to floats...
    n_types = [4,13,14,15,16,17,18,19,20,22,23,27,28,29,30,31,32,33,36]
    #categorical columns - convert to numerical TFIDFs an cast to floats
    c_types = [5,6,7,8,9,10,11,12,21,24,25,34,35,37,38,39,40]
    #DETERMINE HOW TO DEAL WITH EMPTY CELLS...
    for col in param_train:
	if(col in c_types):
	   #no lowercase and want to match (any) word
	   tfidf = TfidfVectorizer(lowercase=False, token_pattern=r"(?u)\S+")
	   #replace " " with "_", decode, and get rid of 'b[w]' 
           param_train_col = list(map(lambda word: word.replace(" ","_").decode(), list(param_train[col])))
           tfidf.fit_transform(param_train_col)
	   #dictionary zip up the feature names with the respective idf value...
           dict_tfidf = dict(zip(tfidf.get_feature_names(), tfidf.idf_))
	   #map the word onto its TFIDF float value
	   param_train_col = list(map(lambda word: float(dict_tfidf[word]), param_train_col))
	   param_train[col] = param_train_col
	   pd.to_numeric(param_train[col], downcast='float')
	elif(col in n_types): param_train[col] = pd.to_numeric(param_train[col], downcast='float')
    return param_train
		


#take training data, and build an SVM classifier (return SVM classifier object...)
def build_SVM_Classifier(train, REV_FLAG_INDEX, penalty='l2'):
    rev_flag_train = np.asarray(pd.to_numeric(train.loc[:, REV_FLAG_INDEX], downcast='float'))
    #remove the revl_flag column for the param_train (x-axis) data...
    param_train = train.drop(REV_FLAG_INDEX, axis=1)
    param_train = np.asarray(numerisize_data(param_train))
    print("Done modifying param_train")
    clf_svc = svm.LinearSVC(penalty=penalty)
    clf_svc.fit(param_train, rev_flag_train)
    print("The training score on SVC is %f"%clf_svc.score(param_train, rev_flag_train))
    return clf_svc #return the actual LinearSVC classifier...

def test_SVM_classifier(test, REV_FLAG_INDEX, clf_svc):
    rev_flag_test = np.asarray(pd.to_numeric(test.loc[:, REV_FLAG_INDEX], downcast='float'))
    param_test = test.drop(REV_FLAG_INDEX, axis=1)
    param_test = np.asarray(numerisize_data(param_test))
    score = clf_svc.score(param_test, rev_flag_test)
    return score ##SCORE THE ABOVE CLASSIFIER###

#function that tests score accuracy with train/test partition...
def plot_wrapper_call(csv_card):
    (pdDataFrame, REV_INDEX) = read_files_train_test_PD(csv_card)
    #percent of data that goes to training data...
    train_partitions = [0.7, 0.75, 0.8, 0.85, 0.9]
    score_for_partitions = list()
    for train_part in train_partitions:
	(train, test) = partition_data(pdDataFrame, train_part)
	print("Done with read files")
	clf_svc = build_SVM_Classifier(train, REV_INDEX)
	print("Done building the classifier")
	score = test_SVM_classifier(test, REV_INDEX, clf_svc)
	print("The final test score is... %f\n"%score)
	score_for_partitions.append(score)
	plt.plot(train_partitions, score_for_partitions, 'ro')
	plt.xlabel("training data partition percentage")
	plt.ylabel("score for given training data percentage")
	plt.title("Training partition vs. LinearSVC score")
	plt.show()
   return

#main wrapper function for everything above...
def main_wrapper_call(csv_card):
    (pdDataFrame, REV_INDEX) = read_files_train_test_PD(csv_card)
    print("Done reading files into pandas dataFrame")
    (train, test) = partition_data(pdDataFrame)
    print("Done partitioning the data")
    clf_svc = build_SVM_Classifier(train, REV_INDEX)
    print("Done building the SVM classifier")
    score = test_SVM_classifier(test, REV_INDEX, clf_svc)
    print("The final test score is %f"%score)
    return

main_wrapper_call('card201701.csv')
