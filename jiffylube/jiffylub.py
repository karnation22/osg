import pandas as pd, numpy as np, warnings,nltk,matplotlib.pyplot as plt 
warnings.filterwarnings(action='ignore', category=UserWarning, module='gensim')
from gensim.models import LdaModel
from gensim.corpora.dictionary import Dictionary
from gensim.parsing.preprocessing import preprocess_string
from nltk.sentiment.vader import SentimentIntensityAnalyzer as SIA

#for each dataframe, output the misclassified data...
def output_csv_files(output_dfs, output_df_strs):
	assert(len(output_dfs)==len(output_df_strs))
	sia = SIA()
	for index in range(len(output_dfs)):
		preprocsplit = (lambda rev: preprocess_string(str(rev)))
		output_df,stem_name = output_dfs[index],output_df_strs[index]
		output_df[2] = (output_df[1].astype(str).apply(preprocsplit))
		new_output_df = pd.DataFrame() #new output dataframe...
		for (_,row) in output_df.iterrows():
			if(('unprofession' in list(row[2]) or 'profession' in list(row[2]))): 
				new_output_df = new_output_df.append(row,ignore_index=True)
		misclassified_df = pd.DataFrame()
		for (_,row) in new_output_df.iterrows():
			if(('unprofession' in list(row[2]) and 
				sia.polarity_scores(row[0])['compound']>0.0) or ('profession' in 
				list(row[2]) and sia.polarity_scores(row[0])['compound']<0.0)): 
				misclassified_df = misclassified_df.append(row,ignore_index=True)
		f_name = 'misclassified_'+stem_name+'.csv'
		print(type(misclassified_df))
		print(f_name)
		misclassified_df.to_csv(f_name)
	return

#Main shell that accrues all of the dataframes from the .csv files
def main_shell():
	BS_Oil_Non_Return_27June2017=pd.read_csv('BS_Oil_Non_Return_27June2017.csv',header=None,error_bad_lines=False)
	BS_Oil_Non_Return_27June2017=BS_Oil_Non_Return_27June2017[[0,1]] #just first two columns
	BS_Oil_Return_27June2017=pd.read_csv('BS_Oil_Return_27June2017.csv',header=None,error_bad_lines=False)
	BS_Oil_Return_27June2017=BS_Oil_Return_27June2017[[0,1]] #just first two columns
	BS_RM_Non_Return_27June2017=pd.read_csv('BS_RM_Non_Return_27June2017.csv',header=None,error_bad_lines=False)
	BS_RM_Non_Return_27June2017=BS_RM_Non_Return_27June2017[[0,1]] #just first two columns
	Core_Oil_Non_Return_27June2017=pd.read_csv('Core_Oil_Non_Return_27June2017.csv',header=None,error_bad_lines=False)
	Core_Oil_Non_Return_27June2017=Core_Oil_Non_Return_27June2017[[0,1]] #just first two columns
	Core_Oil_Return_27June2017=pd.read_csv('Core_Oil_Return_27June2017.csv',header=None,error_bad_lines=False)
	Core_Oil_Return_27June2017=Core_Oil_Return_27June2017[[0,1]] #just first two columns
	Core_RM_Non_Return_27June2017=pd.read_csv('Core_RM_Non_Return_27June2017.csv',header=None,error_bad_lines=False)
	Core_RM_Non_Return_27June2017=Core_RM_Non_Return_27June2017[[0,1]] #just first two columns
	output_dfs = [BS_Oil_Non_Return_27June2017,BS_Oil_Return_27June2017,BS_RM_Non_Return_27June2017,
			Core_Oil_Non_Return_27June2017,Core_Oil_Return_27June2017,Core_RM_Non_Return_27June2017]
	output_df_strs = ['BS_Oil_Non_Return_27June2017','BS_Oil_Return_27June2017','BS_RM_Non_Return_27June2017',
			  'Core_Oil_Non_Return_27June2017','Core_Oil_Return_27June2017','Core_RM_Non_Return_27June2017']
	output_csv_files(output_dfs, output_df_strs)

main_shell()
