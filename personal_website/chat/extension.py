import re
from typing import Any
from xml.etree.ElementTree import Element, SubElement

from markdown import Markdown
from markdown.blockparser import BlockParser
from markdown.blockprocessors import BlockProcessor
from markdown.extensions import Extension

from personal_website.chat.exception import UnknownSpeaker, UnterminatedChatBlock
from personal_website.person.dto import Person
from personal_website.person.repository import PersonRepository

AVATAR_URL_PREFIX = "{static}/images/family/people/"
BLOCK_PROCESSOR_PRIORITY = 105


class ChatBlockProcessor(BlockProcessor):
    """Turns ``::: chat <name>`` ... ``:::`` fences into avatar + speech bubble markup."""

    _OPEN = re.compile(r"^::: *chat +(?P<name>\S.*?) *$")
    _CLOSE = re.compile(r"^::: *$")

    def __init__(self, parser: BlockParser, people: dict[str, Person]) -> None:
        super().__init__(parser)
        self._people = people

    def test(self, parent: Element, block: str) -> bool:
        return self._opening_name(block) is not None

    def run(self, parent: Element, blocks: list[str]) -> None:
        name = self._opening_name(blocks[0])
        if name is None:
            return
        _, _, first_lines = blocks.pop(0).partition("\n")

        message, leftover = self._split_at_closing_fence(name, first_lines, blocks)
        if leftover:
            blocks.insert(0, leftover)

        bubble = self._build_bubble(parent=parent, speaker=self._speaker(name=name))
        self.parser.parseChunk(bubble, message)

    def _opening_name(self, block: str) -> str | None:
        match = self._OPEN.match(block.partition("\n")[0])
        return match.group("name") if match else None

    def _split_at_closing_fence(self, name: str, first_lines: str, blocks: list[str]) -> tuple[str, str]:
        """Consume blocks up to the closing fence, returning the message and any trailing text."""
        message_blocks: list[str] = []
        block = first_lines
        while True:
            lines = block.split("\n")
            for index, line in enumerate(lines):
                if self._CLOSE.match(line):
                    message_blocks.append("\n".join(lines[:index]))
                    return "\n\n".join(message_blocks), "\n".join(lines[index + 1 :])
            message_blocks.append(block)
            if not blocks:
                raise UnterminatedChatBlock(name=name)
            block = blocks.pop(0)

    def _speaker(self, name: str) -> Person:
        try:
            return self._people[name]
        except KeyError:
            raise UnknownSpeaker(name=name) from None

    def _build_bubble(self, parent: Element, speaker: Person) -> Element:
        """Builds the chat markup and returns the element the message content belongs in."""
        container = SubElement(parent, "div")
        container.set("class", "chat")

        avatar = SubElement(container, "img")
        avatar.set("class", "chat__avatar")
        avatar.set("src", f"{AVATAR_URL_PREFIX}{speaker.avatar}")
        avatar.set("alt", speaker.name)

        bubble = SubElement(container, "div")
        bubble.set("class", "chat__body")

        return bubble


class ChatExtension(Extension):
    def __init__(self, repository: PersonRepository, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._people = {person.name: person for person in repository.get_items()}

    def extendMarkdown(self, md: Markdown) -> None:
        md.parser.blockprocessors.register(
            ChatBlockProcessor(parser=md.parser, people=self._people),
            "chat",
            BLOCK_PROCESSOR_PRIORITY,
        )
