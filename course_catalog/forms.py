from django import forms
from haystack.forms import FacetedSearchForm

from course_catalog.models import Term


BY_CHOICES = [('id', 'Course ID'), ('disc', 'Discipline'), ('title', 'Course Title'),
              ('desc', 'Course Description'), ('all', 'all')]
ORDER_CHOICES = [('id', 'Course ID'), ('disc', 'discipline')]
GRAD_CHOICES = [('both', 'Both'), ('undergrad', 'Undergraduate'), ('grad', 'Graduate')]


class CourseSearchForm(FacetedSearchForm):
    q = forms.CharField(required=False)
    i = forms.ChoiceField(required=False, choices=BY_CHOICES)
    sort = forms.ChoiceField(required=False, choices=ORDER_CHOICES)
    grad = forms.ChoiceField(required=False, choices=GRAD_CHOICES)

    def search(self):
        sqs = super(CourseSearchForm, self).search()

        if not self.is_valid():
            return self.no_query_found()
        q = self.cleaned_data['q']
        i = self.cleaned_data['i']
        sort = self.cleaned_data['sort']
        grad = self.cleaned_data['grad']

        if i != '':
            if i == 'id':
                sqs = sqs.filter(course_id__startswith=q)
            # if i == 'disc':
            #     sqs = sqs.filter(discipline_exact=string.upper(q))
            if i == 'title':
                sqs = sqs.filter(course_title=q)
            if i == 'desc':
                sqs = sqs.filter(course_description=q)
            if i == 'all':
                pass

        if sort != '':
            if sort == 'id':
                sqs = sqs.order_by('id')
            if sort == 'disc':
                sqs = sqs.order_by('discipline')

        if grad != '':
            if grad == 'both':
                pass
            if grad == 'undergrad':
                sqs = sqs.filter(graduate_level='undergraduate')
            if grad == 'grad':
                sqs = sqs.filter(graduate_level='graduate')

        return sqs.facet('discipline')


class CourseTermForm(forms.Form):
    term = forms.ChoiceField(required=False,
                             choices=tuple((i.term_code, i.term_name) for i in (Term.objects.all())))

    def get_term(self):
        term = self.cleaned_data['term']
        return term
