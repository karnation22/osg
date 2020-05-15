import csv, requests

# return (False, [docs], ok_count) if there are reports missing; (True, None, ok_count) otherwise
def report_check(csv_links): #check the most recent date..
	datalinks = open(csv_links, 'r')
	dataFrame = list(csv.reader(datalinks))[1:]
	all_reports_present = True #assume all reports are present initially
	missing_reports = None
	ok_count = 0
	for (num,data) in enumerate(dataFrame):
		req = requests.get(data[0])
		if(req.status_code != requests.codes.ok):
			all_reports_present = False
			if(missing_reports != None): missing_reports.append(data[0])
			else: missing_reports  = [data[0]]
		else: ok_count+=1
	return(all_reports_present, missing_reports, ok_count) 

print(report_check('data-1527185380387.csv'))