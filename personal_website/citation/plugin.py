from pelican import signals
from pelican.contents import Article, Content

from personal_website.citation.renderer import add_citations


def cite_article_links(instance: Content) -> None:
    if not isinstance(instance, Article):
        return
    instance._content = add_citations(instance._content)


def register() -> None:
    signals.content_object_init.connect(cite_article_links)
