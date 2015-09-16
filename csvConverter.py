"""
	Norpak CSV Converter

	Andrew Crumrine
	8/6/2015

	This script reads a file and outputs a CSV for sales history

"""

import stringMan as s
import fileReader as f


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
		self.p_inv = ''
		self.rate = 0
		self.fileIn = filenameIn
		self.fileOut = None
		self.text = ''
		self.switchText = ''
		self.fid = None
		self.Cfid = None
		self.useSalesOrder = useSalesOrder
		self.total = 0
		self.writeTotal = False
		self.printCustomer = True

		self.defaults = {'Undeposited Funds':"True", "Subsidiary": "7",\
			"Location":"3", "Payment Method":"Cash","Tax Code":"-8",\
			"Price Level":"-1",'Cost Estimate':"Custom"}

		self.customerMap = {}
		self.itemMap = {}
		self.unitsMap = {}
		self.postingMap = {}
		self.invoiceMap = {}


		self.header = ['Undeposited Funds', 'Posting Period', 'Customer',\
		'Subsidiary','Location','Payment Method','Transaction Date','Item',\
		'Quantity','Rate','Tax Code','Units','Price Level','Sales Total',\
		'Cost Estimate','Cost','Invoice','Inv Open','Parent Inv']

		self.indices = {'Customer ID':[0,8], 'Customer Name':[14,40], \
			'Item ID':[44,60], 'Item Description':[60,86], 'Date':\
			[101,110], 'Quantity':[110,135], 'Rate':[160,171],\
			'Price':[171,185],'Invoice':[94,101],'Cost':[147,160]}
		if type(self) == CSVCreator:
			self.salesOrder = None
			self.__populateMaps()
			self.__createCSV()


	def __del__(self):
		"""
	This method runs when the object is destroyed.  It closes the file.
		"""
		if self.fid is not None:
			self.fid.close()
		if self.Cfid is not None:
			self.Cfid.close()

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

			if self.useSalesOrder:			
				self.__createCreditCSV()
				self.__createHeader(self.Cfid)


	def __getFilenameOut(self,filenameIn):
		"""
	This method runs when the object is initialized.  It defines the name
	of the output csv based off the incoming text file name
		"""		
		if filenameIn.find('.txt') != -1 :
			return filenameIn[:filenameIn.find('.txt')] + '.csv'
		return filenameIn

	def __createCreditCSV(self):
		"""
	Creates a csv only for the credits
		"""
		fOut = self.__getFilenameOut(self.fileIn)
		fOut = s.subStrByChar(fOut,'','/') + '/' + 'Credits-' + \
			s.subStrByChar(fOut,'/','.csv') + '.csv'
		self.Cfid = open(fOut,'w')

	def __isCSV(self):
		"""
	This method runs after the csv file has been named.  It checks to
	make sure the csv file was named properly
		"""		
		if self.fileOut.find('.csv') != -1 :
			return True
		return False


	def __createHeader(self,fid=None):
		"""
	This method runs after the csv has been verified.  It creates the header
	based off of the previously defined fields.
		"""
		if fid is None:
			fid = self.fid
		count = 0
		end = len(self.header)
		for field in self.header:
			if field == 'Item':
				self.__nextField(fid)
			fid.write(field)
			count += 1
			if count != end:
				self.__nextField(fid)
		self.__nextEntry(fid)

	def __populateMaps(self):
		"""
	Method reads map files and populates ivars.
		"""
		self.customerMap = f.MapReader('customerMap.txt').getMap()
		self.itemMap = f.MapReader('itemMap.txt').getMap()
		self.unitMap = f.MapReader('unitMap.txt').getMap()
		self.postingMap = f.MapReader('postingMap.txt').getMap()
		self.invoiceMap = f.MapReader('invoiceMap.txt').getMap()
		

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
				self.p_inv = self.salesOrder.invoice
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
		self.__writeCreditsFromSalesOrder()

	def closeCSV(self):
		"""
	Public method used to clear sales order.
		"""
		self.total = self.salesOrder.getTotal()
		self.__writeFromSalesOrder()

	def __writeCreditsFromSalesOrder(self):
		"""
	Iterates the Sales Order object and writes to Credit csv
		"""
		credits = self.salesOrder.getCredits()
		for textIn in credits:
			self.__setText(textIn)
			self.__setEntry(self.Cfid)

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


	def __setEntry(self,fid = None):
		"""
	This is method manages the data written to the csv file.  It saves the
	customer and item data to be used on other entries
		"""		
		self.printCustomer = True
		if fid is None:
			fid = self.fid
		count = 0
		end = len(self.header)
		self.__setCustomer(fid)
		self.__setItem()
		self.setRate()
		for field in self.header:
			if field != 'Sales Total':
				self.__setField(field,fid)
			elif field == 'Sales Total' and self.writeTotal:
				self.__setField(field,fid)
			count += 1
			if count != end:
				self.__nextField(fid)
		self.__nextEntry(fid)

	def __setField(self,field,fid=None):
		"""
	This method writes data to the csv file.  It pulls persistant data
	stored in the class for the fields it doesn't have.  It scrubs the data
	for each entry for formatting errors.  It takes an incoming field name
	pulled from the header list, finds the data from the text variable and
	writes to the csv.
		"""
		if field == 'Customer ID':
			if self.printCustomer:
				fieldVal = self.customerID
			else:
				fieldVal = ''
		elif field == 'Customer Name':
			if self.printCustomer:
				fieldVal = self.customer
			else:
				fieldVal = ''
		elif field == 'Item ID':
			fieldVal = self.itemID
		elif field == 'Item Description':
			fieldVal = self.item
		elif field == 'Rate':
			fieldVal = self.rate
		elif field == 'Sales Total':
			fieldVal = self.total
		elif field == 'Transaction Type':
			if self.isCredit():
				fieldVal = 'Credit'
			else:
				fieldVal = 'Sale'

		elif field == 'Undeposited Funds' or field == 'Subsidiary' or \
		field == 'Location'	or field == 'Payment Method' :
			if self.printCustomer:
				fieldVal = self.defaults[field]
			else:
				fieldVal = ''

		elif field == 'Tax Code' or field == 'Price Level' or \
		field == 'Cost Estimate':
			fieldVal = self.defaults[field]

		elif field == 'Customer':
			if self.printCustomer:
				fieldVal = self.__getCustomerID()
			else:
				fieldVal = ''
		elif field == 'Item':
			self.__nextField(fid)
			fieldVal = self.__getItemID()
		elif field == 'Units':
			fieldVal = self.__getUnits()
		elif field == 'Transaction Date':
			if self.printCustomer:
				fieldVal = self.iterText('Date')
			else:
				fieldVal = ''

		elif field == 'Posting Period':
			if self.printCustomer:
				fieldVal = self.__convertDateToPostingPeriod()
			else:
				fieldVal = ''

		elif field == 'Inv Open':
			invoice = self.iterText('Invoice')
			if self.__hasInvoice(invoice):
				fieldVal = 'True'
			else:
				fieldVal = ''

		elif field == 'Parent Inv':
			fieldVal = self.p_inv
		#elif field == 'Invoice':
		# 	if self.printCustomer:
		# 		fieldVal = self.iterText('Invoice')
		# 	else:
		# 		fieldVal = ''


		else:
			fieldVal = self.iterText(field)
		fieldVal = s.removeSpaces(fieldVal)
		fieldVal = s.removeCommas(fieldVal)
		if fid is None:
			fid = self.fid
		fid.write(fieldVal)


	def __nextField(self,fid = None):
		"""
	This method just adds a comma to the csv. It divides the two fields.
		"""
		if fid is None:
			fid = self.fid
		fid.write(',')


	def __nextEntry(self,fid=None):
		"""
	This method just writes a new line character to the csv.  It divides the
	two entries.
		"""
		if fid is None:
			fid = self.fid
		fid.write('\n')

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
		customerID = self.iterText('Customer ID')
		if customerID.find(' ') == -1:
			self.customerID = customerID
			return True
		return False

	def __setCustomer(self,fid = None):
		"""
	This method runs the hasCustomer method.  If the text variable has customer
	data, it sets the customer variables
		"""
		if fid is None:
			fid = self.fid
		if fid == self.fid:
			self.printCustomer = False
		if self.__hasCustomer():
			self.customer = self.iterText('Customer Name')
			self.printCustomer = True
		pass

	def __hasItem(self):
		"""
	This method is the same as the hasCustomer method, but checks the item data
	It returns a boolean.
		"""
		itemID = self.iterText('Item ID')
		if itemID.find('F') != -1 or itemID.find('G') != -1:
			self.itemID = itemID
			return True
		return False

	def __setItem(self):
		"""
	This method is the same as the setCustomer method, but sets the item data.
		"""
		if self.__hasItem():
			self.item = self.iterText('Item Description')
		pass


	def isCredit(self,textIn=None):
		"""
	This method checks the quantity field to make sure the transaction is
	a sale.  If not, it returns false.
		"""
		if textIn is None:
			if self.iterText('Quantity').find('-') >= 0:
				return True
		else:
			if self.iterText('Quantity',True,textIn).find('-') >= 0:
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
			quantity = float(s.removeMinus(s.removeCommas(\
				self.iterText('Quantity'))))
			price = float(s.removeMinus(s.removeCommas(self.iterText('Price'))))
			self.rate = str(round(price / quantity,self.SIG_FIGS))
		else:
			quantity = float(s.removeMinus(s.removeCommas(\
				self.iterText('Quantity',True,textIn))))
			price = float(s.removeMinus(s.removeCommas(\
				self.iterText('Price',True,textIn))))
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

	def __getCustomerID(self):
		"""
	Returns the Customer NetSuite ID
		"""
		customer = s.removeSpaces(self.customerID)
		return self.customerMap[customer]

	def __getItemID(self):
		"""
	Returns the Item NetSuite ID
		"""
		item = s.removeSpaces(self.itemID)
		return self.itemMap[item]

	def __hasInvoice(self,invoice):
		"""
	Returns boolean if invoice appears in Invoice Map
		"""
		invoice = s.removeSpaces(invoice)
		if self.invoiceMap.has_key(invoice):
			return True
		else:
			return False

	def __getUnits(self):
		"""
	Returns sale unit type
		"""
		item = s.removeSpaces(self.itemID)
		return self.unitMap[item]

	def __getPostingPeriod(self,key):
		"""
	Returns the posting period id
		"""
		return self.postingMap[key]

	def __convertDateToPostingPeriod(self):
		"""
	Converts the date of the transaction to the postion period id 
		"""
		date = s.removeSpaces(self.iterText('Date'))
		month = s.subStrByChar(date,'','/')
		date_w_no_month = s.subStrByChar(date+'*', '/','*')
		year = s.subStrByChar(date_w_no_month+'*','/','*')
		return self.__getPostingPeriod(month + '/' + year)

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
		self.invoice = ''

	def addEntry(self, textIn):
		"""
	Inputs text from the CSV Creator to the text list
		"""
		self.addToTotal(textIn)
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
			self.__setInvoice(textIn)
			price = float(s.removeCommas(self.iterText('Price',True,textIn)))
			self.total += price
		else:	
			price = float(s.removeCommas(s.removeMinus(self.iterText(\
				'Price',True,textIn))))
			self.total -= price


	def getEntries(self):
		"""
	Returns the stored entries in the object.
		"""
		self.__createCreditList()
		self.__removeCreditsFromEntries()
		return self.entries

	def getCredits(self):
		"""
	Returns the stored credits in the object.
		"""
		return self.credits


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

	def __setInvoice(self,textIn):
		"""
	Sets invoice
		"""
		self.invoice = s.removeSpaces(self.iterText('Invoice',True,textIn))
