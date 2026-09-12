import re
from collections.abc import Iterable

from personal_website.citation.dto import Citation

REFERENCES_HEADING = "References"

_EXTERNAL_ANCHOR = re.compile(
    r'<a\s[^>]*href="(?P<url>https?://[^"]*)"[^>]*>(?P<label>.*?)</a>',
    re.DOTALL,
)


def add_citations(html: str) -> str:
    citations = _collect_citations(html)
    if not citations:
        return html
    return f"{_replace_links(html, citations)}\n{_render_references(citations.values())}"


def _collect_citations(html: str) -> dict[str, Citation]:
    citations: dict[str, Citation] = {}
    for match in _EXTERNAL_ANCHOR.finditer(html):
        url = match.group("url")
        if url not in citations:
            citations[url] = Citation(number=len(citations) + 1, label=match.group("label"), url=url)
    return citations


def _replace_links(html: str, citations: dict[str, Citation]) -> str:
    def _to_marker(match: re.Match[str]) -> str:
        citation = citations[match.group("url")]
        return f'{match.group("label")}<sup class="citation"><a href="#{citation.anchor}">[{citation.number}]</a></sup>'

    return _EXTERNAL_ANCHOR.sub(_to_marker, html)


def _render_references(citations: Iterable[Citation]) -> str:
    items = "\n".join(_render_reference(citation) for citation in citations)
    return (
        '<section class="citations">\n'
        f"<h2>{REFERENCES_HEADING}</h2>\n"
        '<ol class="citations__list">\n'
        f"{items}\n"
        "</ol>\n"
        "</section>"
    )


def _render_reference(citation: Citation) -> str:
    label = "" if citation.label == citation.url else f"{citation.label} &mdash; "
    return (
        f'<li class="citations__item" id="{citation.anchor}">'
        f'<span class="citations__marker">[{citation.number}]</span> '
        f'{label}<a class="citations__url" href="{citation.url}">{citation.url}</a>'
        "</li>"
    )
