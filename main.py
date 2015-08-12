"""
	CSV Converter Main Routine

	Andrew Crumrine
	8/6/2015

	Wrapper script that executes csvConverter.py

"""

#	Import csvConverter
from csvConverter import *
from manageFiles import *
import os


#	CONSTANTS
PATH = 'Sales Files'
files = FileList(PATH)
print files.files

while not files.isEmpty():
	nextFile = files.getNextFile()

	csvOut = CSVCreator(nextFile)
	inFile = TxtFileReader(nextFile)

	while inFile.reading:
		lineOut = inFile.getNextLine()
		if lineOut != None:
			csvOut.writeToCSV(lineOut.getText())

	size = os.path.getsize(csvOut.fileOut)
	print "Wrote " + str(size) + " bytes to " + csvOut.fileOut + "."
print "Program finished writing to csv."
