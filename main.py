#! /usr/bin/python

"""
	CSV Converter Main Routine

	Andrew Crumrine
	8/6/2015

	Wrapper script that executes csvConverter.py

"""

#	Import required libraries
from csvConverter import *
from fileReader import *
from manageFiles import *
from buildSalesMap import *
import os


#	CONSTANTS
PATH = 'Sales Files'
SALES_MAP_FILE = 'CashSales484.csv'
USE_MAP = True
files = FileList(PATH)
print files.files

if USE_MAP:
	totalSalesMap = SalesMap(SALES_MAP_FILE)
	totalSalesMap.buildMap()

totalSize = 0

while not files.isEmpty():
	nextFile = files.getNextFile()

	csvOut = CSVCreator(nextFile,useSalesOrder = True,useMap = True)
	inFile = TxtFileReader(nextFile)

	while inFile.reading:
		lineOut = inFile.getNextLine()
		if lineOut != None:
			if USE_MAP:
				csvOut.writeToCSV(lineOut.getText(),totalSalesMap)
			else:
				csvOut.writeToCSV(lineOut.getText())
	csvOut.closeCSV()

	size = os.path.getsize(csvOut.fileOut)
	totalSize += size
	print "Wrote " + str(size) + " bytes to " + csvOut.fileOut + "."
print "Program finished writing to csv."
print "Wrote " + str(totalSize) + " bytes total to csvs."
