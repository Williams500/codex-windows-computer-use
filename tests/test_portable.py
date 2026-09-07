import unittest
from windows_cu.core import KEY_VK, utf16_units

class PortableTests(unittest.TestCase):
    def test_generic_keyset(self):
        for k in ("a","z","0","9","ctrl","alt","win","enter","f12","delete"):
            self.assertIn(k, KEY_VK)

    def test_utf16_ascii(self):
        self.assertEqual(list(utf16_units("abc")), ["a","b","c"])

    def test_utf16_surrogate_pair(self):
        units=list(utf16_units("😀"))
        self.assertEqual(len(units), 2)
        self.assertEqual([ord(x) for x in units], [0xD83D,0xDE00])

if __name__ == "__main__": unittest.main()
