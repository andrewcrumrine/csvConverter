"""
	Norpak CSV Converter

	Andrew Crumrine
	8/6/2015

	This script reads a file and outputs a CSV for sales history

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
		if self.fid != None:
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

class CSVCreator(object):
	"""
	CSVCreator object creates a csv file based off the incoming file name.
	It takes in text given to it by the TxtFileReader object and splices
	the data into the required fields.
	"""

	def __init__(self,filenameIn):
		"""
	This initializes the CSVCreator object.  It sets the header titles,
	defines the locations on a given line where the specific fields are,
	and creates the csv file
		"""
		self.SIG_FIGS = 5

		self.customerID = ''
		self.customer = ''
		self.itemID = ''
		self.item = ''
		self.total = None
		self.totalSum = 0
		self.rate = 0

		self.header = ['Customer ID', 'Customer Name', 'Item ID', \
			'Item Description', 'Date','Quantity','Rate', 'Price',\
			'Transaction Type']

		self.indices = {self.header[0]:[0,8], self.header[1]:[14,40], \
			self.header[2]:[44,60], self.header[3]:[60,86], self.header[4]:\
			[101,110], self.header[5]:[110,135], self.header[6]:[160,171],\
			self.header[7]:[171,185]}
		self.fileOut = self.__getFilenameOut(filenameIn)
		self.text = ''
		if self.__isCSV() :
			self.fid = open(self.fileOut,'w')
			self.__createHeader()

	def __del__(self):
		"""
	This method runs when the object is destroyed.  It closes the file.
		"""
		self.fid.close()


	def __getFilenameOut(self,filenameIn):
		"""
	This method runs when the object is initialized.  It defines the name
	of the output csv based off the incoming text file name
		"""		
		if filenameIn.find('.txt') != -1 :
			return filenameIn[:filenameIn.find('.txt')] + '.csv'
		return filenameIn


	def __isCSV(self):
		"""
	This method runs after the csv file has been named.  It checks to
	make sure the csv file was named properly
		"""		
		if self.fileOut.find('.csv') != -1 :
			return True
		return False


	def __createHeader(self):
		"""
	This method runs after the csv has been verified.  It creates the header
	based off of the previously defined fields.
		"""
		count = 0
		end = len(self.header)
		for field in self.header:
			self.fid.write(field)
			count += 1
			if count != end:
				self.__nextField()
		self.__nextEntry()

	def writeToCSV(self,textIn):
		"""
	This is the only public method in the class.  It accepts an incoming string
	and wraps around the setText and setEntry method.  It passes the incoming
	string to the setText method.		
		"""
		self.__setText(textIn)
		self.__setEntry()


	def __setText(self,textIn):
		"""
	This method sets the text variable to the value passed to it by the
	writeToCSV method
		"""
		self.text = textIn


	def __setEntry(self):
		"""
	This is method manages the data written to the csv file.  It saves the
	customer and item data to be used on other entries
		"""
		count = 0
		end = len(self.header)
		self.__setCustomer()
		self.__setItem()
		self.__setRate()
		for field in self.header:
			self.__setField(field)
			count += 1
			if count != end:
				self.__nextField()
		self.__nextEntry()

	def __setField(self,field):
		"""
	This method writes data to the csv file.  It pulls persistant data
	stored in the class for the fields it doesn't have.  It scrubs the data
	for each entry for formatting errors.  It takes an incoming field name
	pulled from the header list, finds the data from the text variable and
	writes to the csv.
		"""
		if field == self.header[0]:
			fieldVal = self.customerID
		elif field == self.header[1]:
			fieldVal = self.customer
		elif field == self.header[2]:
			fieldVal = self.itemID
		elif field == self.header[3]:
			fieldVal = self.item
		elif field == self.header[6]:
			fieldVal = self.rate
		elif field == self.header[-1]:
			if self.__isCredit():
				fieldVal = 'Credit'
			else:
				fieldVal = 'Sale'
		else:
			fieldVal = self.__iterText(field)
		fieldVal = s.removeSpaces(fieldVal)
		fieldVal = s.removeCommas(fieldVal)
		self.fid.write(fieldVal)


	def __nextField(self):
		"""
	This method just adds a comma to the csv. It divides the two fields.
		"""
		self.fid.write(',')


	def __nextEntry(self):
		"""
	This method just writes a new line character to the csv.  It divides the
	two entries.
		"""
		self.fid.write('\n')

	def __iterText(self,textIn):
		"""
	This method does the grunt work.  It accepts a string, searches the
	dictionary for the two keys, splices the instance variable holding the
	string from the text file, and returns the splice.
		"""
		key1 = self.indices[textIn][0]
		key2 = self.indices[textIn][1]
		return self.text[key1:key2]

	def __hasCustomer(self):
		"""
	This method checks if the instance text variable has customer data.
		"""
		customerID = self.__iterText(self.header[0])
		if customerID.find(' ') == -1:
			self.customerID = customerID
			return True
		self.__clearCustomer()
		return False

	def __setCustomer(self):
		"""
	This method runs the hasCustomer method.  If the text variable has customer
	data, it sets the customer variables
		"""
		if self.__hasCustomer():
			self.customer = self.__iterText(self.header[1])
		pass

	def __hasItem(self):
		"""
	This method is the same as the hasCustomer method, but checks the item data
	It returns a boolean.
		"""
		itemID = self.__iterText(self.header[2])
		if itemID.find('F') != -1 or itemID.find('G') != -1:
			self.itemID = itemID
			return True
		return False

	def __setItem(self):
		"""
	This method is the same as the setCustomer method, but sets the item data.
		"""
		if self.__hasItem():
			self.item = self.__iterText(self.header[3])
		pass

	def __isCredit(self):
		"""
	This method checks the quantity field to make sure the transaction is
	a sale.  If not, it returns false.
		"""
		if self.__iterText('Quantity').find('-') >= 0:
			return True
		return False

	def __clearCustomer(self):
		"""
		Clears customer from memory so customer is not repeated for every row.
		"""
		self.customer = ''
		self.customerID	= ''

	def __setRate(self):
		"""
		Calculates the rate to a higher percision of digits so the original value can 
		be overwritten.
		"""
		self.rate = float(self.__iterText(self.header[7])) / float(self.__iterText(self.\
			header[5]))

		self.rate = str(round(self.rate,self.SIG_FIGS))