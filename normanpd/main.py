#!/usr/bin/env python
#-*- coding: utf-8 -*-
import normanpd
from normanpd import norman

"""the main program"""
def main():
	#download data
	#sets match to the array of links to pdfs download and saved from method
	match = norman.fetchincidents()

	#extract data
	#set incidents to the array of the formated data extracted from the pdfs
	#input the links match created in fetchincident
	incidents = norman.extractincidents(match)

	#Create Database
	#creates the Database normadpd.db and the table incidents
	norman.createdb()

	#insert data
	#populations the incident table with the array of the pdf data from extractincidents
	norman.populatedb(incidents)

	#print status
	#gives the status of the database by stdout the rowcount of incident and 
	#returns 5 random rows from the table
	norman.status()

if __name__ == '__main__':
	main()
