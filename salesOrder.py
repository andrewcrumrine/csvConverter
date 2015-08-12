"""
	salesOrder.py

	Sales Order Class
	-----------------

	Builds up a sales order from a series of strings.  Modifies the strings
	to output a sum total then outputs the string line by line.

"""

from csvConverter import CSVCreator

class SalesOrder(CSVCreator):
	"""
		Builds a sales order from a series of itemized lines inputed from the 
	CSVCreator object.  The intent of the class is to output a sum total.
	"""
	def __init__(self,textIn):
		"""
	Input the first line into the text list.
		"""
		self.text = [textIn]
		self.header, self.indicies = self.getHeaderAndIndicies()