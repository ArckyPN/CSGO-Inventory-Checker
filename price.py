import steammarket as sm
import numpy as np
import re
import shutil
import glob
from os import listdir
import os
from time import sleep
from time import gmtime

# item = sm.get_csgo_item('Glove Case', currency='EUR')
# print(type(item))
# print(item)
# price = re.findall(r"[-+]?\d*\.\d+|\d+", item["lowest_price"])
# if len(price) == 2:
# 	price = float(int(price[0]) + int(price[1]) / 100)
# else:
# 	price = np.round(float(price[0]), 2)
# print(price)
# negative = -5.23
# print(str(negative))
# positive = 4.67
# positive = "+" + str(positive)
# print(positive)
# nul = 0
# print(str(nul))
# print("{:>+9.2}".format(5.4))
# print("{:>+9.2}".format(-5.4))
# print("{:>+9.2}".format(0.0))
# if type(item) == <class 'dict'>:
# 	print("hurray")
# exit()

def today():
	date = gmtime()
	return "{hour}_{minute}_{second}_{day}_{month}_{year}".format(day=date.tm_mday-1, month=date.tm_mon, year=date.tm_year, hour=date.tm_hour, minute=date.tm_min, second=date.tm_sec)

def convertPrice(str):
	price = re.findall(r"[-+]?\d*\.\d+|\d+", str)
	if len(price) == 2:
		price = float(int(price[0]) + int(price[1]) / 100)
	else:
		price = np.round(float(price[0]), 2)
	return price

def readStorage(inv):
	storage = listdir("storage")
	for s in storage:
		s = "storage/" + s
		container = np.genfromtxt(s, delimiter=';', skip_header=1, dtype=str, max_rows=1)
		print(container)
		data = np.genfromtxt(s, delimiter=';', skip_header=2, dtype=None, encoding=None)
		if len(data.shape) == 0:
			data = np.array([data])
		for d in data:
			num = int(d[0])
			name = d[1]
			item = None
			while item == None:
				item = sm.get_csgo_item(name, currency='EUR')
				if item == None:
					print("retrying {} in 1s".format(name))
					sleep(1)
			if item["success"]:
				price = convertPrice(item["lowest_price"])
				print("{:20} - lowest_price: {:7.2f}€".format(name, price))
				inv.add(Item(name, price, num))
			else:
				print("Error:", name)
		print("\n")

class Item:
	def __init__(self, name, price, num):
		self.item = {
			"name" 	: name,
			"price" : price,
			"num" 	: num
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

class Inventory:
	def __init__(self):
		self.stock = []

	def add(self, item):
		if len(self.stock) > 0:
			for s in self.stock:
				if s["name"] == item["name"]:
					s.setNum(s["num"] + item["num"])
					return
			self.stock.append(item)
		else:
			self.stock.append(item)

	def __str__(self):
		return str(self.stock)

	def getTotalValue(self):
		value = 0
		for s in self.stock:
			value += (s["num"] * s["price"])
		return "{:34}{:>9.2f}€\n".format("Total value:", np.round(value, 2))

	def getSaleValue(self):
		value = 0
		for s in self.stock:
			value += (s["num"] * np.round(s["price"] / 1.15, 2))
		return "{:34}{:>9.2f}€\n".format("Total Sale value (approx.):", np.round(value, 2))

	def saveRawInventory(self):
		if glob.glob("inventory/*") != []:
			previousInv = max(glob.glob("inventory/*"), key=os.path.getctime)
			print("previous", previousInv)
			preData = np.genfromtxt(previousInv, delimiter=';', skip_header=1, max_rows=len(self.stock), dtype=None, encoding=None)
			p = self.getTotalProfit()
		else:
			preData = self.stock
			p = None
		if glob.glob("inventory.txt"):
			shutil.move("inventory.txt", "inventory/inventory_{}.txt".format(today()))
			print("archived inventory.txt to inventory directory")
		f = open("inventory.txt", "w")
		f.write("{:20};{:>5};{:>7};{:>8} | {:>8};{:>9}\n".format("Name","Num","Price","Total","Profit","Total"))
		totalProfit = 0.0
		for s, d in zip(self.stock, preData):
			profit = self.profit(s, d)
			f.write("{:20};{:5};{:6.2f}€;{:7.2f}€ | {:>+7}€;{:>+8}€\n".format(s["name"], s["num"], s["price"], np.round(s["num"] * s["price"], 2), profit, np.round(profit * s["num"], 2)))
			totalProfit += np.round(s["num"] * profit, 2)
		if totalProfit > 0: prefix = "+"
		f.write(self.getTotalValue())
		f.write(self.getSaleValue())
		f.write("\n{:34}{:>+9.2f}€\n".format("Total Profit since the last time:",totalProfit))
		if p != None:
			f.write(p)
		f.close()

	def profit(self, new, old):
		if type(old) == type(new):
			return np.round(new["price"] - old["price"], 2)
		else:
			return np.round(new["price"] - convertPrice(old[2]), 2)

	def getTotalProfit(self):
		oldInv = min(glob.glob("inventory/*"), key=os.path.getctime)
		print("old: ", oldInv)
		preData = np.genfromtxt(oldInv, delimiter=';', skip_header=1, max_rows=len(self.stock), dtype=None, encoding=None)
		totalProfit = 0.0
		prefix = ""
		for s, d in zip(self.stock, preData):
			profit = self.profit(s, d)
			totalProfit += np.round(s["num"] * profit, 2)
		return "{:34}{:>+9.2f}€\n".format("Total Profit since beginning:", totalProfit)

def main():
	inv = Inventory()
	readStorage(inv)
	print(inv.getTotalValue())
	print(inv.getSaleValue())
	inv.saveRawInventory()

if __name__ == '__main__':
	main()