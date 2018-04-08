from collections import OrderedDict

from django.shortcuts import render
from django.http import HttpResponse, Http404
from django.shortcuts import render
from django.template import RequestContext
from django.views import View
from django.utils.translation import ugettext as _
from django.views.generic import TemplateView, DetailView, ListView
from django.db.models import Count

from .models import Subject, Course


# Create your views here.
class CatalogView(TemplateView):
    template_name = 'bearcatalog.html'

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)

        l_g = OrderedDict([
            ('{}-{}'.format(group[0], group[1]), OrderedDict([
                (letter,
                 list(Subject.objects.filter(short_name__startswith=letter).annotate(course_count=Count('course'))))
                for letter in group
            ])) for group in ['ABCD', 'EFGHI', 'JKLM', 'NOPQR', 'STUV', 'WXYZ']
        ])

        a = {
            '{}-{}'.format(group[0], group[-1]):
                OrderedDict([
                    (letter,
                     list(Subject.objects.filter(short_name__startswith=letter)
                          .annotate(course_count=Count('course'))
                          .order_by('short_name')))
                    for letter in group
                ])
            for group in ['ABCD', 'EFGHI', 'JKLM', 'NOPQR', 'STUV', 'WXYZ']
        }

        context['subjects'] = sorted(a.items())
        return self.render_to_response(context)


def subject(request, pk):
    _subject = Subject.objects.get(pk=pk)
    courses = Course.objects.filter(subject_id=_subject)
    return render(request, 'subject.html', context={'subject': _subject, 'courses': courses})


class CourseView(DetailView):
    model = Course
    template_name = 'course.html'
    pk_url_kwarg = 'number'

    def get_object(self, queryset=None):
        """
        Returns the object the view is displaying.

        By default this requires `self.queryset` and a `pk` or `slug` argument
        in the URLconf, but subclasses can override this to return any object.
        """
        # Use a custom queryset if provided; this is required for subclasses
        # like DateDetailView
        if queryset is None:
            queryset = self.get_queryset()

        # Next, try looking up by primary key.
        pk = self.kwargs.get(self.pk_url_kwarg)
        slug = self.kwargs.get(self.slug_url_kwarg)
        if pk is not None:
            queryset = queryset.filter(number=pk, subject_id=self.kwargs.get('subject'))

        # Next, try looking up by slug.
        if slug is not None and (pk is None or self.query_pk_and_slug):
            slug_field = self.get_slug_field()
            queryset = queryset.filter(**{slug_field: slug})

        # If none of those are defined, it's an error.
        if pk is None and slug is None:
            raise AttributeError("Generic detail view %s must be called with "
                                 "either an object pk or a slug."
                                 % self.__class__.__name__)

        try:
            # Get the single item from the filtered queryset
            obj = queryset.get()
        except queryset.model.DoesNotExist:
            raise Http404(_("No %(verbose_name)s found matching the query") %
                          {'verbose_name': queryset.model._meta.verbose_name})
        return obj

    def get_queryset(self):
        qs = super(CourseView, self).get_queryset()
        filtered_qs = qs.filter(subject=self.kwargs['subject'], number=self.kwargs['number'])
        return filtered_qs
