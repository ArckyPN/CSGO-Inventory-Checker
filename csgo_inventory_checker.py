import os
from inventory import Inventory

def main():
	os.makedirs("inventory", exist_ok=True)
	inv = Inventory()
	inv.getMarketPrice()
	inv.saveBaseInv()
	inv.saveRawInventory()
	with open("inventory.txt", "r") as f:
		print(f.read())

if __name__ == '__main__':
	main()