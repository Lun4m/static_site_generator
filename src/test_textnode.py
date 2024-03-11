import unittest

from textnode import TextNode


class TestTextNode(unittest.TestCase):
    def test_eq(self):
        node = TextNode("This is a text node", "bold")
        node2 = TextNode("This is a text node", "bold")
        self.assertEqual(node, node2)

    def test_different_type(self):
        node = TextNode("This is a text node", "italics")
        node2 = TextNode("This is a tex node", "bold")
        self.assertNotEqual(node, node2)

    def test_different_url(self):
        node = TextNode("This is a text node", "bold", "https://website.com")
        node2 = TextNode("This is a text node", "bold", "https://notsite.com")
        self.assertNotEqual(node, node2)


if __name__ == "__main__":
    unittest.main()
