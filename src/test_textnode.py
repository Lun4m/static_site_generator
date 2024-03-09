import unittest

from htmlnode import LeafNode
from textnode import TextNode, TextType, split_nodes_delimiter, text_node_to_html_node


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


class SplitDelimiterText(unittest.TestCase):
    def test_split_code(self):
        node = TextNode("This is text with a `code block` word", TextType.Text)
        new_nodes = split_nodes_delimiter([node], "`", TextType.Code)
        expected = [
            TextNode("This is text with a ", TextType.Text),
            TextNode("code block", TextType.Code),
            TextNode(" word", TextType.Text),
        ]
        self.assertEqual(new_nodes, expected)

    def test_split_bold(self):
        node = TextNode("**This** is text with words", TextType.Text)
        new_nodes = split_nodes_delimiter([node], "**", TextType.Bold)
        expected = [
            TextNode("This", TextType.Bold),
            TextNode(" is text with words", TextType.Text),
        ]
        self.assertEqual(new_nodes, expected)

    def test_split_multiple(self):
        nodes = [
            TextNode("*This* is text with words", TextType.Text),
            TextNode("This is *text* with words", TextType.Text),
        ]
        new_nodes = split_nodes_delimiter(nodes, "*", TextType.Italic)
        expected = [
            TextNode("This", TextType.Italic),
            TextNode(" is text with words", TextType.Text),
            TextNode("This is ", TextType.Text),
            TextNode("text", TextType.Italic),
            TextNode(" with words", TextType.Text),
        ]
        self.assertEqual(new_nodes, expected)


if __name__ == "__main__":
    unittest.main()
