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