class Item:
	def __init__(self, name, price, num):
		self.item = {
			"name" 	: name,
			"price" : price,
			"num" 	: num,
		}

	def __str__(self):
		return "(" + str(self.item["name"]) + ", " + str(self.item["price"]) + "€, " + str(self.item["num"]) + ")"

	def __repr__(self):
		return self.__str__()

	def __getitem__(self, key):
		return self.item[key]
	
	def getName(self):
		return self.__getitem__("name")

	def getPrice(self):
		return self.__getitem__("price")

	def getNum(self):
		return self.__getitem__("num")

	def __setitem__(self, key, value):
		self.item[key] = value

	def setName(self, value):
		self.__setitem__("name", value)

	def setPrice(self, value):
		self.__setitem__("price", value)

	def setNum(self, value):
		self.__setitem__("num", value)