import webbrowser
import os
import base64
from numpy import genfromtxt

import PySimpleGUI as sg


def addItem(file, name, num, price):
    data = genfromtxt(file, skip_header=1 , delimiter=';', dtype=None, encoding=None)
    f = open(file, "w")
    f.write("{};{};{}".format("num", "name", "buyprice"))
    for d in data:
        if d[1] == name and d[2] == price:
            f.write("\n{};{};{}".format(int(num) + d[0], name, price))
        else:
            f.write("\n{};{};{}".format(d[0], d[1], d[2]))
    f.close()


def getItemAmount(classid, json_data):
    inventory = json_data["rgInventory"]
    count = 0
    for item in inventory:
        if inventory[item]["classid"] == classid:
            count += 1
    return count


def icon(f):
    with open(f, "rb") as f:
        icon = base64.b64encode(f.read())
    return icon


def updateStock():
    with open("inventory.txt", "r") as f:
        stock = f.read()
    stock = stock.split("\n")
    return stock


def askSteamMarket(inv, window):
    inv.getMarketPrice()
    inv.saveBaseInv()
    inv.saveRawInventory()
    window["Stock"].update(updateStock())


def openExternalLink(url):
    webbrowser.open(url, new=0, autoraise=True)


def confirmLink(link):
    layout = [
        [
            sg.Text("!!!Your being redirected to this URL!!!", )
        ],
        [
            sg.Text(link, justification="center")
        ],
        [
            sg.Text("Please confirm", justification="center")
        ],
        [
            sg.Button("Ok"),
            sg.Button("No")
        ]
    ]
    window = sg.Window("Redirecting to URL", layout, modal=True, element_justification="center")
    while True:
        event, values = window.read()
        if event == "Exit" or event == sg.WIN_CLOSED:
            break
        if event == "Ok":
            openExternalLink(link)
            break
        if event == "No":
            break
    window.close()


def getSteamIDs():
    ids = "steamid.txt"
    if not os.path.exists(ids):
        f = open(ids, "w")
        f.close()
    return genfromtxt(ids, dtype=str).tolist(), ids
