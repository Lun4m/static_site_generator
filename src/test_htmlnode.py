import unittest

from htmlnode import HTMLNode, LeafNode, ParentNode


class TestHTMLNode(unittest.TestCase):
    def test_props_to_html(self):
        node = HTMLNode(props={"href": "https://www.google.com", "target": "_blank"})
        expected = ' href="https://www.google.com" target="_blank"'
        self.assertEqual(node.props_to_html(), expected)


class TestLeafNode(unittest.TestCase):
    def test_leaf_to_html(self):
        nodes = (
            LeafNode("p", "This is a paragraph of text."),
            LeafNode("a", "Click me!", {"href": "https://www.google.com"}),
        )
        expected = (
            "<p>This is a paragraph of text.</p>",
            '<a href="https://www.google.com">Click me!</a>',
        )
        for node, exp in zip(nodes, expected):
            self.assertEqual(node.to_html(), exp)


class TestParentNode(unittest.TestCase):
    def test_single_parent(self):
        node = ParentNode(
            "p",
            [
                LeafNode("b", "Bold text"),
                LeafNode(None, "Normal text"),
                LeafNode("i", "italic text"),
                LeafNode(None, "Normal text"),
            ],
        )
        expected = "<p><b>Bold text</b>Normal text<i>italic text</i>Normal text</p>"
        self.assertEqual(node.to_html(), expected)

    def test_nested_parents(self):
        node = ParentNode(
            "p",
            [
                ParentNode(
                    "b",
                    [
                        LeafNode("b", "Bold text"),
                        LeafNode(None, "Normal text"),
                        LeafNode("i", "italic text"),
                    ],
                ),
                LeafNode(None, "Normal text"),
            ],
        )
        expected = (
            "<p><b><b>Bold text</b>Normal text<i>italic text</i></b>Normal text</p>"
        )
        self.assertEqual(node.to_html(), expected)


if __name__ == "__main__":
    unittest.main()
