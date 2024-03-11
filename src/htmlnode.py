class HTMLNode:
    def __init__(self, tag=None, value=None, children=None, props=None):
        self.tag = tag
        self.value = value
        self.children = children
        self.props = props

    def to_html(self):
        raise NotImplementedError

    def props_to_html(self):
        if self.props is not None:
            joined = [f' {key}="{value}"' for key, value in self.props.items()]
            return "".join(joined)
        return ""

    def __eq__(self, other) -> bool:
        tag = self.tag == other.tag
        value = self.value == other.value
        children = self.children == other.children
        props = self.props == other.props
        return tag and value and children and props

    def __repr__(self) -> str:
        return f"HTMLNode({self.tag}, {self.value}, {self.children}, {self.props})"


class LeafNode(HTMLNode):
    def __init__(self, tag=None, value=None, props=None):
        super().__init__(tag, value, None, props)
        pass

    def to_html(self):
        if self.value is None:
            raise ValueError("'value' field is required")
        if self.tag is None:
            return self.value
        return f"<{self.tag}{self.props_to_html()}>{self.value}</{self.tag}>"

    def __repr__(self) -> str:
        return f"Leaf({self.tag}, {self.value}, {self.props})"


class ParentNode(HTMLNode):
    def __init__(self, tag=None, children=None, props=None):
        super().__init__(tag, None, children, props)
        pass

    def to_html(self):
        if self.children is None:
            raise ValueError("'children' field is required")
        if self.tag is None:
            raise ValueError("'tag' field is required")
        result = f"<{self.tag}{self.props_to_html()}>"
        for child in self.children:
            result += child.to_html()
        return result + f"</{self.tag}>"

    def __repr__(self) -> str:
        return f"Parent({self.tag}, {self.children}, {self.props})"
