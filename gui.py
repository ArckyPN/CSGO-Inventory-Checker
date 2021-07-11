from inventory import Inventory
from events import *
from time import sleep
import glob


def progress(window, stock):
    i = 0
    for _ in range(len(stock)):
        sleep(3)
        i += 1
        print(i)
        window["-PROGRESS-"].update(i)


def main():
    path = glob.glob("storage/*")
    pathLen = len(path)
    stock = updateStock()
    unit = []
    sg.theme("dark")
    sg.SetOptions(font="courier", icon=icon("icon.ico"))
    window = sg.Window("Inventory Checker", [[]])
    inv = Inventory(window)
    steamIDs, _ = getSteamIDs()
    add_item_tab = [
        [
            sg.Button("Add Item", key="-ADDITEM-"),
            sg.Button("Remove Item", key="-REMOVEITEM-")
        ],
        [
            sg.Combo(path, default_value="Choose Storage Unit", key="-SU-", enable_events=True,
                     size=(len(max(path, key=len)), 1))
        ],
        [
            sg.Input(size=(inv.nameLength, 1), enable_events=True, key="-Name-", default_text="Name"),
            sg.Input(size=(4, 1), enable_events=True, key="-Num-", default_text="Num", justification="r"),
            sg.Input(size=(7, 1), enable_events=True, key="-Buy Price-", default_text="Price", justification="r")
        ],
        [
            sg.Text("", key="-OUTPUT-", size=(50, 1))
        ],
        [  # TODO deselect entry to allow changing input
            sg.Listbox(values=[], enable_events=True, size=(inv.numLength + inv.nameLength + 3 + inv.priceLength, 20),
                       key="-Unit-")
        ]
    ]
    add_unit_tab = [
        [sg.Input(size=(20, 1), key="newUnit", default_text="new storage unit",
                  tooltip="only the name, no file type or index")],
        [
            sg.Button("Add Storage Unit", key="-ADDSU-"),
            sg.Button("Remove Storage Unit", key="-REMOVESU-")
        ],
        [sg.Listbox(values=path, size=(len(max(path, key=len)), 15), key="-SU_LIST-")],
        [sg.Text("", key="-OUTPUT_SU-", size=(50, 1))]
    ]
    run_tab = [
        [sg.Button("Run", key="runButton")],
        [sg.ProgressBar(len(stock), orientation="h", size=(45, 15), key="-PROGRESS-", bar_color=("Green", "Black"),
                        visible=True)],
        [sg.Text("All Items")],
        [sg.Listbox(values=[], enable_events=True, size=(50, 20), key="-Storage-")]
    ]
    main_layout = [
        [
            sg.Text("Welcome")  # TODO add some info
        ],
        [
            sg.Button("Steam", key="-STEAM-"),
            sg.Button("YouTube", key="-YOUTUBE-"),
            sg.Button("Donate", key="-DONATE-"),
            sg.Button("GitHub", key="-GITHUB-"),
            sg.Button("Video - TODO", key="-VIDEO-")
        ]
    ]
    storage_layout = [
        [
            sg.Listbox(values=stock, key="Stock", size=(inv.numLength + inv.nameLength + inv.priceLength * 4 + 7, 27))
        ]
    ]
    inventory_layout = [
        [
            sg.Text("Input a new SteamID to [Request] its inventory or choose from a previously used SteamID")
        ],
        [
            # sg.Input(size=(20, 1), key="-STEAMID-", default_text="new SteamID", tooltip="Add a new SteamID"),
            # sg.Combo(steamIDs, size=(len(max(steamIDs, key=len)), 1), default_value="SteamID",
            #          tooltip="Choose a SteamID", key="SteamID"),
            sg.Combo(values=steamIDs, enable_events=True, bind_return_key=True, key="-STEAMCOMBO-", size=(len(max(steamIDs, key=len)), min(5, len(steamIDs)))),
            sg.Button("Request", key="-GETINV-")
        ],
        [
            sg.Listbox(values=[], size=(75, 25), key="-INV-")
        ]
    ]
    layout = [[sg.Titlebar(title="Weazel LOL", icon=icon("icon.ico"), text_color="red", background_color="green", font="avengeance")],[sg.TabGroup([[sg.Tab("Main", main_layout),
                             sg.Tab("Item", add_item_tab),
                             sg.Tab("Storage Unit", add_unit_tab),
                             sg.Tab("Run", run_tab),
                             sg.Tab("Storage", storage_layout),
                             sg.Tab("Inventory", inventory_layout)]])]]
    window = sg.Window("Inventory Checker", layout)

    while True:
        event, values = window.read()
        if event == "Exit" or event == sg.WIN_CLOSED:
            # TODO kill all Threads, global variable stop, set here to True
            inv.terminate()
            print("Killing all Threads!")
            break
        if event == "runButton":
            run(inv, window)
        if event == "-ADDITEM-":
            add(unit, window, values, inv)
        if event == "-REMOVEITEM-":
            remove(values, window, inv)
        if event == "-SU-":
            unit = show(values, window, inv)
            if not unit:
                continue
        if event == "-ADDSU-":
            addSU(window, pathLen, values)
        if event == "-REMOVESU-":
            removeSU(values, window)
        if event == "-GETINV-":
            getInv(window, values)
        if event == "-STEAM-":
            confirmLink("https://steamcommunity.com/profiles/76561198077815167")
        if event == "-YOUTUBE-":
            confirmLink("https://www.youtube.com/channel/UCbT0tvbLXZOGtsgg6_vsUrQ")
        if event == "-GITHUB-":
            confirmLink("https://github.com/ArckyPN/CSGO-Inventory-Checker")
        if event == "-DONATE-":
            confirmLink("https://streamlabs.com/archsyker/tip")
        if values["-Unit-"]:
            updateInput(values, window)
        if event == "-STEAMCOMBO-":
            continue
    window.close()


if __name__ == '__main__':
    main()

# TODO image_data = base64_image => image as button
