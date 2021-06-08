# CSGO-Inventory-Checker

Keep track of your CSGO Inventory value (semi-automatically).

## Requiements

- python3 `sudo apt install python3-pip`
- steammarket module `pip3 install steammarket`
- numpy module `pip3 install numpy`
	
## How to use

1. clone this repository to your directory of choice
	- `git clone https://github.com/ArckyPN/CSGO-Inventory-Checker.git`
2. create a directory named `storage`
	- `mkdir storage`
3. inside `storage` create as many .csv file as you like containing your items
	- personally, I have one file for every Storage Unit (SU)
4. .csv must have following structure
	- Line 1 and 2 doesn't matter (I have a help in line 1: `num;name` and line 2 is the name of the SU)
	- after that every line contains one item as stated above:
		- `num;name` for example:
		- 34;Prisma 2 Cases (meaning this peticular SU contains 24 Prisma 2 Cases)
		- 1;Sticker | Renegades (Foil) | Cologne 2015 (additionally 1 of this Sticker ^^)
		- and so on for every item
		- Note: the Item names has to the precise ones as they are listed on the Community Market
5. open a terminal inside this directory or navigate to this directory
6. run the .py file
	- `python3 csgo_inventory_checker.py`
7. the results will be printed to stdout of your terminal and also saved to `inventory.txt`
8. after the first use existing `inventory.txt` will be moved to a new `inventory` directory with present timestamp