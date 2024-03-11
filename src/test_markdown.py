import unittest

from htmlnode import LeafNode
from markdown import (
    Block,
    block_to_block_type,
    extract_markdown_images,
    extract_markdown_links,
    markdown_to_blocks,
    split_nodes_delimiter,
    split_nodes_image,
    split_nodes_link,
    text_node_to_html_node,
    text_to_textnodes,
)
from textnode import TextNode, TextType


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


class SplitDelimiterTests(unittest.TestCase):
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


class ImageAndLinkParsingTests(unittest.TestCase):
    def test_images(self):
        text = "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png) and ![another](https://i.imgur.com/dfsdkjfd.png)"
        expected = [
            ("image", "https://i.imgur.com/zjjcJKZ.png"),
            ("another", "https://i.imgur.com/dfsdkjfd.png"),
        ]
        self.assertEqual(extract_markdown_images(text), expected)

    def test_links(self):
        text = "This is text with a [link](https://www.example.com) and [another](https://www.example.com/another)"
        expected = [
            ("link", "https://www.example.com"),
            ("another", "https://www.example.com/another"),
        ]
        self.assertEqual(extract_markdown_links(text), expected)


class ImageAndLinkSplittingTests(unittest.TestCase):
    def test_images(self):
        node = TextNode(
            "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png) and another ![second image](https://i.imgur.com/3elNhQu.png)",
            TextType.Text,
        )
        new_nodes = split_nodes_image([node])
        expected = [
            TextNode("This is text with an ", TextType.Text),
            TextNode("image", TextType.Image, "https://i.imgur.com/zjjcJKZ.png"),
            TextNode(" and another ", TextType.Text),
            TextNode("second image", TextType.Image, "https://i.imgur.com/3elNhQu.png"),
        ]
        self.assertEqual(new_nodes, expected)

    def test_links(self):
        node = TextNode(
            "This is text with an [link](https://www.imgur.com) and another [second link](https://www.google.com)",
            TextType.Text,
        )
        new_nodes = split_nodes_link([node])
        expected = [
            TextNode("This is text with an ", TextType.Text),
            TextNode("link", TextType.Link, "https://www.imgur.com"),
            TextNode(" and another ", TextType.Text),
            TextNode("second link", TextType.Link, "https://www.google.com"),
        ]
        self.assertEqual(new_nodes, expected)


class TextToTextNodeTests(unittest.TestCase):
    def test_parsing(self):
        text = "This is **text** with an *italic* word and a `code block` and an ![image](https://i.imgur.com/zjjcJKZ.png) and a [link](https://boot.dev)"
        nodes = text_to_textnodes(text)
        expected = [
            TextNode("This is ", TextType.Text),
            TextNode("text", TextType.Bold),
            TextNode(" with an ", TextType.Text),
            TextNode("italic", TextType.Italic),
            TextNode(" word and a ", TextType.Text),
            TextNode("code block", TextType.Code),
            TextNode(" and an ", TextType.Text),
            TextNode("image", TextType.Image, "https://i.imgur.com/zjjcJKZ.png"),
            TextNode(" and a ", TextType.Text),
            TextNode("link", TextType.Link, "https://boot.dev"),
        ]
        self.assertEqual(nodes, expected)


class MarkdownBlocksTests(unittest.TestCase):
    def test_md_to_block(self):
        text = """This is **bolded** paragraph

This is another paragraph with *italic* text and `code` here
This is the same paragraph on a new line

* This is a list
* with items
"""
        blocks = markdown_to_blocks(text)
        expected = [
            "This is **bolded** paragraph",
            "This is another paragraph with *italic* text and `code` here\nThis is the same paragraph on a new line",
            "* This is a list\n* with items",
        ]
        self.assertEqual(blocks, expected)

    def test_block_type_parsing(self):
        blocks = [
            "#### This is a header",
            "This is **bolded** paragraph",
            "```\npython some_script.py\n```",
            "This is another paragraph with *italic* text and `code` here\nThis is the same paragraph on a new line",
            "> Quotes\n> And more quotes\n> And more quotes",
            "* This is a list\n* with items",
            "1. item\n2. item\n3. item",
        ]
        expected = [
            Block.Heading,
            Block.Paragraph,
            Block.Code,
            Block.Paragraph,
            Block.Quote,
            Block.UnorderedList,
            Block.OrderedList,
        ]
        for block, exp in zip(blocks, expected):
            self.assertEqual(block_to_block_type(block), exp)


if __name__ == "__main__":
    unittest.main()
