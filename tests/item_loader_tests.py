import unittest
import item_loader

class Floop:
    pass

class ItemLoaderTests(unittest.TestCase):

    def test_get_class(self):
        cls = item_loader.get_class("item_loader_tests.Floop")
        instance = cls()
        self.assertIsInstance(instance, Floop)

if __name__ == '__main__':
    unittest.main()
