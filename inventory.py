import steammarket as sm
import numpy as np
import re
import shutil
import glob
import os
from time import sleep
from item import Item
from time import gmtime


def today():
    date = gmtime()
    return "{hour}_{minute}_{second}_{day}_{month}_{year}".format(day=date.tm_mday - 1, month=date.tm_mon,
                                                                  year=date.tm_year, hour=date.tm_hour,
                                                                  minute=date.tm_min, second=date.tm_sec)


class Inventory:
    def __init__(self, window):
        self.stock = []
        self.baseInv = []
        self.nameLength = 1
        self.numLength = 1
        self.priceLength = 1
        self.lineLength = 1
        self.stop = False
        self.readStorage()
        self.window = window

    def add(self, item):
        if len(self.stock) > 0:
            for s in self.stock:
                if s["name"] == item["name"]:
                    s.setNum(s["num"] + item["num"])
                    return
            self.stock.append(item)
        else:
            self.stock.append(item)

    def addBase(self, item):
        if len(self.baseInv) > 0:
            for s in self.baseInv:
                if s["name"] == item["name"]:
                    s.setNum(s["num"] + item["num"])
                    s.setPrice(s["price"] + item["price"])
                    return
            self.baseInv.append(item)
        else:
            self.baseInv.append(item)

    def readStorage(self):
        storage = os.listdir("storage")
        for s in storage:
            s = "storage/" + s
            data = np.genfromtxt(s, delimiter=';', skip_header=1, dtype=None, encoding=None)
            if len(data.shape) == 0:
                data = np.array([data])
            for d in data:
                num = int(d[0])
                name = d[1]
                self.add(Item(name, 0.0, num))
                self.addBase(Item(name, float(d[2]) * num, num))
        self.updateLen()

    def getMarketPrice(self):
        i = 0
        for s in self.stock:
            # print(stop)  # TODO stop doesnt change
            item = None
            while item == None:
                item = sm.get_csgo_item(s["name"], currency='EUR')
                if item == None:
                    print("retrying {} in 3s".format(s["name"]))
                sleep(3.01)
                i += 1
            # self.window["-PROGRESS-"].update_bar(i) #TODO GUI as class and create in Inventory?
            if item["success"]:
                price = self.convertPrice(item["lowest_price"])
                print("{:{}} - lowest_price: {:7.2f}€".format(s["name"], self.nameLength, price))
                s["price"] = price
            if self.stop:
                return

    def terminate(self):
        self.stop = True

    def saveBaseInv(self):
        total = 0.0
        for s in self.baseInv:
            total += s["price"]
        f = open("inventory/inventory.txt", "w")
        f.write("{}\n".format(np.round(total, 2)))
        f.write("{name:{nameLen}};{num:>{numLen}};{price:>{priceLen}}\n".format(name="Name", nameLen=self.nameLength,
                                                                                num="Num", price="Price",
                                                                                numLen=self.numLength,
                                                                                priceLen=self.priceLength))
        for s in self.baseInv:
            f.write("{name:<{nameLen}};{num:>{numLen}};{price:>{priceLen}.2f}€\n".format(name=s["name"],
                                                                                         nameLen=self.nameLength,
                                                                                         num=s["num"],
                                                                                         numLen=self.numLength,
                                                                                         price=s["price"],
                                                                                         priceLen=self.priceLength - 1))

    def getNameLen(self):
        for s in self.baseInv:
            if len(str(s["name"])) > self.nameLength:
                self.nameLength = len(str(s["name"]))

    def getNumLen(self):
        for s in self.baseInv:
            if len(str(s["num"])) > self.numLength:
                self.numLength = len(str(s["num"]))

    def getPriceLen(self):
        for s in self.baseInv:
            if len(str(s["price"])) > self.priceLength:
                self.priceLength = len(str(s["price"]))
        self.priceLength += 2

    def updateLen(self):
        self.getNameLen()
        self.getNumLen()
        self.getPriceLen()
        self.lineLength = self.priceLength * 4 + self.numLength + self.nameLength + 8

    def __str__(self):
        return str(self.stock)

    def getTotalValue(self):
        value = 0
        for s in self.stock:
            value += (s["num"] * s["price"])
        return np.round(value, 2)

    def getSaleValue(self):
        value = 0
        for s in self.stock:
            value += (s["num"] * np.round(s["price"] / 1.15, 2))
        return np.round(value, 2)

    def saveRawInventory(self):
        path = glob.glob("inventory/*")
        preData = self.stock
        first = False
        p = 0.00
        if glob.glob("inventory.txt"):
            preData = np.genfromtxt("inventory.txt", delimiter=';', skip_header=1, skip_footer=6, dtype=None,
                                    encoding=None, autostrip=True, usecols=(0, 1, 2))
            first = True
            p = self.getTotalProfit(self.getTotalValue())
            shutil.move("inventory.txt", "inventory/inventory_{}.txt".format(today()))
            print("archived inventory.txt to inventory directory")
        f = open("inventory.txt", "w")
        f.write(
            "{name:{nameLen}};{num:>{numLen}};{price:>{priceLen}};{total:>{priceLen}} | {profit:>{priceLen}};{totalP:>{priceLen}}\n".format(
                name="Name", nameLen=self.nameLength, num="Num", price="Price", total="Total", profit="Profit",
                totalP="Total", numLen=self.numLength, priceLen=self.priceLength))
        totalProfit = 0.0
        totalItems = 0
        for s in self.stock:
            new = True
            if first:
                for d in preData:
                    if s["name"] == d[0]:
                        profit = self.profit(s, d)
                        f.write(
                            "{:{}};{:{numLen}};{:{priceLen}.2f}€;{:{priceLen}.2f}€ | {:>+{priceLen}}€;{:>+{priceLen}}€\n".format(
                                s["name"], self.nameLength, s["num"], s["price"], np.round(s["num"] * s["price"], 2),
                                profit, np.round(profit * s["num"], 2), numLen=self.numLength,
                                priceLen=self.priceLength - 1))
                        totalProfit += np.round(s["num"] * profit, 2)
                        totalItems += s["num"]
                        new = False
                        break
            if new:
                f.write("{:{}};{:5};{:6.2f}€;{:7.2f}€ | new Item!\n".format(s["name"], self.nameLength, s["num"],
                                                                            s["price"],
                                                                            np.round(s["num"] * s["price"], 2)))
                totalItems += s["num"]

        self.line(f)
        f.write("\n{:34}{:>9}\n".format("Total Items:", totalItems))
        f.write("{:34}{:>9.2f}\n".format("Total value:", self.getTotalValue()))
        f.write("{:34}{:>9.2f}\n".format("Total Sale value (approx.):", self.getSaleValue()))
        f.write("\n{:34}{:>+9.2f}€\n".format("Total Profit since the last time:", totalProfit))
        f.write("{:34}{:>+9.2f}€\n".format("Total Profit since beginning:", p))
        f.close()

    def profit(self, new, old):
        if type(old) == type(new):
            return np.round(new["price"] - old["price"], 2)
        else:
            return np.round(new["price"] - self.convertPrice(old[2]), 2)

    def getTotalProfit(self, currentValue):
        preData = np.genfromtxt("inventory/inventory.txt", delimiter=';', dtype=float, max_rows=1)
        totalProfit = currentValue - preData
        return totalProfit

    def convertPrice(self, str):
        price = re.findall(r"[-+]?\d*\.\d+|\d+", str)
        if len(price) == 2:
            price = float(int(price[0]) + int(price[1]) / 100)
        else:
            price = np.round(float(price[0]), 2)
        return price

    def line(self, f):
        for _ in range(self.lineLength): f.write("-")
