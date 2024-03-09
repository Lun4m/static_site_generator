import unittest

from htmlnode import LeafNode
from textnode import TextNode, TextType, text_node_to_html_node


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


class ConversionTests(unittest.TestCase):
    def test_conversion(self):
        text_nodes = [
            TextNode("Text", TextType.Text),
            TextNode("Bold", TextType.Bold),
            TextNode("Italic", TextType.Italic),
            TextNode("Code", TextType.Code),
            TextNode("Link", TextType.Link, "https://website.com"),
            TextNode("Image", TextType.Image, "image.png"),
        ]
        expected = [
            LeafNode(value="Text"),
            LeafNode(tag="b", value="Bold"),
            LeafNode(tag="i", value="Italic"),
            LeafNode(tag="code", value="Code"),
            LeafNode(tag="a", value="Link", props={"href": "https://website.com"}),
            LeafNode(tag="img", props={"src": "image.png", "alt": "Image"}),
        ]
        for node, exp in zip(text_nodes, expected):
            self.assertEqual(text_node_to_html_node(node), exp)


if __name__ == "__main__":
    unittest.main()
