from django import template

register = template.Library()


@register.inclusion_tag('blog/disqus_comments.html', takes_context=True)
def include_comments(context):
    return {
        'disqus_page_url': context['request'].build_absolute_uri(),
        'disqus_page_identifier': context['request'].path,
    }
