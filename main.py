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


#	CONSTANTS
PATH = 'Sales Files'
files = FileList(PATH)
print files.files

totalSize = 0

while not files.isEmpty():
	nextFile = files.getNextFile()

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
print "Program finished writing to csv."
print "Wrote " + str(totalSize) + " bytes total to csvs."
