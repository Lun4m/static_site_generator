from enum import Enum

from htmlnode import LeafNode


class TextType(Enum):
    Text = 0
    Bold = 1
    Italic = 2
    Code = 3
    Link = 4
    Image = 5


class TextNode:
    def __init__(self, text, text_type=None, url=None) -> None:
        self.text = text
        self.text_type = text_type
        self.url = url

    def __eq__(self, other) -> bool:
        text = self.text == other.text
        text_type = self.text_type == other.text_type
        url = self.url == other.url
        return text and text_type and url

    def __repr__(self) -> str:
        return f"TextNode({self.text}, {self.text_type}, {self.url})"


def text_node_to_html_node(text_node):
    # TODO: add tests
    match text_node.text_type:
        case TextType.Text:
            return LeafNode(value=text_node.text)
        case TextType.Bold:
            return LeafNode(tag="b", value=text_node.text)
        case TextType.Italic:
            return LeafNode(tag="i", value=text_node.text)
        case TextType.Code:
            return LeafNode(tag="code", value=text_node.text)
        case TextType.Link:
            return LeafNode(
                tag="a", value=text_node.text, props={"href": text_node.url}
            )
        case TextType.Image:
            return LeafNode(
                tag="img", props={"src": text_node.url, "alt": text_node.text}
            )
        case _:
            raise Exception("Unsupported type")


def split_nodes_delimiter(old_nodes, delimiter, text_type):
    # TODO: support multilevel nesting of TextType
    new_nodes = []
    for node in old_nodes:
        if node.text_type != TextType.Text:
            # warn: we only split Text
            new_nodes.append(node)
            continue

        sections = node.text.split(delimiter)
        if len(sections) % 2 == 0:
            raise Exception("Missing a closing delimiter")

        for i, text in enumerate(sections):
            if text == "":
                continue

            if i % 2 == 0:
                new = TextNode(text, TextType.Text)
            else:
                new = TextNode(text, text_type)
            new_nodes.append(new)
    return new_nodes
