"""
	fileReader.py

	File Reader Module
	------------------

	This module manages reading the text files outputted from the AS400.  You can 
	read the files, filter lines of text that are not prefferred, and pass the
	appropriate lines of text to the CSVCreator class.

"""

import stringMan as s

class TxtFileReader():
	"""
	This object manages opening the incoming text file, creating a TxtBuffer
	object, destroying it and moving on to the next line.  The object also
	manages when the read text is in the header.
	"""
	def __init__(self, filenameIn):
		"""
	This initializes the TxtFileReader object.  It stops the program if a
	file cannot be opened.
		"""
		self.header = True
		self.reading = True
		self.buffer = None
		self.fid = None
		try:
			self.fid = open(filenameIn,'r')
		except IOError:
			print filenameIn + " does not exist in this directory."
			raise SystemExit

	def __del__(self):
		"""
	When the object is destroyed, this method will close the file.
		"""
		if self.fid is not None:
			self.fid.close()

	def getNextLine(self):
		"""
	This method creates a new TxtBuffer object.  It tells the program when
	There is no more text to be read.
		"""
		self.buffer = TxtBuffer(self.fid)
		self.__setReading()
		self.__updateHeader()
		if self.buffer.returnLine and self.header == False:
			return self.buffer
		return None

	def __updateHeader(self):
		"""
	This method manages the header instance variable based off of what's
	passed from the TxtBuffer object.
		"""
		if self.buffer.header != None:
			if self.buffer.header and self.header == False:
				self.header = True
			if self.buffer.header == False and self.header == True:
				self.header = False

	def __setReading(self):
		"""
	This method sets the reading method to false if there are no more
	lines of text read from the file.
		"""
		if self.buffer.text == '':
			self.reading = False

class TxtBuffer():
	"""
	This class screens the string produced by the readline method
	from the TxtFileReader class.  It checks for the header, the sum
	lines and blank lines.
	"""

	def __init__(self,fid):
		"""
	This initializes instance variables such as keys, the size of the 
	string and the content read from the TxtFileReader() object
		"""
		self.HEADER_KEY_START = ' */**/15'
		self.HEADER_KEY_STOP = '------'
		self.TOTAL_KEY_1 = '*\r\r\n'
		self.TOTAL_KEY_2 = '*\r\n'
		self.TOTAL_KEY_3 = '*\n'
		self.text = fid.readline()
		self.size = len(self.text)
		self.header = None
		self.returnLine = self.__checkReturnLine()

	def __checkReturnLine(self):
		"""
	This method screens the string output for undesirable strings
		"""
		if self.__isHeader() or self.__isBlankLine() or self.__isTotalLine():
			return False
		return True

	def __isBlankLine(self):
		"""
	This method checks the read screen for a blank line.
		"""
		if self.size < 10:
			return True
		return False

	def __isHeader(self):
		"""
	This method checks the read line to see if it's a header.
		"""
		if self.__isSpecialLine(self.HEADER_KEY_START,0,'*') :
			self.header = True
			return True
		if self.__isSpecialLine(self.HEADER_KEY_STOP,0) :
			self.header = False
			return True
		return False

	def __isTotalLine(self):
		"""
	This method screens for any totals lines produced by the report.
		"""
		if self.__isSpecialLine(self.TOTAL_KEY_1,self.size - len(self.TOTAL_KEY_1)) \
		or self.__isSpecialLine(self.TOTAL_KEY_2,self.size - len(self.TOTAL_KEY_2)) \
		or self.__isSpecialLine(self.TOTAL_KEY_3,self.size - len(self.TOTAL_KEY_3)):
			return True
		return False

	def __isSpecialLine(self,key,loc,wc=None):
		"""
	This method is a general method that returns a boolean if the text you're
	looking for is where you expect it to be.
		"""
		if s.wildSearch(self.text,key,wc) == loc :
			return True
		return False

	def getText(self):
		"""
	This method returns the instance text variable.  It's called if the text
	passes all of the tests.  It intentionally removes the last two characters
	to prevent extra new line characters from being passed to the csv.
		"""
		return self.text[:-2]

class MapReader(object):
	def __init__(self,fileIn):
		self.delim = '\t'
		self.fid = None
		self.fileName = fileIn
		self.reading = True
		self._openFile()

	def __del__(self):
		if self.fid is not None:
			self.fid.close()

	def _openFile(self):
		self.fid = open(self.fileName,'r')

	def getMap(self):
		mapOut = {}
		while self.reading:
			key,value = self._getNextPair()
			if key is not None:
				mapOut[key] = value
		return mapOut

	def _getNextPair(self):
		text = self.fid.readline()
		if text == '':
			self.reading = False
		else:
			key = s.subStrByChar(text,'','\t')
			key = s.removeSpaces(key)
			value = s.subStrByChar(text,'\t','\n')
			value = s.removeSpaces(value)
			return key,value
		return None,None