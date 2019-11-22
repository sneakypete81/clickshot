import time
from pynput.mouse import Controller, Button


class Mouse:
    def __init__(self):
        self._controller = Controller()

    def get_position(self):
        return self._controller.position

    def move_to(self, x, y):
        self._controller.position = (x, y)

    def click(self, x, y, button=Button.left):
        self.move_to(x, y)
        time.sleep(0.01)
        self._controller.click(button)
