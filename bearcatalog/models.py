import uuid

from django.core.validators import RegexValidator
from django.db import models


class Term(models.Model):
    """
    The term code is a 4 digit code that has the following structure:

        CYTT

        Where:
            C  := Centry
            YY := Calendar Year of the Term
            T  := Month the term Begins

    e.g. The Fall Semester of 2014-15 begins in August, so the 4 digit code is 2148

    source: https://www.uc.edu/catalyst/term-structure.html
    """
    code = models.PositiveSmallIntegerField(primary_key=True)
    season = models.CharField(max_length=6, choices=(
        ('Spring', 'Spring'), ('Summer', 'Summer'), ('Fall', 'Fall')
    ))
    year = models.PositiveSmallIntegerField()
    start_date = models.DateField()
    end_date = models.DateField()

    def __str__(self):
        return "{} {} Semester".format(self.season, self.year)


class Building(models.Model):
    """
    I am guilty of wishing I could mess around with campus GIS data.
    """
    building_code = models.CharField(primary_key=True, max_length=25)
    name = models.CharField(max_length=50)
    address = models.CharField(max_length=100)
    campus = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Professor(models.Model):
    full_name = models.CharField(max_length=150)
    title = models.CharField(max_length=100, blank=True, default=None)
    internal_id = models.CharField(default=None, max_length=50, blank=True, unique=True)
    email = models.EmailField(default=None, blank=True, unique=True)
    six_plus_two = models.CharField(default=None, max_length=8, blank=True, unique=True)
    search_first_name = models.CharField(max_length=75, default=None, blank=True)
    search_last_name = models.CharField(max_length=75, default=None, blank=True)
    office_phone_number = models.CharField(max_length=15, null=True)
    office_number = models.CharField(max_length=25, null=True)


class Subject(models.Model):
    short_name = models.CharField(max_length=5, primary_key=True)
    long_name = models.CharField(max_length=50)
    last_scraped = models.DateTimeField(null=True)

    def __str__(self):
        return self.short_name


class Course(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    number = models.CharField(max_length=6)
    title = models.CharField(max_length=100)
    multiple_offerings = models.BooleanField()
    academic_credits = models.CharField(max_length=25, null=True, blank=True)
    academic_career = models.CharField(max_length=50, null=True, blank=True)
    academic_group = models.CharField(max_length=50, null=True, blank=True)
    prerequisites = models.TextField(null=True, blank=True)
    description = models.TextField(default='No description found.')
    attributes = models.TextField(null=True, blank=True)
    expanded_id = models.CharField(max_length=25, default=None, null=True)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "{} {} - {}".format(self.subject, self.number, self.title)

    class Meta:
        unique_together = ('subject', 'number')


# class Section(models.Model):
#     pass


class TopLevelCatalog(models.Model):
    """
    This is used purely for scraping purposes. It essentially holds basic information that can be gleaned
    from the main page of the PeopleSoft course catalog. This information is then used as follows:

    expanded_id is used in post requests to the catalog site
    multiple offerings is used to determine how the post request is made

    everything else is used to compare to the data returned by the post request
    """
    short = models.CharField(max_length=25)  # This will be something like FAA
    long = models.CharField(max_length=255)  # This is FAA spelled out like so: Fine Arts - Arts
    number = models.CharField(max_length=25)  # This is the equivalent of the Course field number
    expanded_id = models.CharField(max_length=25)
    title = models.CharField(max_length=255)  # Course field title
    # If a course has multiple offerings, it is available at multiple campuses at the university.
    # This changes the way we have to scrape its data.
    multiple_offerings = models.BooleanField(default=False)

    def __str__(self):
        return "{}{} - {}".format(self.short, self.number, self.title)

    class Meta:
        verbose_name = 'TLC Entry'
        verbose_name_plural = 'TLC Entries'
        # Force some kind of uniqueness on these keys to keep from having multiple copies in the DB
        unique_together = ('short', 'number')


class Letter(models.Model):
    """
    I'm essentially using this as a deque that is stored in the postgres database. Dirty but it works.
    """
    letter = models.CharField(max_length=1, primary_key=True)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "{}".format(self.letter)