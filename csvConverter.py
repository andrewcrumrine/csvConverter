"""
	Norpak CSV Converter

	Andrew Crumrine
	8/6/2015

	This script reads a file and outputs a CSV for sales history

"""

import stringMan as s


class CSVCreator(object):
	"""
	CSVCreator object creates a csv file based off the incoming file name.
	It takes in text given to it by the TxtFileReader object and splices
	the data into the required fields.
	"""

	def __init__(self,filenameIn=None,useSalesOrder = False):
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
		self.rate = 0
		self.fileIn = filenameIn
		self.fileOut = None
		self.text = ''
		self.switchText = ''
		self.fid = None
		self.useSalesOrder = useSalesOrder
		self.total = 0
		self.writeTotal = False

		self.header = ['Customer ID', 'Customer Name', 'Item ID', \
			'Item Description', 'Date','Quantity','Rate', 'Price',\
			'Sales Total','Transaction Type']

		self.indices = {self.header[0]:[0,8], self.header[1]:[14,40], \
			self.header[2]:[44,60], self.header[3]:[60,86], self.header[4]:\
			[101,110], self.header[5]:[110,135], self.header[6]:[160,171],\
			self.header[7]:[171,185]}
		if type(self) == CSVCreator:
			self.salesOrder = None
			self.__createCSV()


	def __del__(self):
		"""
	This method runs when the object is destroyed.  It closes the file.
		"""
		if self.fid is not None:
			self.fid.close()

	def __createCSV(self):
		"""
	Copies the filename in and generates a csv.  Completes after creating a 
	header
		"""
		self.fileOut = self.__getFilenameOut(self.fileIn)
		self.text = ''
		if self.__isCSV() :
			self.fid = open(self.fileOut,'w')
			self.__createHeader()


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
		if self.useSalesOrder:
			self.__setSwitchedText(textIn)
			self.__setText(textIn)
			if self.__hasCustomer() and self.salesOrder is None:
				self.__createSalesOrder(textIn)
			elif self.__hasCustomer() and self.salesOrder is not None:
				self.total = self.salesOrder.getTotal()
				self.__writeFromSalesOrder()
				self.__createSalesOrder(textIn)
			elif not self.__hasCustomer():
				self.__addToSalesOrder(textIn)

		else:
			self.__setText(textIn)
			self.__setEntry()

	def __writeFromSalesOrder(self):
		"""
	Iterates the Sales Order object and writes to csv
		"""
		entries = self.salesOrder.getEntries()
		count = 0
		end = len(entries)
		for textIn in entries:
			count += 1
			if count == end:
				self.writeTotal = True
			else:
				self.writeTotal = False
			self.__setText(textIn)
			self.__setEntry()

	def __setText(self,textIn):
		"""
	This method sets the text variable to the value passed to it by the
	writeToCSV method
		"""
		self.text = textIn

	def __setSwitchedText(self,textIn):
		"""
	This method sets the text variable to the value passed to it by the
	writeToCSV method.  Used to store a line of text that does not belong to the
	buffered sales order.  Once the sales order is committed to the csv, the
	switched text is transfered to the normal text.
		"""
		self.switchText = textIn


	def __setEntry(self):
		"""
	This is method manages the data written to the csv file.  It saves the
	customer and item data to be used on other entries
		"""
		count = 0
		end = len(self.header)
		self.__setCustomer()
		self.__setItem()
		self.setRate()
		for field in self.header:
			if field != 'Sales Total':
				self.__setField(field)
			elif field == 'Sales Total' and self.writeTotal:
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
		elif field == self.header[-2]:
			fieldVal = self.total
		elif field == self.header[-1]:
			if self.isCredit():
				fieldVal = 'Credit'
			else:
				fieldVal = 'Sale'
		else:
			fieldVal = self.iterText(field)
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

	def iterText(self,keyIn,altText=False,textIn=None):
		"""
	This method does the grunt work.  It accepts a string, searches the
	dictionary for the two keys, splices the instance variable holding the
	string from the text file, and returns the splice.
		"""
		key1 = self.indices[keyIn][0]
		key2 = self.indices[keyIn][1]
		if not altText:
			return self.text[key1:key2]
		else:
			return textIn[key1:key2]

	def __hasCustomer(self):
		"""
	This method checks if the instance text variable has customer data.
		"""
		customerID = self.iterText(self.header[0])
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
			self.customer = self.iterText(self.header[1])
		pass

	def __hasItem(self):
		"""
	This method is the same as the hasCustomer method, but checks the item data
	It returns a boolean.
		"""
		itemID = self.iterText(self.header[2])
		if itemID.find('F') != -1 or itemID.find('G') != -1:
			self.itemID = itemID
			return True
		return False

	def __setItem(self):
		"""
	This method is the same as the setCustomer method, but sets the item data.
		"""
		if self.__hasItem():
			self.item = self.iterText(self.header[3])
		pass

	def isCredit(self,textIn=None):
		"""
	This method checks the quantity field to make sure the transaction is
	a sale.  If not, it returns false.
		"""
		if textIn is None:
			if self.iterText(self.header[5]).find('-') >= 0:
				return True
		else:
			if self.iterText(self.header[5],True,textIn).find('-') >= 0:
				return True
		return False

	def __clearCustomer(self):
		"""
	Clears customer from memory so customer is not repeated for every row.
		"""
		self.customer = ''
		self.customerID	= ''

	def setRate(self,textIn=None):
		"""
	Calculates the rate to a higher percision of digits so the original value can 
	be overwritten.
		"""
		if textIn is None:
			if not self.isCredit():
				quantity = float(s.removeCommas(self.iterText(self.header[5])))
				price = float(s.removeCommas(self.iterText(self.header[7])))
				self.rate = str(round(price / quantity,self.SIG_FIGS))
		else:
			if not self.isCredit():
				quantity = float(s.removeCommas(self.iterText('Quantity',True,\
					textIn)))
				price = float(s.removeCommas(self.iterText('Price',True,\
					textIn)))
				return str(round(price / quantity,self.SIG_FIGS))

	def __createSalesOrder(self,textIn):
		"""
	Creates sales order list in order to return sum total.
		"""
		self.salesOrder = SalesOrder(textIn)

	def __addToSalesOrder(self,textIn):
		"""
	Adds additional lines of text to the sales order object
		"""
		self.salesOrder.addEntry(textIn)

