from pathlib import Path
from html.parser import HTMLParser
import sys

class Extractor(HTMLParser):
    def __init__(self, language):
        super().__init__()
        self.language = language
        self.depth = 0
        self.parts = []
        self.items = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if self.depth:
            self.depth += 1
        elif attrs.get("data-lang") == self.language:
            self.depth = 1
            self.parts = []

    def handle_endtag(self, tag):
        if self.depth:
            self.depth -= 1
            if self.depth == 0:
                self.items.append(" ".join("".join(self.parts).split()))

    def handle_data(self, data):
        if self.depth:
            self.parts.append(data)


path = Path(sys.argv[1])
language = sys.argv[2] if len(sys.argv) > 2 else "en"
parser = Extractor(language)
parser.feed(path.read_text(encoding="utf-8"))
for index, text in enumerate(parser.items, 1):
    print(f"{index:03d} {language.upper()} | {text}")
