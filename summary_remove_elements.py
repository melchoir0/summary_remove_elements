from pelican import signals, contents
from pelican.generators import ArticlesGenerator
from pelican.utils import truncate_html_words
from bs4 import BeautifulSoup, NavigableString
from six import text_type

def init(pelican):
    default_invalid_tags = ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']
    global invalid_tags
    invalid_tags = pelican.settings.get('SUMMARY_REMOVE_ELEMENTS_INVALID_TAGS', default_invalid_tags)

def summary_remove_elements(instance):
    if type(instance) == contents.Article:
        summary = None
        SUMMARY_MAX_LENGTH = instance.settings.get('SUMMARY_MAX_LENGTH')
        if hasattr(instance, '_summary') and instance._summary:
            summary = instance._summary
        else:
            summary = truncate_html_words(instance.content, SUMMARY_MAX_LENGTH)
        summary = BeautifulSoup(summary, 'html.parser')
        for tag in summary.findAll(True):
            if tag.name in invalid_tags:
                s = ""

                for c in tag.contents:
                    if not isinstance(c, NavigableString):
                        c = strip_tags(unicode(c), invalid_tags)
                    s += unicode(c)
                tag.replaceWith(s)
        instance._summary = text_type(summary)

def run_plugin(generators):
    for generator in generators:
        if isinstance(generator, ArticlesGenerator):
            for article in generator.articles:
                summary_remove_elements(article)

def register():
        signals.initialized.connect(init)
        try:
            signals.all_generators_finalized.connect(run_plugin)
        except AttributeError:
            # NOTE: This may result in #314 so shouldn't really be relied on
            # https://github.com/getpelican/pelican-plugins/issues/314
            signals.content_object_init.connect(summary_remove_elements)
