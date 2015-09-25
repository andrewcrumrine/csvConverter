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
import os
import sys

#	CONSTANTS
PATH = 'Sales Files'
totalSize = 0

if sys.argv[0] is not None:
	fullBuild = sys.argv[0]
else:
	fullBuild = True

if fullBuild:
	files = FileList(PATH)
	print files.files



	while not files.isEmpty():
		nextFile = files.getNextFile(True)

		csvOut = CSVCreator(nextFile,True)
		inFile = TxtFileReader(nextFile)

		while inFile.reading:
			lineOut = inFile.getNextLine()
			if lineOut != None:
				csvOut.writeToCSV(lineOut.getText())
		csvOut.closeCSV()

		size = os.path.getsize(csvOut.fileOut)
		totalSize += size
		print "Wrote " + str(size) + " bytes to " + csvOut.fileOut + "."

csvFiles = FileList(PATH,csv=True)
csvOut = FileMerge(csvFiles.getNextFile(True))
while len(csvFiles.files) > 0:
	csvOut._setFileIn(csvFiles.getNextFile(True))
	csvOut._translateCSV()

creditFiles = FileList(PATH,csv=True,credit=True)
creditOut = FileMerge(creditFiles.getNextFile(True),'Credit.csv')
while len(creditFiles.files) > 0:
	creditOut._setFileIn(creditFiles.getNextFile(True))
	creditOut._translateCSV()
print "Program finished writing to csv."
print "Wrote " + str(totalSize) + " bytes total to csvs."
