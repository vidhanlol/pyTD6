import keyboard, mouse, json, pygetwindow, time, ctypes
from typing import Tuple
from exceptions import *

# required for the mouse.move to not be offset when display scaling is enabled.
user32 = ctypes.windll.user32
user32.SetProcessDPIAware()

# load json file with monkey information in it.
with open("monkeys.json") as monkeys_json:
    monkeys = json.load(monkeys_json)

with open("hotkeys.json") as hotkeys_json:
    hotkeys = json.load(hotkeys_json)

# Used to round price to the nearest 5.
def price_round(x, base=5):
    return base * round(x / base)


class monkey:
    def __init__(self, monkey: str):

        # initialize monkey's attributes.
        self.sold = False
        self.placed = False
        self.upgrades = [0, 0, 0]
        self.monkey_name = monkey

    # self.info(self.monkey_name)

    def place(self, coordinates: Tuple[int, int]):

        # raise CoordinateError if invalid type or tuple length.
        if (type(coordinates) is not list) and (type(coordinates) is not tuple):
            raise CoordinateError
        if len(coordinates) != 2:
            raise CoordinateError

        # raise MonkeyPlaced if the monkey has already been placed.
        if self.placed:
            raise MonkeyPlaced

        # activate Bloons TD 6 window.
        btd6_window = pygetwindow.getWindowsWithTitle("BloonsTD6")[0]
        btd6_window.activate()

        # move to the monkey's position
        # send the hotkey for the monkey
        # left click to place the monkey
        # time.sleep required for the monkey to be placed in time.
        previous_position = mouse.get_position()
        mouse.move(coordinates[0], coordinates[1])
        time.sleep(0.1)
        keyboard.send(hotkeys["Monkeys"][self.monkey_name])
        time.sleep(0.1)
        mouse.click()
        time.sleep(0.1)

        # record the coordinates of the monkey.
        self.coordinates = coordinates

        # record that the monkey has been placed.
        self.placed = True

    def upgrade(self, upgrades: Tuple[int, int, int] = None, skip_esc: bool = False):

        # if no upgrade path is passed, use the one provided when the monkey was generated.
        if upgrades is None:
            upgrades = self.upgrades

        # raise UpgradeError if invalid type or tuple length.
        if (type(upgrades) is not list) and (type(upgrades) is not tuple):
            raise UpgradeError
        if len(upgrades) != 3:
            raise UpgradeError

        # raise UpgradeError if all paths have tiers active.
        if upgrades.count(0) == 0:
            raise UpgradeError

        # raise UpgradeError there is a path above the 5th tier or below the base tier.
        if max(upgrades) > 5 or min(upgrades) < 0:
            raise UpgradeError

        # raise UpgradeError if there is more than one path at tier 3 or higher
        third_tier_upgrade_count = len([i for i in upgrades if i >= 3])
        if third_tier_upgrade_count > 1:
            raise UpgradeError

        # raise exceptions if the monkey hasn't been placed or has been already sold.
        if not self.placed:
            raise MonkeyNotPlaced
        if self.sold:
            raise MonkeySold

        # move to the monkey's position
        # send the hotkey for (current upgrade - previous upgrade)
        # send escape to get out of upgrade menu
        mouse.move(self.coordinates[0], self.coordinates[1])
        time.sleep(0.1)
        mouse.click()
        time.sleep(0.1)
        for path in range(len(upgrades)):
            for tier in range(upgrades[path] - self.upgrades[path]):
                keyboard.send(hotkeys["Monkeys"]["Upgrades"][path])
                time.sleep(0.1)
        if not skip_esc:
            keyboard.send("esc")
        time.sleep(0.1)

        # record the upgrades of the monkey.
        self.upgrades = upgrades

        # update information about tower
        # self.info(self.monkey_name)

    def sell(self):

        # raise exceptions if the monkey hasn't been placed or has been already sold.
        if not self.placed:
            raise MonkeyNotPlaced
        if self.sold:
            raise MonkeySold

        # move to the monkey's position
        # sell monkey
        mouse.move(self.coordinates[0], self.coordinates[1])
        time.sleep(0.1)
        mouse.click()
        time.sleep(0.1)
        keyboard.send(hotkeys["Gameplay"]["Pause/Deselect"])
        time.sleep(0.1)

        # record that the monkey has been sold.
        self.sold = True

    def info(self, monkey_name: str = None, upgrades: Tuple[int, int, int] = None):

        # raise UpgradeError if invalid type or tuple length.
        if (type(upgrades) is not list) and (type(upgrades) is not tuple):
            raise UpgradeError
        if len(upgrades) != 3:
            raise UpgradeError

        # raise UpgradeError if all paths have tiers active.
        if upgrades.count(0) == 0:
            raise UpgradeError

        # raise UpgradeError there is a path above the 5th tier or below the base tier.
        if max(upgrades) > 5 or min(upgrades) < 0:
            raise UpgradeError

        # raise UpgradeError if there is more than one path at tier 3 or higher
        third_tier_upgrade_count = len([i for i in upgrades if i >= 3])
        if third_tier_upgrade_count > 1:
            raise UpgradeError

        # if no upgrade path is passed, use the one provided when the monkey was generated.
        if upgrades == None:
            upgrades = self.upgrades

        # if no monkey name is passed, use the one provided when the monkey was generated.
        if monkey_name == None:
            monkey_name = self.monkey_name

        # get main path from the 3, represented by highest tier.
        main_tier = max(upgrades)
        main_path = upgrades.index(main_tier)

        # set basic monkey data
        self.monkey_name = monkey_name
        self.monkey_description = monkeys[monkey_name]["description"]

        # calculate monkey prices for different difficulties.
        self.monkey_price_medium = monkeys[monkey_name]["price"]
        self.monkey_price_easy = price_round(0.85 * self.monkey_price_medium)
        self.monkey_price_hard = price_round(1.08 * self.monkey_price_medium)
        self.monkey_price_impoppable = price_round(1.2 * self.monkey_price_medium)

        # reset upgrade info every time this method is called.
        self.upgrade_name = None
        self.upgrade_description = None

        self.upgrade_price_medium = 0
        self.upgrade_price_easy = 0
        self.upgrade_price_hard = 0
        self.upgrade_price_impoppable = 0

        # only run this if the monkey has been upgraded.
        if upgrades != [0, 0, 0]:

            # get basic upgrade data from monkeys.json
            self.upgrade_name = monkeys[monkey_name]["upgrades"][main_path][
                main_tier - 1
            ]["name"]
            self.upgrade_description = monkeys[monkey_name]["upgrades"][main_path][
                main_tier - 1
            ]["description"]

            # calculate upgrade prices for different difficulties.
            self.upgrade_price_medium = monkeys[monkey_name]["upgrades"][main_path][
                main_tier - 1
            ]["price"]
            self.upgrade_price_easy = price_round(0.85 * self.upgrade_price_medium)
            self.upgrade_price_hard = price_round(1.08 * self.upgrade_price_medium)
            self.upgrade_price_impoppable = price_round(1.2 * self.upgrade_price_medium)

        # calculate total prices for different difficulties.
        self.total_price_medium = self.monkey_price_medium
        for path in range(len(upgrades)):
            for tier in range(upgrades[path]):
                self.total_price_medium += monkeys[monkey_name]["upgrades"][path][tier][
                    "price"
                ]
        self.total_price_easy = price_round(0.85 * self.total_price_medium)
        self.total_price_hard = price_round(1.08 * self.total_price_medium)
        self.total_price_impoppable = price_round(1.2 * self.total_price_medium)


class hotkey:
    def play(self):
        keyboard.send(hotkeys["Gameplay"]["Play/Fast Forward"])

    def change_targeting(targeting: str = "First"):
        targeting_options = ["First", "Last", "Close", "Strong"]
        targeting_change = targeting_options.index(targeting) - 0
        for i in range(targeting_change):
            keyboard.send(hotkeys["Monkeys"]["Change Targeting"][1])

    def confirm():
        keyboard.send("enter")
        time.sleep(0.1)