class SalesOrder(CSVCreator):
	"""
	Builds a sales order from a series of itemized lines inputed from the 
	CSVCreator object.  The intent of the class is to output a sum total.
	"""
	def __init__(self,textIn):
		"""
	Input the first line into the text list.
		"""
		CSVCreator.__init__(self)
		self.entries = [textIn]
		self.total = 0
		self.addToTotal(textIn)
		self.credits = []

	def addEntry(self, textIn):
		"""
	Inputs text from the CSV Creator to the text list
		"""
		self.addToTotal(textIn)
		print self.total
		self.entries.append(textIn)

	def getTotal(self):
		"""
	Returns total calculated price for the sales order in a string
		"""
		return str(round(self.total,2))

	def addToTotal(self,textIn):
		"""
	Returns the added price to the total
		"""
		if not self.isCredit(textIn):
			price = float(s.removeCommas(self.iterText('Price',True,textIn)))
			self.total += price


	def getEntries(self):
		"""
	Returns the stored entries in the object.
		"""
		self.deductCreditsFromEntries()
		return self.entries


	def __createCreditList(self):
		"""
	Builds list of credits in order
		"""
		for entry in self.entries:
			if self.isCredit(entry):
				self.credits.append(entry)

	def __removeCreditsFromEntries(self):
		"""
	Scans the entry list for credits and removes them.
		"""
		for credit in self.credits:
			self.entries.remove(credit)

	def __compareCredit(self,textIn):
		"""
	Scans entry list for credit match and returns an index, returns -1 if no match
		"""
		count = 0
		for entry in self.entries:
			if self.iterText('Item ID', True, textIn) == \
			self.iterText('Item ID', True, entry):
				return count
			count += 1
		return -1

	def __returnQuantity(self,textIn):
		"""
	Returns quantity from text input 
		"""
		textOut = self.iterText('Quantity',True,textIn)
		textOut = s.removeSpaces(textOut)
		textOut = s.removeCommas(textOut)
		textOut = s.removeMinus(textOut)
		return int(textOut)

	def __addSpaces(self,textIn,field):
		"""
	Prefixes spaces to make string desired length
		"""
		length = self.indices[field][1] - self.indices[field][0]
		while len(textIn) < length:
			textIn = ' ' + textIn
		return textIn

	def __updateEntry(self,index,quantNew,priceNew,rate):
		"""
	Updates the entry with the credits taken into account.
		"""
		newEntry = self.entries[index]
		newEntry.replace(self.iterText('Quantity',True,newEntry),\
			quantNew)
		newEntry.replace(self.iterText('Rate',True,newEntry),\
			rate)
		newEntry.replace(self.iterText('Price',True,newEntry),\
			priceNew)
		self.entries[index] = newEntry

	def deductCreditsFromEntries(self):
		"""
	Isolates credits from order, deducts credits from order if items match,
	otherwise appends credits to entry list.
		"""
		creditsToAdd = []
		self.__createCreditList()
		self.__removeCreditsFromEntries()
		for credit in self.credits:
			index = self.__compareCredit(credit)
			if index == -1:
				creditsToAdd.append(credit)
			else:
				rate = self.setRate(self.entries[index])
				quantCredit = self.__returnQuantity(credit)
				quantEntry = self.__returnQuantity(self.entries[index])
				quantNew = quantEntry - quantCredit
				newPrice = self.__addSpaces(str(quantNew * float(rate)),'Price')
				quantNew = self.__addSpaces(str(quantNew),'Quantity')
				rate = self.__addSpaces(rate,'Rate')
				self.__updateEntry(index,quantNew,newPrice,rate)


