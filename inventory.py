import steammarket as sm
import numpy as np
import re
import shutil
import glob
import os
from time import sleep
from item import Item
from time import gmtime

def line(f):
	for _ in range(100): f.write("-")

def today():
	date = gmtime()
	return "{hour}_{minute}_{second}_{day}_{month}_{year}".format(day=date.tm_mday-1, month=date.tm_mon, year=date.tm_year, hour=date.tm_hour, minute=date.tm_min, second=date.tm_sec)

class Inventory:
	def __init__(self):
		self.stock = []
		self.readStorage()
		self.saveRawInventory()

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
		path = glob.glob("inventory/*")
		if path != []:
			previousInv = max(path, key=os.path.getctime)
			print("previous", previousInv)
			preData = np.genfromtxt(previousInv, delimiter=';', skip_header=1, skip_footer=6, dtype=None, encoding=None, autostrip=True, usecols = (0,1,2))
			p = self.getTotalProfit()
		else:
			preData = self.stock
			p = None
		if glob.glob("inventory.txt"):
			shutil.move("inventory.txt", "inventory/inventory_{}.txt".format(today()))
			print("archived inventory.txt to inventory directory")
		f = open("inventory.txt", "w")
		f.write("{name:{nameLen}};{num:>5};{price:>7};{total:>8} | {profit:>8};{totalP:>9}\n".format(name="Name",nameLen=nameLength, num="Num",price="Price",total="Total",profit="Profit",totalP="Total"))
		totalProfit = 0.0
		totalItems = 0
		for s in self.stock:
			new = True
			for d in preData:
				if s["name"] == d[0]:
						profit = self.profit(s, d)
						f.write("{:{}};{:5};{:6.2f}€;{:7.2f}€ | {:>+7}€;{:>+8}€\n".format(s["name"],nameLength,  s["num"], s["price"], np.round(s["num"] * s["price"], 2), profit, np.round(profit * s["num"], 2)))
						totalProfit += np.round(s["num"] * profit, 2)
						totalItems += s["num"]
						new = False
						break
			if new:
				f.write("{:{}};{:5};{:6.2f}€;{:7.2f}€ | new Item!\n".format(s["name"],nameLength,  s["num"], s["price"], np.round(s["num"] * s["price"], 2)))
				totalItems += s["num"]

		line(f)
		f.write("\n{:34}{:>9}\n".format("Total Items:", totalItems))
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
			return np.round(new["price"] - self.convertPrice(old[2]), 2)

	def getTotalProfit(self):
		oldInv = min(glob.glob("inventory/*"), key=os.path.getctime)
		print("old: ", oldInv)
		preData = np.genfromtxt(oldInv, delimiter=';', skip_header=1, max_rows=len(self.stock), dtype=None, encoding=None)
		totalProfit = 0.0
		for s in self.stock:
			new = True
			for d in preData:
				if s["name"] == d[0]:
					profit = self.profit(s, d)
					totalProfit += np.round(s["num"] * profit, 2)
					new = False
					break
			if new:
				totalProfit += np.round(s["num"] * s["price"])
		return "{:34}{:>+9.2f}€\n".format("Total Profit since beginning:", totalProfit)

	def convertPrice(sel, str):
		price = re.findall(r"[-+]?\d*\.\d+|\d+", str)
		if len(price) == 2:
			price = float(int(price[0]) + int(price[1]) / 100)
		else:
			price = np.round(float(price[0]), 2)
		return price

	def readStorage(self):
		global nameLength
		nameLength = 0
		storage = os.listdir("storage")
		for s in storage:
			s = "storage/" + s
			container = np.genfromtxt(s, delimiter=';', skip_header=1, dtype=str, max_rows=1)
			print(container)
			data = np.genfromtxt(s, delimiter=';', skip_header=2, dtype=None, encoding=None)
			if len(data.shape) == 0:
				data = np.array([data])
			for d in data:
				if len(d[1]) > nameLength:
					nameLength = len(d[1])
			for d in data:
				num = int(d[0])
				name = d[1]
				item = None
				while item == None:
					sleep(3.01)
					item = sm.get_csgo_item(name, currency='EUR')
					if item == None:
						print("retrying {} in 1s".format(name))
						sleep(1)
				if item["success"]:
					price = self.convertPrice(item["lowest_price"])
					print("{:{}} - lowest_price: {:7.2f}€".format(name, nameLength, price))
					self.add(Item(name, price, num))
				else:
					print("Error:", name)