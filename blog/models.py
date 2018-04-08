from django import forms
from django.db import models
from django.utils.safestring import mark_safe
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from modelcluster.fields import ParentalKey, ParentalManyToManyField
from modelcluster.contrib.taggit import ClusterTaggableManager
from taggit.models import TaggedItemBase
from wagtail.core import blocks

from wagtail.core.models import Page, Orderable
from wagtail.core.fields import RichTextField, StreamField
from wagtail.admin.edit_handlers import FieldPanel, MultiFieldPanel, InlinePanel, StreamFieldPanel
from wagtail.images.blocks import ImageChooserBlock
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.search import index
from wagtail.snippets.models import register_snippet

from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import get_formatter_by_name


@register_snippet
class BlogCategory(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    panels = [
        FieldPanel('name'),
        FieldPanel('slug'),
        FieldPanel('description')
    ]

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'blog categories'


class BlogPageTag(TaggedItemBase):
    content_object = ParentalKey(
        'BlogPage',
        related_name='tagged_items',
        on_delete=models.CASCADE
    )


class BlogTagIndexPage(Page):
    def get_context(self, request, **kwargs):
        # Filter by tag
        tag = request.GET.get('tag')
        blogpages = BlogPage.objects.filter(tags__name=tag)

        # Update template context
        context = super().get_context(request)
        context['blogpages'] = blogpages
        return context


class BlogIndexPage(Page):
    intro = RichTextField(blank=True)

    content_panels = Page.content_panels + [
        FieldPanel('intro', classname="full")
    ]

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request)
        blogs = BlogPage.objects.live()
        paginator = Paginator(blogs, 5)
        page = request.GET.get('page')
        try:
            paginated_blogs = paginator.page(page)
        except PageNotAnInteger:
            pass
        except EmptyPage:
            pass
        return context


class CodeBlock(blocks.StructBlock):
    choices = [('python', 'Python')]
    language = blocks.ChoiceBlock(choices=choices)
    code = blocks.TextBlock()

    class Meta:
        icon = 'code'

    def render(self, value, **kwargs):
        src = value['code'].strip('\n')
        lang = value['language']

        lexer = get_lexer_by_name(lang)
        formatter = get_formatter_by_name(
            'html',
            linenos=None,
            cssclass='highlight',
            style='default',
            noclasses=False,
        )
        return mark_safe(highlight(src, lexer, formatter))


class HeaderBlock(blocks.StructBlock):
    section_header = blocks.CharBlock(classname="title")

    class Meta:
        template = 'blocks/header.html'


class BlogPage(Page):
    date = models.DateField("Post date")
    intro = models.CharField(max_length=250, blank=True)
    body = StreamField([
        ('section_heading', HeaderBlock()),
        ('paragraph', blocks.RichTextBlock()),
        ('image', ImageChooserBlock()),
        ('code', CodeBlock()),
        ('html', blocks.RawHTMLBlock()),
    ])
    tags = ClusterTaggableManager(through=BlogPageTag, blank=True)
    categories = ParentalManyToManyField('blog.BlogCategory', blank=True)

    search_fields = Page.search_fields + [
        index.SearchField('intro'),
        index.SearchField('body'),
    ]

    content_panels = Page.content_panels + [
        MultiFieldPanel([
            FieldPanel('date'),
            FieldPanel('tags'),
            FieldPanel('categories', widget=forms.CheckboxSelectMultiple),
        ], heading="Blog information"),
        FieldPanel('intro'),
        StreamFieldPanel('body'),
    ]
