from tools import *
from threading import Thread
from numpy import genfromtxt
from numpy import array
from glob import glob
from requests import get
from json import loads
from os import remove as fileRemove


def run(inv, window):       #TODO integrate progress bar
    Thread(target=askSteamMarket, args=(inv, window)).start()
    # Thread(target=progress, args=(window, stock)).start()


def add(unit, window, values, inv):
    if unit == []:
        window["-OUTPUT-"].update("Error: Please choose a Storage Unit before adding a new Item")
        return
    try:
        name = str(values["-Name-"])    #TODO check if name is actual item?
    except:
        window["-OUTPUT-"].update("Error: Name must a String")
        return
    try:
        num = int(values["-Num-"])
    except:
        window["-OUTPUT-"].update("Error: Num must a Integer")
        return
    try:
        price = float(values["-Buy Price-"])
    except:
        window["-OUTPUT-"].update("Error: Price must a Float")
        return
    addItem(unit, values["-Name-"], values["-Num-"], values["-Buy Price-"])
    window["-OUTPUT-"].update("Added {num} {name} with {price} to {unit}".format(num=num, name=name, price=price, unit=unit))
    show(values, window, inv)


def remove(values, window, inv):
    unit = values["-SU-"]
    data = genfromtxt(unit, delimiter=";", skip_header=1, dtype=None, encoding=None, autostrip=True)
    if len(data.shape) == 0:
        data = array([data])
    for d in data:
        if str(d[1]) == values["-Name-"] and float(d[2]) == float(values["-Buy Price-"]):
            if int(d[0]) <= int(values["-Num-"]):
                d[0] = 0
            else:
                d[0] = int(d[0]) - int(values["-Num-"])
    window["-OUTPUT-"].update("Removed {num} {name} with {price} from {unit}".format(num=values["-Num-"], name=values["-Name-"], price=values["-Buy Price-"], unit=unit))
    with open(unit, "w") as f:
        f.write("num;name;buyprice")
        for d in data:
            if d[0] == 0: continue
            f.write("\n{};{};{}".format(d[0], d[1], d[2]))
    show(values, window, inv)


def show(values, window, inv):
    unit = values["-SU-"]
    if len(genfromtxt(unit, delimiter=";", dtype=None, encoding=None, autostrip=True)) == 1:
        window["-OUTPUT-"].update("Error: chosen Storage Unit is empty")
        out = ["{:<{}};{:>{}};{:>{}}".format("Name", inv.nameLength, "Num", inv.numLength, "Buy Price",
                                             inv.priceLength + 1)]
        window["-Unit-"].update(out)
        return unit
    data = genfromtxt(unit, delimiter=";", skip_header=1, dtype=None, encoding=None, autostrip=True)
    if len(data.shape) == 0:
        data = array([data])
    out = ["{:<{}};{:>{}};{:>{}}".format("Name", inv.nameLength, "Num", inv.numLength, "Buy Price", inv.priceLength + 1)]
    for d in data:
        out.append("{:<{}};{:>{}};{:>{}}".format(d[1], inv.nameLength, d[0], inv.numLength, d[2], inv.priceLength + 1))
    window["-OUTPUT-"].update("")
    window["-Unit-"].update(out)
    return unit


def addSU(window, pathLen, values):
    unitName = "{:03}{}.csv".format(pathLen + 1, values["newUnit"])
    newUnit = "storage/{}".format(unitName)
    f = open(newUnit, "w")
    f.write("num;item;buyprice\n")
    f.close()
    path = glob("storage/*")
    window["-SU-"].update(values=path, value="Choose Storage Unit")
    window["-SU_LIST-"].update(values=path)
    window["-OUTPUT_SU-"].update("Added new Storage Unit {} to disk.".format(unitName))


def removeSU(values, window):
    unit = values["-SU_LIST-"]
    if not unit:
        window["-OUTPUT_SU-"].update("Error: to remove a Storage Unit please choose one from above!")
        return
    else:
        unit = unit[0]
    fileRemove(unit)
    window["-OUTPUT_SU-"].update("Removed Storage Unit {} from disk.".format(unit))
    path = glob("storage/*")
    window["-SU_LIST-"].update(values=path)


def getInv(window, values):         #TODO ignore untradable items (or list sperately), requests prices
    if values["-STEAMID-"] != "new SteamID":
        steamid = values["-STEAMID-"]
        ids = "steamid.txt"
        data = genfromtxt(ids, dtype=str)
        if len(data.shape) == 0:
            data = array([data])
        if steamid not in data:
            with open(ids, "a+") as f:
                f.write("{}\n".format(steamid))
    else:
        steamid = values["SteamID"]
    data = get("https://steamcommunity.com/id/{}/inventory/json/730/2".format(steamid))
    data = loads(data.text)
    descriptions = data["rgDescriptions"]
    window["-INV-"].update(
        [(descriptions[item]["name"], getItemAmount(descriptions[item]["classid"], data)) for item in descriptions])


def updateInput(values, window):
    temp = values["-Unit-"][0].replace(";", " ").split()
    length = len(temp)
    price = temp[length - 1]
    num = temp[length - 2]
    name = temp[0]
    for i in range(1, length - 2):
        name += " " + temp[i]
    window["-Name-"].update(name)
    window["-Num-"].update(num)
    window["-Buy Price-"].update(price)