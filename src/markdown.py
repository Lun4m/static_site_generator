import enum
import re

from htmlnode import LeafNode, ParentNode
from textnode import TextNode, TextType


class Block(enum.Enum):
    Paragraph = 0
    Heading = 1
    Code = 2
    Quote = 3
    UnorderedList = 4
    OrderedList = 5


## Markdown inline
def extract_markdown_images(text):
    # ![alt](src)
    return re.findall(r"!\[(.*?)\]\((.*?)\)", text)


def extract_markdown_links(text):
    # [text](url)
    return re.findall(r"\[(.*?)\]\((.*?)\)", text)


def split_nodes_image(old_nodes):
    new_nodes = []
    for node in old_nodes:
        if node.text_type != TextType.Text:
            # warn: we only split Text
            new_nodes.append(node)
            continue

        matches = extract_markdown_images(node.text)
        if not matches:
            new_nodes.append(node)
            continue

        text = node.text
        for alt, url in matches:
            start, text = text.split(f"![{alt}]({url})", maxsplit=1)
            if start != "":
                new_nodes.append(TextNode(start, TextType.Text))
            new_nodes.append(TextNode(alt, TextType.Image, url))

        if text != "":
            new_nodes.append(TextNode(text, TextType.Text))
    return new_nodes


def split_nodes_link(old_nodes):
    new_nodes = []
    for node in old_nodes:
        if node.text_type != TextType.Text:
            # warn: we only split Text
            new_nodes.append(node)
            continue

        matches = extract_markdown_links(node.text)
        if not matches:
            new_nodes.append(node)
            continue

        text = node.text
        for alt, url in matches:
            start, text = text.split(f"[{alt}]({url})", maxsplit=1)
            if start != "":
                new_nodes.append(TextNode(start, TextType.Text))
            new_nodes.append(TextNode(alt, TextType.Link, url))

        if text != "":
            new_nodes.append(TextNode(text, TextType.Text))
    return new_nodes


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


def text_to_textnodes(text):
    nodes = [TextNode(text, TextType.Text)]
    delimiters = {
        TextType.Bold: "**",
        TextType.Italic: "*",
        TextType.Code: "`",
    }

    for t, d in delimiters.items():
        nodes = split_nodes_delimiter(nodes, d, t)

    nodes = split_nodes_image(nodes)
    nodes = split_nodes_link(nodes)
    return nodes


def text_node_to_html_node(text_node):
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


## Markdown blocks
def markdown_to_blocks(markdown: str):
    # NOTE: we assume blocks are separated by blank lines!
    lines = markdown.split("\n\n")

    blocks = []
    for line in lines:
        if line == "":
            continue
        blocks.append(line.strip())
    return blocks


def block_to_block_type(block):
    # TODO: might be better
    lines = block.split("\n")
    allowed_headings = ["# ", "## ", "### ", "#### ", "##### ", "###### "]

    if any([lines[0].startswith(h) for h in allowed_headings]):
        return Block.Heading
    if len(lines) > 1 and lines[0] == "```" and lines[-1] == "```":
        return Block.Code
    if all([line.startswith(">") for line in lines]):
        return Block.Quote
    if all([line.startswith("* ") for line in lines]):
        return Block.UnorderedList
    if all([line.startswith("- ") for line in lines]):
        return Block.UnorderedList
    if all([line.startswith(f"{i+1}. ") for i, line in enumerate(lines)]):
        return Block.OrderedList
    return Block.Paragraph


def heading_block_to_html(block):
    # NOTE: We assume a single title line
    headings = {
        "# ": "h1",
        "## ": "h2",
        "### ": "h3",
        "#### ": "h4",
        "##### ": "h5",
        "###### ": "h6",
    }
    for h in headings:
        if h in block:
            block = block.removeprefix(h)
            nodes = text_to_textnodes(block)
            children = [text_node_to_html_node(node) for node in nodes]
            return ParentNode(tag=headings[h], children=children)

    raise Exception(f"Wrong heading in line: {block}")


def code_block_to_html(block):
    lines = block.split("\n")
    text = "\n".join(lines[1:-1])
    nodes = text_to_textnodes(text)
    children = [text_node_to_html_node(node) for node in nodes]
    return ParentNode(tag="pre", children=[ParentNode(tag="code", children=children)])


def quote_block_to_html(block):
    lines = block.split("\n")
    text = "\n".join([line[1:].lstrip() for line in lines])
    nodes = text_to_textnodes(text)
    children = [text_node_to_html_node(node) for node in nodes]
    return ParentNode(tag="blockquote", children=children)


def unordered_list_block_to_html(block):
    parent_node = ParentNode(tag="ul")
    parent_node.children = []
    lines = block.split("\n")
    for line in lines:
        nodes = text_to_textnodes(line[1:].lstrip())
        children = [text_node_to_html_node(node) for node in nodes]
        inner_parent = ParentNode(tag="li", children=children)
        parent_node.children.append(inner_parent)
    return parent_node


def ordered_list_block_to_html(block):
    parent_node = ParentNode(tag="ol")
    parent_node.children = []
    lines = block.split("\n")
    for line in lines:
        _, text = line.split(".", maxsplit=1)
        nodes = text_to_textnodes(text.lstrip())
        children = [text_node_to_html_node(node) for node in nodes]
        inner_parent = ParentNode(tag="li", children=children)
        parent_node.children.append(inner_parent)
    return parent_node


def paragraph_block_to_html(block):
    nodes = text_to_textnodes(block)
    children = [text_node_to_html_node(node) for node in nodes]
    return ParentNode(tag="p", children=children)


def markdown_to_html_node(markdown):
    html = ParentNode(tag="div", children=[])
    html.children = []

    blocks = markdown_to_blocks(markdown)
    for block in blocks:
        match block_to_block_type(block):
            case Block.Heading:
                nodes = heading_block_to_html(block)
            case Block.Code:
                nodes = code_block_to_html(block)
            case Block.Quote:
                nodes = quote_block_to_html(block)
            case Block.UnorderedList:
                nodes = unordered_list_block_to_html(block)
            case Block.OrderedList:
                nodes = ordered_list_block_to_html(block)
            case Block.Paragraph:
                nodes = paragraph_block_to_html(block)
            case _:
                raise Exception("Unsuppported Block")
        html.children.append(nodes)
    return html
