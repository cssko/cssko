from django.shortcuts import render, get_object_or_404
from django.template import RequestContext
from django.views.generic import ListView, DetailView
from django.views.generic.edit import FormMixin

from course_catalog.forms import CourseSearchForm, CourseTermForm
from course_catalog.models import Discipline, Course, Section, Term, Professor


class CourseSectionsView(ListView, FormMixin):
    template_name = 'sections.html'
    form_class = CourseTermForm
    initial = {'term': '2016B02'}
    terms = Term.objects.all()

    def get_queryset(self):
        self.form = self.form_class(self.request.GET)
        if self.form.is_valid():
            self.current_term = self.form.get_term()
        else:
            self.current_term = '2016B02'
        self.course = get_object_or_404(Course, course_number=self.kwargs['course'])
        self.sections = Section.objects.filter(course_id=self.course).prefetch_related(
                'lecture', 'lab', 'recitation', 'lablecture', 'seminar', 'clinical', 'individualstudy', 'other',
                'sectionterm').filter(sectionterm__term_id=self.current_term).extra(
                select={
                    'total_seats': 'SELECT total_seats FROM course_catalog_seats WHERE course_catalog_seats.section_id = course_catalog_section.call_number',
                    'seats_available': 'SELECT seats_available FROM course_catalog_seats WHERE course_catalog_seats.section_id = course_catalog_section.call_number',
                    'current_enrollment': 'SELECT current_enrollment FROM course_catalog_seats WHERE course_catalog_seats.section_id = course_catalog_section.call_number',
                    'course_open': 'SELECT course_open FROM course_catalog_seats WHERE course_catalog_seats.section_id = course_catalog_section.call_number',
                    'last_updated': 'SELECT last_updated FROM course_catalog_seats WHERE course_catalog_seats.section_id = course_catalog_section.call_number',
                })

        return self.sections

    def get_context_data(self, **kwargs):
        context = super(CourseSectionsView, self).get_context_data(**kwargs)
        context['course'] = self.course
        context['terms'] = self.terms
        context['sections'] = self.sections
        if self.current_term:
            context['current_term'] = Term.objects.get(pk=self.current_term)
        return context


def catalog_index_view(request):
    """ The index view, contains a search box and a tabbed list of disciplines separated alphabetically.
    :param request:
    :return:
    """
    if request.GET.get('q'):
        form = CourseSearchForm(request.GET, {'user': request.user.groups})
        sq = form.search()
        query = form.cleaned_data['q']
        search_in = form.cleaned_data['i']
        sort = form.cleaned_data['sort']
        grad = form.cleaned_data['grad']
        facets = sq.facet_counts()

        return render(request, "search_results.html",
                      RequestContext(request,
                                     {'query': query, 'sq': sq, 'form': form, 'i': search_in,
                                      'sort': sort, 'grad': grad, 'facets': facets}))
    else:
        disciplines = Discipline.objects.with_course_counts()
        letter_groups = ['ABCD', 'EFGHI', 'JKLM', 'NOPQR', 'STUV', 'WXYZ']

        tab_groups = []
        for group in letter_groups:
            dis_grp = []
            for l in group:
                disc = []
                for d in disciplines:
                    if d.discipline.startswith(l):
                        disc.append(d)
                dis_grp.append({'letter': l, 'disciplines': disc})
            tab_groups.append(dis_grp)

        return render(request, 'catalog.html',
                      RequestContext(request, {'tabs': tab_groups}))


def discipline_courses_view(request, discipline):
    """ A view for the courses in a discipline.

    :param request:
    :param discipline:
    :return:
    """

    disc = Discipline.objects.get(pk=discipline)
    undergrad = Course.objects.with_section_counts(discipline=discipline, grad_level='undergraduate')
    grad = Course.objects.with_section_counts(discipline=discipline, grad_level='graduate')
    return render(request, 'courses_table.html',
                  RequestContext(request, {'discipline': disc, 'grad': grad, 'undergrad': undergrad}))


def discipline_table(request):
    """ A view for a simple table of disciplines.
    :param request:
    :return:
    """
    disciplines = Discipline.objects.with_course_counts()
    return render(request, 'discipline_table.html', RequestContext(request, {'disciplines': disciplines}))
