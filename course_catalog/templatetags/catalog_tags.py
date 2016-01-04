from django import template
from course_catalog.models import Lecture, Lab, Recitation, Clinical, IndividualStudy, LabLecture, Seminar, Other
register = template.Library()


@register.inclusion_tag('availability_tag.html')
def availability_tag(availability):
    return {'availability': availability}


@register.inclusion_tag('section_row.html')
def section_table_row(section):
    sub = section.get_subsections()
    prof = sub[0].instructor
    campus = sub[0].campus
    return{'section': section, 'ss': sub, 'prof': prof, 'campus': campus}
