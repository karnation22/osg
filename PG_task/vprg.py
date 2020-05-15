import scanf, psycopg2, requests, argparse, string, json #relevant packages
from requests.auth import HTTPBasicAuth
from datetime import datetime, timedelta
HTTP_OK = 200 #magic number of HTTP OK status code
ASCII = string.printable

#count the reports - flag whether all reports are present, link the missing reports, and
	#delineate number of ok reports...
# def report_counter(link_rows):
# 	all_reports_present = True #assume all reports are present initially
# 	missing_reports = None
# 	ok_count = 0
# 	for data in link_rows:
# 		req = requests.get(data[0])
# 		if(req.status_code != HTTP_OK):
# 			all_reports_present = False
# 			if(missing_reports != None): missing_reports.append(data[0])
# 			else: missing_reports  = [data[0]]
# 		else: ok_count+=1
# 	return(all_reports_present, missing_reports, ok_count)

#returns appropriate branch folder based on report type and report date information
def return_folder_branch(report_type_date):
	(report_type, (month, day, year)) = report_type_date
	assert(report_type in ['weekly', 'monthly', 'quarterly'])
	oldtime = datetime(year=int(year), month=int(month), day=int(day))
	if(oldtime.weekday() != 1): raise Exception("Date supplied is invalid - needs to be a Tuesday of a given week")
	newtime = oldtime - timedelta(days=3) #assume report runs three days after folder date...
	if(report_type=='weekly'): #weekly case - look for Saturday folder for follwing Tuesday run date
		(new_month, new_day, new_year) = (str(newtime.month), str(newtime.day), str(newtime.year))
		if(len(new_month)==1): new_month='0'+new_month #implies single digit month
		if(len(new_day)==1): new_day='0'+new_day #implies single digit day
		return new_month+'_'+new_day+'_'+new_year
	elif(report_type=='monthly'):
		return month+"_"+year
	else: #quarterly run date
		if(int(month)==1): return 'Q4'+'_'+str(int(year)-1)
		elif(2<=int(month)<=4): return 'Q1'+'_'+year
		elif(5<=int(month)<=7): return 'Q2'+'_'+year
		elif(8<=int(month)<=10): return 'Q3'+'_'+year
		else: return 'Q4'+'_'+year #month==11 or month==12

#returns the count of number of reports on Jasper server
def find_Jasper_count(report_type_date):
	folder = return_folder_branch(report_type_date)
	print("folder: %s"%folder)
	url = 'http://ec2-52-45-228-251.compute-1.amazonaws.com:9090/jasperserver/rest_v2/resources?type=file&folderURI=LatestJLIPDFs/'+folder
	print('URL: %s'%url)
	try: 
		req = requests.get(url=url, auth=HTTPBasicAuth('steve.fan@optimalstrategix.com', 1234))
		print('status code: %s'%req.status_code)
	except: print("unable to connect to JASPERSOFT for given run date, url, and credentials")
	print("Jaspersoft count: %d"%int(req.headers['Total-Count']))
	return (int(req.headers['Total-Count']))


#parse the argument dictionary
def parse_type_n_date(args_dict):
	report_type = args_dict['rt'][0] 
	mm_dd_yyyy = args_dict['rd'][0]
	report_date = scanf.scanf(format="%s-%s-%s", s=mm_dd_yyyy)
	return(report_type, report_date)

#helper function that creates command line arguments and parses them...
def main_parser():
	parser = argparse.ArgumentParser(description='Verify Report Count JLI Server')
	##--rt argument
	parser.add_argument('--rt', nargs=1, type=str, required=True, \
		help='specify type of reports for JLI report verification', \
		choices=['weekly', 'monthly', 'quarterly'])
	parser.add_argument('--rd', nargs=1, type=str, required=True,
		help='specify date for which count must occur(format mm-dd-yyyy); \
		ensure date is on a Tuesday of calendar year...')
	args = parser.parse_args()
	args_dict = vars(args) #dictionary with arguments (feed into helper function...)
	try:
		(report_type, report_date) = parse_type_n_date(args_dict)
		return (report_type, report_date)

	except: print("incorrect formatting for report dates - please format via mm-dd-yyyy")

	return

def write_PGSQL_script_and_collect(report_type_date):
	(report_type, (month, date, year)) = report_type_date
	try:
		conn = psycopg2.connect(host='jli-prod-jun-07-2018.ctzkxaoqvbrx.us-east-1.rds.amazonaws.com', \
			user='postgres', password='Optimal.01', dbname='JLI')
	except: 
		print('unable to connect to database...')
		return
	cursor = conn.cursor()
	SQL_query = "SELECT count(*) FROM report_info_history WHERE report_type='"+report_type+ \
				"' AND run_date::date='"+year+"-"+month+"-"+date+"'"
	try:
		cursor.execute(SQL_query)
		rows = cursor.fetchall()
		print("SQL_query: %s"%SQL_query)
		cur_count = int(rows[0][0]) #count reported for number of reports in the SQL database 
		print("PGSQL Count: %d"%cur_count)
		return cur_count

	except: print("unable to process SQL query given connected database")
	return
	

# Main function that runs everything above...
def PG_SQL_Main():
	report_type_date = main_parser()
	# check if report_type == None; if not, proceed normally
	if(report_type_date != None):
		cur_count = write_PGSQL_script_and_collect(report_type_date)
		jasper_count = find_Jasper_count(report_type_date)
	if(cur_count==jasper_count): print "Counts match!"
	else: raise Exception("SQL server and Jaspersoft counts DO NOT match")
	return
			

PG_SQL_Main()