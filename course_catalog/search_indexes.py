from haystack import indexes
from models import Course


class CourseIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    course_id = indexes.EdgeNgramField(model_attr='course_number')
    discipline = indexes.CharField(model_attr='discipline__discipline')
    course_title = indexes.EdgeNgramField(model_attr='course_title')
    course_description = indexes.CharField(model_attr='description')
    credit_hours = indexes.CharField(model_attr='credit_hours')
    fall_availability = indexes.CharField(model_attr='fall_availability')
    spring_availability = indexes.CharField(model_attr='spring_availability')
    summer_availability = indexes.CharField(model_attr='summer_availability')
    alt_years = indexes.CharField(model_attr='alternating_years')
    graduate_level = indexes.CharField(model_attr='graduate_level')

    def get_model(self):
        return Course

    def index_queryset(self, using=None):
        """Used when the entire index for model is updated."""
        return self.get_model().objects.all().select_related('discipline')
