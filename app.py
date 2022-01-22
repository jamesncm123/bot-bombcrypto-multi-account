from configparser import ConfigParser
from PIL import ImageGrab
import os
import time
import win32api
import win32con
import logging
import asyncio
import requests


class MyBot():
    def __init__(self) -> None:
        logging.basicConfig(format='%(asctime)s %(message)s',
                            datefmt='%m/%d/%Y %I:%M:%S %p', filename='app.log', level=logging.INFO,)
        self.configObject = ConfigParser()
        self.configObject.read("config.ini")
        self.grab = ImageGrab
        self.mainPath = os.path.dirname(__file__)
        self.pathPhoto = os.path.join(self.mainPath, "photo")
        self.box = ()
        self.start_time = 0
        self.token_notify = self.configObject["LINE_NOTIFY"]["TOKEN"]
        self.posImageLeftTopX = int(
            self.configObject["IMAGE_POSITION"]["LEFT_TOP_X"])
        self.posImageLeftTopY = int(
            self.configObject["IMAGE_POSITION"]["LEFT_TOP_Y"])
        self.posImageRightButtomX = int(
            self.configObject["IMAGE_POSITION"]["RIGHT_BUTTOM_X"])
        self.posImageRightButtomY = int(
            self.configObject["IMAGE_POSITION"]["RIGHT_BUTTOM_Y"])

        self.screenUnit = int(
            self.configObject["SCREEN"]["SCREEN_UNIT"])
        self.positions = []
        for i in range(self.screenUnit):
            position = "POSITION_"+str(i+1)
            if position in self.configObject:
                bodyPosition = {
                    "index": i,
                    "posWallet": (int(self.configObject[position]["WALLET_X"]), int(
                        self.configObject[position]["WALLET_Y"])),
                    "posReset": (int(self.configObject[position]["RESET_X"]), int(
                        self.configObject[position]["RESET_Y"])),
                    "posAll": (int(self.configObject[position]["ALL_X"]), int(
                        self.configObject[position]["ALL_Y"])),
                    "posExitHeroes": (int(self.configObject[position]["EXIT_HEROES_X"]), int(
                        self.configObject[position]["EXIT_HEROES_Y"])),
                    "posTreasureHunt": (int(self.configObject[position]["TREASUREHUNT_X"]), int(
                        self.configObject[position]["TREASUREHUNT_Y"])),
                    "posExitWallet": (int(self.configObject[position]["EXIT_WALLET_X"]), int(
                        self.configObject[position]["EXIT_WALLET_Y"])),
                    "posPauseAndSelectHeroes": (int(self.configObject[position]["PAUSE_AND_SELECT_HEROES_X"]), int(
                        self.configObject[position]["PAUSE_AND_SELECT_HEROES_Y"])),
                    "delayLoopSwapPage": 60 *
                    int(self.configObject[position]
                        ["DELAY_LOOP_SWAP_PAGE"]),
                    "delayLoopRefreshStamina": 60 *
                    int(self.configObject[position]
                        ["DELAY_LOOP_REFRESH_STAMINA"]),
                    "timeLoopSwap": 0,
                    "timeLoopRefresh": 0
                }
                self.positions.append(bodyPosition)
        self.loop = asyncio.get_event_loop()

    def capture_screen(self):
        try:
            self.box = (self.posImageLeftTopX, self.posImageLeftTopY,
                        self.posImageRightButtomX, self.posImageRightButtomY)
            img = self.grab.grab(self.box)
            img.save("picture.jpg")
            print("capture screen success")
        except:
            print('capture screen error')

    def mouseClick(self, cord):
        win32api.SetCursorPos((cord[0], cord[1]))
        time.sleep(2)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0)
        time.sleep(0.2)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0)

    def loopSwapPage(self, position):
        now = int(time.time() * 1000)
        if self.start_time > 0 and self.start_time > 0 \
                and now - position["timeLoopSwap"] > position["delayLoopSwapPage"] * 1000:
            logging.info("Loop Swap Page Start")
            self.positions[position["index"]]["timeLoopSwap"] = int(
                time.time() * 1000)
            print("Screen "+str(position["index"]+1)+", Loop Swap Page Start")
            self.mouseClick(position["posWallet"])
            self.capture_screen()
            time.sleep(3)
            self.linenotify("Screen "+str(position["index"]+1) +
                            ", Loop swap page Working")
            time.sleep(1)
            self.mouseClick(position["posExitWallet"])
            self.mouseClick(position["posExitWallet"])
            logging.info(
                "Loop Swap Page Stop Pending"+str(position["delayLoopSwapPage"])+" Second")

    def loopRefreshStamina(self, position):
        now = int(time.time() * 1000)
        if self.start_time > 0 and now - position["timeLoopRefresh"] > position["delayLoopRefreshStamina"] * 1000:
            self.positions[position["index"]]["timeLoopRefresh"] = int(
                time.time() * 1000)
            logging.info("Loop Refresh Stamina Start")
            print("Loop Refresh Stamina Start")
            self.mouseClick(position["posPauseAndSelectHeroes"])
            logging.info("Select Button Pause Game")
            self.mouseClick(position["posPauseAndSelectHeroes"])
            logging.info("Select Button Heroes")
            time.sleep(3)
            self.mouseClick(position["posReset"])
            logging.info("Select Button Reset")
            self.mouseClick(position["posAll"])
            self.capture_screen()
            time.sleep(3)
            self.linenotify("Screen "+str(position["index"]+1) +
                            ", Loop refresh stamina working")
            logging.info("Select Button All")
            self.mouseClick(position["posExitHeroes"])
            logging.info("Go to Game")
            self.mouseClick(position["posTreasureHunt"])
            logging.info(
                "Loop Refresh Stamina Stop Pending " + str(position["delayLoopRefreshStamina"])+" Second")

    def linenotify(self, message):
        try:
            url = 'https://notify-api.line.me/api/notify'
            token = self.token_notify  # Line Notify Token
            # Local picture File
            img = {'imageFile': open('picture.jpg', 'rb')}
            data = {'message': message}
            headers = {'Authorization': 'Bearer ' + token}
            session = requests.Session()
            session_post = session.post(
                url, headers=headers, files=img, data=data)
            print("send line notify success")
            print("session_post")
        except:
            print("send line notify error")

    def run(self):
        # if self.isConnect == 1:
        #     self.startGame()
        # else:
        self.start_time = int(time.time() * 1000)
        self.capture_screen()
        while True:
            if len(self.positions) > 0:
                for position in self.positions:
                    self.loopSwapPage(position)
                    self.loopRefreshStamina(position)
            print('sleep 10 second')
            time.sleep(10)


bot = MyBot()
event_loop = asyncio.get_event_loop()
try:
    event_loop.run_until_complete(bot.run())
    event_loop.run_forever()
finally:
    event_loop.close()
