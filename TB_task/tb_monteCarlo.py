import warnings,re,sys
warnings.simplefilter('ignore')
from random import betavariate as bvt, normalvariate as nvt
from matplotlib import pyplot as plt
import csv, openpyxl as opxl, pandas as pd, numpy as np

NUM_ITER = 1000 #run magic number of 1000 iterations

sys.setrecursionlimit(sys.getrecursionlimit()*2)

# return dictionary containing percentages, and change in percentages
def load_dict_list(sheet,topleft,bottomright):
	prog_list=list()
	country_list = ['US','EU','JPN','AP','CHN','LA']
	for index,rowObj in enumerate(sheet[topleft:bottomright]):
		prog_dict=dict()
		pdRow = pd.Series(rowObj).apply(lambda cell: cell.value)
		pdRowChg = pdRow.pct_change()
		prog_dict[country_list[index]] = (pdRowChg.values,pdRow.values)
		prog_list.append(prog_dict)
	return prog_list

##function tha writes average monte carlo...
def write_to_excel(prevValAggList,country,name_of_rows,alpha,beta):
	collapseVals = sum(prevValAggList)/len(prevValAggList)
	pd_df = pd.DataFrame(data={country:collapseVals})
	pd_df.to_csv('{}_{}_a={}_b={}.csv'.format(country, name_of_rows,alpha,beta))
	return

##MAIN LOOP THAT RUNS ITERATIONS
def run_iterations(country,name_of_rows,five_year_lock,pct_change,abs_value):
	prevValAggList = []
	for ITER in xrange(NUM_ITER):
				if(ITER%100==0): print(country,ITER,name_of_rows)
				currMonteRun,prevValue=[],None
				prevValList = []
				for index in range(len(pct_change)):
					if((five_year_lock and index>=5) or 
					  (not(five_year_lock) and np.isfinite(pct_change[index]))):
						mult = 2*bvt(alpha,beta) #betavariate distribution centered around 1.0
						NVT = nvt(1.0,0.1) #create a new normal distribution
						currMonteRun.append(prevValue*NVT*(1.0 + pct_change[index]*mult))
						prevValue*= NVT*(1.0 + pct_change[index]*mult)
					else:
						currMonteRun.append(abs_value[index])
						prevValue = abs_value[index]
					prevValList.append(prevValue)
				prevValAggList.append(prevValList)
				assert(len(X_axis)==len(currMonteRun))
				plt.plot(X_axis,currMonteRun)
	return prevValAggList

#runs monte carlo simulation on progress percent list 
def performMonteCarlo(prog_perc_list,name_of_rows,five_year_lock,alpha,beta,orient):
	X_axis = ['FY_{}'.format(num) for num in xrange(22,38)]
	for country_dict in prog_perc_list:
		for country in country_dict:
			currMonteRun = []
			pct_change,abs_value = country_dict[country][0],country_dict[country][1]
			plt.xlabel('Fiscal Year 2022 to 2037')
			if('perc' in name_of_rows): plt.ylabel('percent marketshare')
			else: plt.ylabel('absolute value marketshare') 
			plt.rcParams['figure.figsize'] = [9.6, 4.8]
			prevValAggList = run_iterations(country,name_of_rows,five_year_lock,pct_change,abs_value)
			write_to_excel(np.asarray(prevValAggList),country,name_of_rows,alpha,beta)
			plt.title('{}_Monte_{}_{}'.format(country,name_of_rows,orient))
			plt.savefig('{}_Monte_{}_{}.png'.format(country,name_of_rows,orient))
			assert(len(X_axis)==len(abs_value) and len(pct_change)==len(abs_value))
			plt.figure()
			plt.rcParams['figure.figsize'] = [9.6, 4.8]
			plt.plot(X_axis,abs_value)
			plt.title('{}_actual_{}_{}'.format(country,name_of_rows,orient))
			plt.savefig('{}_actual_{}_{}'.format(country,name_of_rows,orient))
			plt.xlabel('Fiscal Year 2022 to 2037'),plt.ylabel('Actual Values')


#wrapper function to perform Monte Carlo task
def runMonteCarloWrapper(prog_perc_list,prog_abs_list,bd_share_perc_list,
	bd_share_abs_list,price_per_flow,aggre_price_flow):
	for index,(alpha,beta,orient) in enumerate([(4,4,'center'),(2,6,'left'),(6,2,'right')]):
		performMonteCarlo(prog_perc_list, 'perc_prog',False, alpha, beta, orient)
		performMonteCarlo(prog_abs_list, 'abs_prog',False, alpha, beta, orient)
		performMonteCarlo(bd_share_perc_list, 'bdShare_perc',True, alpha, beta, orient)
		performMonteCarlo(bd_share_abs_list, 'bdShare_abs', False, alpha, beta, orient)
		performMonteCarlo(price_per_flow, 'price_flow', True, alpha, beta, orient)
		performMonteCarlo(aggre_price_flow, 'aggregate_price',False, alpha, beta, orient)
		print('done{}\n'.format(index+1))

## MAIN function that does everything
def main_shell():
	wb = opxl.load_workbook('TB_JULY_raw.xlsx')
	sheet = wb.get_sheet_by_name('raw_data')
	##run Monte Carlo simulation; for float percentage;
	prog_perc_list = load_dict_list(sheet, 'B1','Q6')
	print('done1main')
	prog_abs_list = load_dict_list(sheet, 'B7', 'Q12')
	print('done2main')
	bd_share_perc_list = load_dict_list(sheet, 'B16', 'Q21')
	print('done3main')
	bd_share_abs_list = load_dict_list(sheet, 'B22', 'Q27')
	print('done4main')
	price_per_flow = load_dict_list(sheet, 'B31', 'Q36')
	print('done5main')
	aggre_price_flow = load_dict_list(sheet,'B38', 'Q43')
	print('done6main')
	runMonteCarloWrapper(prog_perc_list,prog_abs_list,bd_share_perc_list,
		bd_share_abs_list,price_per_flow,aggre_price_flow)

######################## CALLS THE MAIN FUNCTION ##############################
main_shell()
###############################################################################
