import pandas as pd, numpy as np, savReaderWriter as spss, sys, os, re, warnings
warnings.simplefilter('ignore')
from sklearn.svm import LinearSVC as LSVC
from sklearn.naive_bayes import MultinomialNB as MNB
from sklearn.linear_model import LogisticRegression as LR
from sklearn.neural_network import MLPClassifier as MLPC
from sklearn.model_selection import train_test_split as tts

##train an SVC model for the data...
def learnData(xData,yData,f_obj,MLtype):
	f_obj.write('Accuracy for {}:\n'.format(MLtype))
	for test in [0.10,0.15,0.20,0.25]:
		xData_train,xData_test,yData_train,yData_test = tts(xData,yData,test_size=test,random_state=42)
		if(MLtype=='LSVC'):	clf = LSVC()
		if(MLtype=='LR'): clf = LR()
		if(MLtype=='MNB'): clf = MNB()
		else: clf = MLPC()
		clf.fit(xData_train,yData_train)
		score = clf.score(xData_test,yData_test)
		f_obj.write('\ttest partition {} yields {} accuracy\n'.format(test,score))
	f_obj.write('\n')

# preprocess the xData [categorical/ordinal --> dummy] [numerical -->normalized]
def preprocess_data(input_xData):
	xData_pre = []
	for index,column in enumerate(input_xData):
		series = input_xData[column]
		if(0<=index and index<=6 and not(index==4)):
			seriesONC = pd.get_dummies(series,prefix=series.name).astype(float)
			xData_pre.append(seriesONC)
		else:
			seriesNORM = ((series-series.min()) / (series.max()-series.min()))
			xData_pre.append(seriesNORM)
	xData = pd.concat(objs=xData_pre,axis=1)
	print(xData.head(10))
	return xData

#main shell that runs the rest of the code
def main_function():
	rawData = list(spss.SavReader('RevisedDataFile.sav', returnHeader=True))
	pdData = pd.DataFrame(data=rawData[1:],columns=rawData[0]).dropna()
	sq10 = list(pdData.filter(regex='sq10.*'))
	xData_pre = pdData.drop(labels=['K6b','respid','sq08x1_1','sq08x1_2'],axis=1)
	yData = pdData.filter(regex='K6b')
	xData = preprocess_data(xData_pre)
	xData.to_csv('xData.csv'),yData.to_csv('yData.csv')
	assert(len(xData)==len(yData)) #must be true for any ML model to work
	f_obj = open('cornelius_data.txt','w')
	for MLtype in ['LSVC','MNB', 'LR','MLPC']:
		learnData(xData,yData,f_obj,MLtype)
	f_obj.close()

## CALL the main_function(), which calls everything else...
main_function()