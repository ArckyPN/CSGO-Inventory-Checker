import os
from time import gmtime
from item import Item
from inventory import Inventory

def line(f):
	for _ in range(100): f.write("-")

def today():
	date = gmtime()
	return "{hour}_{minute}_{second}_{day}_{month}_{year}".format(day=date.tm_mday-1, month=date.tm_mon, year=date.tm_year, hour=date.tm_hour, minute=date.tm_min, second=date.tm_sec)

def main():
	os.makedirs("inventory", exist_ok=True)
	inv = Inventory()
	with open("inventory.txt", "r") as f:
		print(f.read())

if __name__ == '__main__':
	main()