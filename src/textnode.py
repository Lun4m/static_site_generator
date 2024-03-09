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
