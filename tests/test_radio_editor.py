import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
from unittest.mock import patch, MagicMock
from main import RadioStationEditor  # Agora deve funcionar

class TestRadioStationEditor(unittest.TestCase):
    def setUp(self):
        self.root = MagicMock()
        self.editor = RadioStationEditor(self.root)

    def test_sample(self):
        self.assertTrue(True)  # Teste simples para verificar se o ambiente está ok

if __name__ == '__main__':
    unittest.main()