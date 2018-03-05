from datetime import date
import string

from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Course, Subject, TopLevelCatalog, Term


class CourseAdminListFilter(admin.SimpleListFilter):
    title = _('Letter')

    parameter_name = 'letter'

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """
        return (
            (l, _(l)) for l in string.ascii_uppercase
        )

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        if self.value():
            return queryset.filter(subject__short_name__startswith=self.value())
        else:
            return queryset


class TLCAdminListFilter(admin.SimpleListFilter):
    title = _('Letter')

    parameter_name = 'letter'

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """
        return (
            (l, _(l)) for l in string.ascii_uppercase
        )

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        if self.value():
            return queryset.filter(short__startswith=self.value())
        else:
            return queryset


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_filter = (CourseAdminListFilter,)
    list_display = ('__str__', 'last_updated')
    ordering = ('subject__short_name', 'number', 'last_updated')


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('short_name', 'long_name', 'last_scraped')
    ordering = ('short_name',)


@admin.register(Term)
class TermAdmin(admin.ModelAdmin):
    list_display = ('__str__',)


@admin.register(TopLevelCatalog)
class TLCAdmin(admin.ModelAdmin):
    list_filter = ('multiple_offerings', TLCAdminListFilter)
    list_display = ('__str__', 'expanded_id', 'multiple_offerings')
    ordering = ('short', 'number')
