import sys
from unittest import mock

# Mock out modules that require a graphical interface
sys.modules["pynput.mouse"] = mock.Mock()
sys.modules["mss.linux"] = mock.Mock()
