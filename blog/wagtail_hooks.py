import wagtail.admin.rich_text.editors.draftail.features as draftail_features
from django.conf import settings
from django.utils.html import format_html_join
from draftjs_exporter.dom import DOM
from wagtail.admin.rich_text.converters.html_to_contentstate import InlineEntityElementHandler
from wagtail.core import hooks


# KaTeX Inline:

@hooks.register('register_rich_text_features')
def register_katex_inline_feature(features):
    features.default_features.append('katex_inline')
    """
    Registering the `katex_inline` feature, which uses the `KATEX_I` Draft.js entity type,
    and is stored as HTML with a `<span data-katex>` tag.
    """
    feature_name = 'katex_inline'
    type_ = 'KATEX_I'

    control = {
        'type': type_,
        'label': 'Ki',
        'description': 'KaTeX Inline',
    }

    features.register_editor_plugin(
        'draftail', feature_name, draftail_features.EntityFeature(control)
    )

    features.register_converter_rule('contentstate', feature_name, {
        # Note here that the conversion is more complicated than for blocks and inline styles.
        'from_database_format': {'span[data-katex-inline]': KaTeXInlineEntityElementHandler(type_)},
        'to_database_format': {'entity_decorators': {type_: katex_inline_entity_decorator}},
    })


def katex_inline_entity_decorator(props):
    """
    Draft.js ContentState to database HTML.
    Converts the Katex entities into a span tag.
    """
    return DOM.create_element('span', {
        'class': 'katex-inline',
        'data-katex-inline': props['content']
    }, props['children'].children)


class KaTeXInlineEntityElementHandler(InlineEntityElementHandler):
    """
    Database HTML to Draft.js ContentState.
    Converts the span tag into a KATEX_I entity, with the right data.
    """
    mutability = 'IMMUTABLE'

    def get_attribute_data(self, attrs):
        """
        Take the ``content`` value from the ``data-katex-inline`` HTML attribute.
        """
        return {
            'content': attrs['data-katex-inline'],
        }


# KaTeX Display Block

@hooks.register('register_rich_text_features')
def register_katex_block_feature(features):
    features.default_features.append('katex_block')
    """
    Registering the `katex_block` feature, which uses the `KATEX_B` Draft.js entity type,
    and is stored as HTML with a `<span data-katex>` tag.
    """
    feature_name = 'katex_block'
    type_ = 'KATEX_B'

    control = {
        'type': type_,
        'label': 'Kb',
        'description': 'KaTeX Block',
    }

    features.register_editor_plugin(
        'draftail', feature_name, draftail_features.EntityFeature(control)
    )

    features.register_converter_rule('contentstate', feature_name, {
        # Note here that the conversion is more complicated than for blocks and inline styles.
        'from_database_format': {'span[data-katex-block]': KaTeXBlockEntityElementHandler(type_)},
        'to_database_format': {'entity_decorators': {type_: katex_block_entity_decorator}},
    })


def katex_block_entity_decorator(props):
    """
    Draft.js ContentState to database HTML.
    Converts the Katex entities into a span tag.
    """
    return DOM.create_element('span', {
        'class': 'katex-block',
        'data-katex-block': props['content']
    }, props['children'].children)


class KaTeXBlockEntityElementHandler(InlineEntityElementHandler):
    """
    Database HTML to Draft.js ContentState.
    Converts the span tag into a KATEX_B entity, with the right data.
    """
    mutability = 'IMMUTABLE'

    def get_attribute_data(self, attrs):
        """
        Take the ``content`` value from the ``data-katex-block`` HTML attribute.
        """
        return {
            'content': attrs['data-katex-block'],
        }


# Register KaTeX JS
@hooks.register('insert_editor_js')
def stock_editor_js():
    js_files = [
        # We require this file here to make sure it is loaded before math.js.
        'wagtailadmin/js/draftail.js',
        'js/math.js',
    ]
    return format_html_join('\n', '<script src="{0}{1}"></script>',
                            ((settings.STATIC_URL, filename) for filename in js_files))
