"""pip install winsdk pyautogui screen_ocr[winrt] wheel pywin32 opencv-python"""
import argparse
import time
import os
import logging
import sys
#from threading import Thread
#from collections import namedtuple
from enum import Enum
# import win32gui
import pyautogui
#import pyscreeze
# import screen_ocr
import bluestacks
from gamebot import Point, Box, Rect, Color, Region, BoxRegion, find_image, find_image_timeout, locate_all, set_default_region


DEBUG = True
RESOLUTION = (659, 1131)
BLUESTACKS = {}
GAME = {}
#OCR_READER = screen_ocr.Reader.create_quality_reader()
SCRIPT_DIR = os.path.dirname(__file__)
os.chdir(SCRIPT_DIR)
logger = logging.getLogger(__name__)
formatter = logging.Formatter(
    "%(asctime)s:%(levelname)s:%(lineno)d:%(message)s", datefmt="%H:%M:%S")
logger.setLevel(logging.DEBUG if DEBUG else logging.INFO)
ch = logging.StreamHandler()
ch.setFormatter(formatter)
logger.addHandler(ch)

ChickenButtonMode = Enum("ChickenButtonMode", ["DRAIN", "REFILL"])

class EggInc:
    """A Bot that can play Egg, Inc."""

    def __init__(self):
        self.regions = {}
        self.chicken_button_mode = ChickenButtonMode.DRAIN
        self.region_rects = {
            'game': Rect(0, 0, 607, 1082),
        }
        # Turn these rects into Regions
        for key, val in self.region_rects.items():
            self.regions[key] = Region(val, BS_PT, debug=True)
        self.colors = {
            'chicken_button_bar_green': Color((25, 172, 0)),
            'chicken_button_bar_red': Color((240, 13, 13)),
            'green': Color((25, 172, 0)),
        }
        self.corner_location = None

    def drone_hunt(self):
        """Search for drones"""
        # drone_images = [x for x in os.listdir() if x.startswith('drone')]
        # for img in drone_images:
        #     if find_image(img, click=True):
        #         logger.info("Got Drone: %s", img)
        corner = find_image('path_corner.png')
        if corner:
            if self.corner_location is None:
                print(f"Found corner: {corner}")
            self.corner_location = corner
        else:
            if self.corner_location is None:
                print("Failed to find corner to drone hunt with")
                return
        corner = self.corner_location
        for _ in range(10):
            spots = [
                (corner.left - 160, corner.top - 120),
                (corner.left - 160, corner.top - 100),
                (corner.left - 140, corner.top - 100),
                (corner.left - 120, corner.top - 100),
                # (corner.left - 100, corner.top - 100),
                # (corner.left - 80, corner.top - 100),
                (corner.left - 135, corner.top - 80),
                (corner.left - 120, corner.top - 80),
                # (corner.left - 100, corner.top - 80),
                # (corner.left - 80, corner.top - 80),
            ]
            for x, y in spots:
                # pyautogui.moveTo(x, y)
                pyautogui.click(x, y)
                time.sleep(0.1)
            time.sleep(0.3)


    def drone_hunt2(self):
        lab_button = find_image('lab.png', click=True)
        if lab_button:
            time.sleep(2)

        shells_button = find_image('shells.png', click=True)
        if shells_button:
            time.sleep(2)

        farm_button = find_image('farm.png', click=True)
        sets_button = find_image('sets.png', click=True)

        spots = [
            (227, 446),
            (243, 458),
            (259, 470),
            (280, 478),
        ]
        for _ in range(200):
            for x, y in spots:
                # pyautogui.moveTo(x, y)
                pyautogui.click(x, y)
                time.sleep(0.2)

        leave_shells = find_image('leave_shells.png', click=True)
        if leave_shells:
            time.sleep(2)

    def hold_chicken_button(self):
        """Reentrant"""
        button_loc = find_image('chicken_button.png')
        if not button_loc:
            logger.error("Chicken button not found")
            return
        button_region = BoxRegion(button_loc, BS_PT)
        button_point = button_region.get_random_point()

        # Wait for bar to fill up with green
        # leftmost fully green pixel (288, 158)
        # rightmost fully green pixel (336, 158)
        bar_start = Point(288, 158)
        bar_end = Point(336, 158)
        # breakpoint()
        # pix = get_pixel(336, 158)  # int(bar_end.x), int(bar_end.y))
        pix = pyautogui.pixel(bar_end.x, bar_end.y)
        green = self.colors['chicken_button_bar_green']
        if pix != green:
            logger.info("Waiting on green bar: %s != %s", pix, green)
            return
            # time.sleep(2)
            # pix = pyautogui.pixel(*bar_end)

        # Hold button down
        logger.debug("Holding chicken button")
        try:
            pix = pyautogui.pixel(*bar_start)
            if pix == green:
                pyautogui.moveTo(button_point)
                #move_mouse(*chicken_button)
                time.sleep(1)
                pyautogui.mouseDown()
                start_time = time.perf_counter()
            duration = 0
            while pix == green and duration < 90:
                pix = pyautogui.pixel(*bar_start)
                time.sleep(0.5)
                duration = time.perf_counter() - start_time
            time.sleep(3)  # give it a little more time to finish out the bar
        finally:
            pyautogui.mouseUp()
            logger.debug("Letting go of chicken button")

    def collect_gift(self):
        """Look for a package/gift and collect it"""
        gift = find_image_timeout('package.png', click=True, timeout=1, quiet=True)
        if gift:
            collect = find_image_timeout('collect.png', click=True, timeout=3)
            if collect:
                logger.info("Collected a gift")
            else:
                logger.error("Found gift, but couldn't find collect button")

    def upgrade(self):
        # Make sure we're more likely on the main screen
        find_image('close.png', click=True)

        logger.debug("Upgrading in the lab")

        lab = find_image('lab.png', click=True)
        if not lab:
            logger.error("Couldn't find lab?")
            return
        time.sleep(0.5)

        # Make sure we're on the common tab
        logger.debug("Clicking COMMON")
        # find_image_timeout('common.png', click=True, timeout=2)
        time.sleep(0.5)
        logger.debug("On COMMON tab")

        num_scrolls = 0
        while True:

            # Ensure we're looking at research
            common = find_image('common.png')
            if not common:
                logger.error("Not looking at research, no common button")
                break
            epic = find_image('epic.png')
            if not epic:
                logger.error("Not looking at research, no epic button")
                break

            # Find the research buttons
            research_buttons = locate_all('research.png')
            logger.debug("Research buttons: %s", research_buttons)
            if not research_buttons:
                logger.warning("No research buttons, let's scroll")
                if not find_image('to_unlock.png'):
                    # Let's scroll
                    # 110, 800 -> 350, 900
                    # y = 280
                    pyautogui.moveTo(200, 800)
                    # pyautogui.mouseDown()  # 200, 800)
                    y_offset = 520
                    pyautogui.dragRel(xOffset=0, yOffset=-y_offset, duration=2)
                    pyautogui.mouseUp(200, 280, duration=3)
                    time.sleep(1)
                    num_scrolls += 1
                    if num_scrolls >= 5:
                        logger.warning("5 scrolls, let's give up")
                    continue
                else:
                    logger.warning("Haven't unlocked next Tier")
                    break
            how_many_green = 0
            # Click & Hold them all for a little bit
            for button in research_buttons:
                reg = BoxRegion(button)
                if reg.contains_color([self.colors['green']]):
                    reg.click_hold(5)
                    how_many_green += 1
                    logger.debug("Upgrading %s", reg)
            if how_many_green == 0:
                logger.debug("No research ready")
                break

        close_button = find_image_timeout('close.png', click=True, timeout=2)
        if not close_button:
            logger.warning("Couldn't find close button...")
        else:
            logger.debug("Closing research")
        time.sleep(1)

    def play(self):
        """Run the bot loop"""
        iterations = 1
        while True:
            self.collect_gift()
            self.drone_hunt()
            # self.drone_hunt2()
            #if iterations % 100 == 0:
            #   self.upgrade()
            #self.hold_chicken_button()
            find_image('white_x.png', click=True)
            find_image('leave_shells.png', click=True)
            iterations += 1

def play():
    ret = bluestacks.get_dimensions(reset=True)
    global BLUESTACKS, GAME, BS_PT
    BLUESTACKS = ret['bluestacks']
    GAME = ret['game']
    BS_PT = Point(BLUESTACKS['left'], BLUESTACKS['top'])
    region = Box(BLUESTACKS['left'], BLUESTACKS['top'], BLUESTACKS['width'], BLUESTACKS['height'])
    set_default_region(region)
    assert BLUESTACKS['width'] == 659 and BLUESTACKS['height'] == 1131
    os.chdir(os.path.join(SCRIPT_DIR, "659x1131"))
    logger.info(BLUESTACKS)
    logger.info(GAME)
    game = EggInc()
    game.play()

if __name__ == "__main__":
    play()