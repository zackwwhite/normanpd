#!/usr/bin/python3
import sys
import sqlite3
from sqlite3 import Error
import re
import urllib.request
import PyPDF2



#fetchs the data of the daily activity normanpd page, uses regex to find all the pdf links to the daily incident Summery, 
#downloads all the daily activity pdfs, and returns the list of pdf links
def fetchincidents():
	#use urlib to access the data of the daily activy of the norman pd website
	with urllib.request.urlopen('http://normanpd.normanok.gov/content/daily-activity') as websiteData:
		#read the website and set it to pdfData
		pdfData = websiteData.read().decode('utf-8')
		#use rege to find all string in pdfData of the format
		#(four digits)-(two digits)-(two digits)%20Daily%20Incident%20Summary.pdf
		match = re.findall(r'\d{4}\-\d{2}\-\d{2}%20Daily%20Incident%20Summary\.pdf',str(pdfData))
		#for loop with the length of the number of strings found from the regex
		for index in range(len(match)):
			#create complete string of the download link of the pdf file
			pdfurl = 'http://normanpd.normanok.gov/filebrowser_download/657/%s' % (match[index])
			#open and download the pdf
			with urllib.request.urlopen(pdfurl) as fetchPDF:
				#create new file with the name of the iterator
				file = open(match[index], 'wb')
				#write to the new file with the PDF data
				file.write(fetchPDF.read())
				#close the file
				file.close()
			#end with
		#end for loop
		#returns the list of pdf names
		return match	
	#end with
#end fetchincident
	
#reads the pdf files, extracts the data, formats it, and puts it into an array of size 5 that will be appended to an array
#taht is returned
#input matches which is an array of strings that contain the links to the pdfs downloaded
def extractincidents(matches):
	#create empty array rawIncidents
	rawIncidents = []
	#for loop that iterates all the strings in matches
	for match in matches:
		#open a the pdf to read
		pdfPath = open(match, 'rb')
		#use the PyPDF2 PdfFileReader to read the pdf data
		pdf = PyPDF2.PdfFileReader( pdfPath )
		#fnd the number of pages in pdf
		pages = pdf.getNumPages()
		#for loop that runs for the number of pages in the pdf
		for pageNum in range(pages):
			#set page to the current page
			page = pdf.getPage(pageNum)
			#find all and extract the date_time in the pdf (2 digits)\(2 digits)\(4 digits) (2 digits):(2 digits)
			dates = re.findall((r'\d{1,2}\/\d{1,2}\/\d{4} \d{1,2}\:\d{2}'),page.extractText())
			#split by the regex date_time 
			sans_dates = re.split((r'\d{1,2}\/\d{1,2}\/\d{4} \d{1,2}\:\d{2}'),page.extractText())
			#create empty array tempIncidents
			tempIncidents = []
			#for loops that runs the length of date_time found
			for i in range(len(dates)):
				#appends the two strings together
				string = "%s %s" % (dates[i],sans_dates[i+1])
				#appends the new string the tempIncidents
				tempIncidents.append(string)
			#for loop iterates all elements in tempIncidents
			for i in tempIncidents:
				#splits the iterator by \n and appends that array to rawIncident
				rawIncidents.append(i.split('\n'))
	#creates array incident
	incidents = []
	#for loop iterates through rawIncidents
	for incident in rawIncidents:
		#find length of current iterator
		incidentLength = len(incident)
		#if the length is 2 then skip to next iterator
		if incidentLength == 2:
			continue
		#if length is 4, put the first 2 elements in arrray detail, then none and none, then the 3rd element
		elif incidentLength == 4:
			details = [incident[0], incident[1], None, None, incident[2]]
		#if length is 6 or 8, the put the first 5 elements in the array detail
		elif incidentLength == 6 or incidentLength == 8:
			details = [incident[0],incident[1],incident[2],incident[3],incident[4]]
		#if length is length is 7 or 9, then append the 3rd and 4th strings, then put the 1st, 2nd, new string,
		#5th and 6th elements in the array detail
		elif  incidentLength == 7 or incidentLength == 9:
			string  = "%s %s" % (incident[2],incident[3])
			details = [incident[0],incident[1], string, incident[4], incident[5]]
		#append array details to incident
		incidents.append(details)	
	#return incidents
	return incidents
#creates normanpd.db database and #creates the table incidents
def createdb():
	#create connect of normanpd.db
	conn = sqlite3.connect('normanpd.db')
	#creates cursor
	c = conn.cursor()

	#write create command in string
	create = "CREATE TABLE incidents (id INTEGER, number TEXT, date_time TEXT, location TEXT, nature TEXT, ORI TEXT);"
	
	#excute the create command
	c.execute(create)

#populates the table with the pdf data array
def populatedb(incidents):
	#create connection and cursor
	conn = sqlite3.connect('normanpd.db')
	c = conn.cursor()
	#idnum set to 0
	idnum = 0
	#for loop iterates incidents
	for incident in incidents:
		#set incidentNumber to 2nd element
		incidentNumber = incident[1]
		#set date_time to 1st element
		date_time = incident[0]
		#set location the the 3rd element
		location = incident[2]
		#set element to 4th element
		nature = incident[3]
		#set ORI to 5th element
		ORI = incident[4]
		#arrange the data to to format in order of table data
		insertdata = (idnum, incidentNumber, date_time, location, nature, ORI)
		#insert data into the table
		c.execute('INSERT INTO incidents VALUES (?,?,?,?,?,?)', insertdata)
		#increament idnum
		idnum += 1
		#commit connect
		conn.commit()
	#end for
	#close connection
	conn.close()

#stdout the rowcount of incidents
#and stdout 5 random rows
def status():
	#establish connection and cursor
	conn = sqlite3.connect('normanpd.db')
	c = conn.cursor()

	#write string for count command
	count = "SELECT count(*) from incidents"
	#use forloop to iterate the command
	for row in c.execute(count):
		#set rowcount to the string of the iterate
		rowcount = str(row)
	
	#stdout row count, remove the first character and last two character
	sys.stdout.write(rowcount[1:-2] + '\n')

	#write string of random command
	random = "SELECT * FROM incidents ORDER BY RANDOM() LIMIT 5"
	#for loop iterare execute command
	for row in c.execute(random):
		#write rows
		sys.stdout.write(str(row) + '\n')
	#commits connection
	conn.commit()
	#closes connection
	conn.close()


