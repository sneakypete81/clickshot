import sys
from unittest import mock

sys.modules["pyautogui"] = mock.Mock()
