import scanf, requests, psycopg2, argparse #relevant packages
HTTP_OK = 200 #magic number of HTTP OK status code

#count the reports - flag whether all reports are present, link the missing reports, and
	#delineate number of ok reports...
def report_counter(link_rows):
	all_reports_present = True #assume all reports are present initially
	missing_reports = None
	ok_count = 0
	for data in link_rows:
		req = requests.get(data[0])
		if(req.status_code != HTTP_OK):
			all_reports_present = False
			if(missing_reports != None): missing_reports.append(data[0])
			else: missing_reports  = [data[0]]
		else: ok_count+=1
	print("All reports present: %s"%all_reports_present)
	print("# of HTTP_OK reports: %d"%ok_count)
	print("Missing reports: ")
	print(missing_reports)
	return("Done!")

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
	parser.add_argument('--rt', nargs=1, type=str, default='weekly', \
		required=False, help='specify type of reports', \
		choices=['daily', 'weekly', 'monthly', 'yearly'])
	parser.add_argument('--rd', nargs=1, type=str, required=True,
		help='specify date for which count must occur')
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
		conn = psycopg2.connect(host='jli-may152018.ctzkxaoqvbrx.us-east-1.rds.amazonaws.com', \
			user='postgres', password='Optimal.01', dbname='JLI')
	except: 
		print('unable to connect to database...')
		return
	cursor = conn.cursor()
	SQL_query = "SELECT link FROM report_info_history WHERE report_type='"+report_type+ \
				"' AND run_date::date='"+year+"-"+month+"-"+date+"'"
	try:
		cursor.execute(SQL_query)
		rows = cursor.fetchall()
		return rows
	except: print("unable to process SQL query given connected database")
	return
	

# Main function that runs everything above...
def PG_SQL_Main():
	report_type_date = main_parser()
	# check if report_type == None; if not, proceed normally
	if(report_type_date != None):
		rows = write_PGSQL_script_and_collect(report_type_date)
		if(rows != None): print(report_counter(rows))
	return
			

PG_SQL_Main()