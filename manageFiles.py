"""
	This module manages the files and logs the output to the user.
"""

import os

class FileList():
	def __init__(self,path='',csv=False):
		self.path = path
		if csv:
			self.files = self.__generateCSVList()
		else:
			self.files = self.__generateList()

	def __generateList(self):
		os.chdir(self.path)
		txtFiles = []
		files = os.listdir(os.curdir)
		for f in files:
			if self.__isTxtFile(f):
				txtFiles.append(self.path + '/' + f)
		os.chdir('..')
		return txtFiles

	def __generateCSVList(self):
		os.chdir(self.path)
		csvFiles = []
		files = os.listdir(os.curdir)
		for f in files:
			if self.__isCSVFile(f) and self.__isNotCredit(f):
				csvFiles.append(self.path + '/' + f)
		os.chdir('..')
		return csvFiles		

	def __isTxtFile(self,f_str):
		if f_str[-4:] == '.txt':
			return True
		return False

	def getNextFile(self,ascending=False):
		if ascending:
			fileOut = self.files[0]
			self.files = self.files[1:]
			return fileOut
		else:
			return self.files.pop()

	def isEmpty(self):
		if len(self.files) == 0:
			return True
		return False

	def __isCSVFile(self,f_str):
		if f_str[-4:] == '.csv':
			return True
		return False

	def __isNotCredit(self,f_str):
		if f_str[:6] != 'Credit':
			return True
		return False

class FileMerge():
	def __init__(self,fileIn):
		self.fileout = 'out.csv'
		self.fid = None
		self._setFileIn(fileIn)
		try:
			self.fid = open(self.fileout,'w')
		except IOError:
			print("Cannot open write file")
			raise SystemExit
		self._translateCSV(True)


	def __del__(self):
		if self.fid is not None:
			self.fid.close()
		if self.fileIn is not None:
			self.fileIn.close()

	def _setFileIn(self,fileIn):
		try:
			self.fileIn = open(fileIn,'r')
		except IOError:
			print("File does not exist.")
			raise SystemExit		

	def _translateCSV(self,header=False):
		if header:
			readLine = None
		else:
			readLine = self.fileIn.readline()
		while readLine != '':
			readLine = self.fileIn.readline()
			self.fid.write(readLine)
