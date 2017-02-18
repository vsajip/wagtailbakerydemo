from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db import models

from wagtail.wagtailadmin.edit_handlers import FieldPanel, StreamFieldPanel
from wagtail.wagtailcore.fields import StreamField
from wagtail.wagtailcore.models import Page

from wagtail.wagtailcore import blocks
from wagtail.wagtailimages.edit_handlers import ImageChooserPanel
from wagtail.wagtailsearch import index
from wagtail.wagtailsnippets.models import register_snippet

from bakerydemo.base.models import BasePageFieldsMixin


@register_snippet
class Country(models.Model):
    """
    Standard Django model to store set of countries of origin.
    Exposed in the Wagtail admin via Snippets.
    """

    title = models.CharField(max_length=100)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name_plural = "Countries of Origin"


@register_snippet
class BreadType(models.Model):
    """
    Standard Django model used as a Snippet in the BreadPage model.
    """

    title = models.CharField(max_length=255)

    panels = [
        FieldPanel('title'),
    ]

    def __str__(self):
        return self.title

    class Meta:
        verbose_name_plural = "Bread types"


class BreadPage(Page):
    """
    Detail view for a specific bread
    """

    origin = models.ForeignKey(
        Country,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    description = StreamField([
        ('heading', blocks.CharBlock(classname="full title")),
        ('paragraph', blocks.RichTextBlock()),
    ])
    bread_type = models.ForeignKey(
        'breads.BreadType',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    image = models.ForeignKey(
        'wagtailimages.Image',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='+',
        help_text='Landscape mode only; horizontal width between 1000px and 3000px.'
    )

    content_panels = [
        FieldPanel('title'),
        FieldPanel('origin'),
        FieldPanel('bread_type'),
        ImageChooserPanel('image'),
        StreamFieldPanel('description'),
    ]

    search_fields = Page.search_fields + [
        index.SearchField('title'),
        index.SearchField('description'),
    ]

    parent_page_types = ['BreadsIndexPage']

    api_fields = ['title', 'bread_type', 'origin', 'image']


class BreadsIndexPage(BasePageFieldsMixin, Page):
    """
    Index page for breads. We don't have any fields within our model but we need
    to alter the page model's context to return the child page objects - the
    BreadPage - so that it works as an index page
    """

    subpage_types = ['BreadPage']

    def get_context(self, request):
        context = super(BreadsIndexPage, self).get_context(request)

        # Get the full unpaginated listing of resource pages as a queryset -
        # replace this with your own query as appropriate
        all_resources = self.get_children().live()

        paginator = Paginator(all_resources, 5)  # Show 5 resources per page

        page = request.GET.get('page')
        try:
            resources = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            resources = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            resources = paginator.page(paginator.num_pages)

        # make the variable 'resources' available on the template
        context['resources'] = resources
        context['paginator'] = paginator
        return context
