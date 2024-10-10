import WIP.pyautogui as pyautogui
import random
import time
import string

def random_movement():
    screen_width, screen_height = pyautogui.size()
    while True:
        # Move the mouse to a random position
        x = random.randint(0, screen_width)
        y = random.randint(0, screen_height)
        pyautogui.moveTo(x, y, duration=random.uniform(0.1, 1.0))

        # Randomly decide whether to click
        if random.random() < 0.1:  # 10% chance to click
            pyautogui.click()

        # Randomly decide whether to type
        if random.random() < 0.05:  # 5% chance to type
            random_text = ''.join(random.choices(string.ascii_letters + string.digits, k=random.randint(5, 15)))
            pyautogui.typewrite(random_text, interval=random.uniform(0.05, 0.2))

        # Wait for a random interval before the next action
        time.sleep(random.uniform(0.5, 2.0))

if __name__ == "__main__":
    random_movement()
