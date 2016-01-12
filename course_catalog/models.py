from __future__ import unicode_literals
from django.db import models, connection


class DisciplineManager(models.Manager):
    def with_course_counts(self):
        """ Modified version of the django example on managers. Thanks django.
        :return: List of Disciplines with added field course_count.
        """
        cursor = connection.cursor()
        cursor.execute("SELECT d.discipline, d.name, COUNT(*) "
                       "FROM course_catalog_discipline d, course_catalog_course c "
                       "WHERE d.discipline = c.discipline_id "
                       "GROUP BY d.discipline, d.name "
                       "ORDER BY d.discipline ASC")
        result_list = []
        for row in cursor.fetchall():
            p = self.model(discipline=row[0], name=row[1])
            p.course_count = row[2]
            result_list.append(p)
        return result_list


class CourseManager(models.Manager):
    def with_section_counts(self, discipline, grad_level):
        """ Modified version of the django example on managers. Thanks django.
        :param discipline:
        :param grad_level:
        :return: List of Courses with added field section_count.
        """

        result_list = []
        cursor = connection.cursor()
        cursor.execute("SELECT "
                       "c.course_number, "
                       "c.discipline_id, "
                       "c.course_title, "
                       "c.description, "
                       "c.credit_hours, "
                       "c.fall_availability, "
                       "c.spring_availability, "
                       "c.summer_availability, "
                       "c.alternating_years, "
                       "c.graduate_level, "
                       "COUNT(s.course_id)"
                       "FROM course_catalog_course c LEFT JOIN course_catalog_section s "
                       "ON c.course_number = s.course_id WHERE c.discipline_id = (?) AND c.graduate_level = (?) "
                       "GROUP BY c.course_number, c.discipline_id ORDER BY c.course_number ASC",
                       (discipline, grad_level))
        for row in cursor.fetchall():
            c = self.model(course_number=row[0],
                           discipline_id=row[1],
                           course_title=row[2],
                           description=row[3],
                           credit_hours=row[4],
                           fall_availability=row[5],
                           spring_availability=row[6],
                           summer_availability=row[7],
                           alternating_years=row[8],
                           graduate_level=row[9])
            c.section_count = row[10]
            result_list.append(c)
        return result_list

    def get_term_counts(self, grad_level, course_id):
        term_counts = {}
        cursor = connection.cursor()
        cursor.execute("SELECT s.term, count(*) "
                       "FROM course_catalog_course c LEFT JOIN course_catalog_section s "
                       "ON c.course_number = s.course_id "
                       "WHERE c.graduate_level = (?) AND s.term NOTNULL AND s.course_id = (?)"
                       "GROUP BY s.term", (grad_level, course_id))

        for row in cursor.fetchall():
            term_counts[row[0]] = row[1]
        return term_counts


class Discipline(models.Model):
    discipline = models.CharField(primary_key=True, max_length=25)
    name = models.CharField(max_length=50)

    objects = DisciplineManager()

    def __unicode__(self):
        return self.name


class Course(models.Model):
    course_number = models.CharField(primary_key=True, max_length=10)
    discipline = models.ForeignKey(Discipline)
    course_title = models.CharField(max_length=100)
    description = models.CharField(max_length=250)
    credit_hours = models.CharField(max_length=10)
    fall_availability = models.CharField(max_length=15)
    spring_availability = models.CharField(max_length=15)
    summer_availability = models.CharField(max_length=15)
    alternating_years = models.CharField(max_length=15)
    graduate_level = models.CharField(max_length=15)
    last_updated = models.DateTimeField(auto_now=True)

    objects = CourseManager()

    def __unicode__(self):
        return self.course_number


class Term(models.Model):
    term_name = models.CharField(max_length=50)
    term_code = models.CharField(max_length=50, primary_key=True)

    def __unicode__(self):
        return self.term_name


class Session(models.Model):
    session_name = models.CharField(max_length=50)
    session_code = models.CharField(max_length=50, primary_key=True)

    def __unicode__(self):
        return self.session_name


class College(models.Model):
    short_name = models.CharField(primary_key=True, max_length=25)
    long_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15)
    website = models.URLField()

    def __unicode__(self):
        return self.long_name


class Building(models.Model):
    building_code = models.CharField(primary_key=True, max_length=25)
    name = models.CharField(max_length=50)
    address = models.CharField(max_length=100)
    campus = models.CharField(max_length=50)

    def __unicode__(self):
        return self.name


class Department(models.Model):
    name = models.CharField(primary_key=True, max_length=50)
    department_code = models.CharField(max_length=10)
    phone_number = models.CharField(max_length=25)
    fax_number = models.CharField(max_length=25)
    building = models.ForeignKey(Building)
    room_number = models.CharField(max_length=15)
    web_site = models.URLField()
    email = models.EmailField()


class Professor(models.Model):
    alias = models.CharField(primary_key=True, max_length=25)
    email = models.EmailField()
    last_name = models.CharField(max_length=25)
    first_name = models.CharField(max_length=25)
    full_name = models.CharField(max_length=100, null=True)
    title = models.CharField(max_length=50, default='')
    office_phone_number = models.CharField(max_length=15, null=True)
    office_number = models.CharField(max_length=25, null=True)
    office_building = models.ForeignKey(Building, null=True)
    # department = models.ForeignKey(Department, null=True)
    dep = models.CharField(max_length=100, default='')

    def __unicode__(self):
        return '%s %s' % (self.first_name, self.last_name)


class Section(models.Model):
    CLASS_CHOICES = (
        ('CI', 'Classroom'),
        ('IN', 'Individual'),
        ('WB', 'Web')
    )
    course = models.ForeignKey(Course)
    call_number = models.IntegerField(primary_key=True)
    section_number = models.IntegerField()
    course_materials_link = models.URLField(null=True)
    instructor = models.ForeignKey(Professor, null=True)

    def __unicode__(self):
        return unicode(self.course_id) + ": " + unicode(self.call_number)

    def get_subsections(self):
        """
        Forgive me Guido, for I have sinned.
        :return: List of Subsections for a section. This could be things like Lectures, Labs, etc.
        """
        ss = ['self.lecture', 'self.lab', 'self.recitation', 'self.clinical',
              'self.individualstudy', 'self.lablecture', 'self.seminar', 'self.other']
        exc = ['Lecture.DoesNotExist', 'Lab.DoesNotExist', 'Recitation.DoesNotExist', 'Clinical.DoesNotExist',
               'IndividualStudy.DoesNotExist', 'LabLecture.DoesNotExist', 'Seminar.DoesNotExist', 'Other.DoesNotExist']
        subsections = []

        for command, error in zip(ss, exc):
            try:
                sub = eval(command)
                subsections.append(sub)
            except eval(error):
                pass

        return subsections


class SectionTerm(models.Model):
    term = models.ForeignKey(Term)
    course = models.ForeignKey(Course)
    call_number = models.OneToOneField(Section, primary_key=True)


class SectionSession(models.Model):
    session = models.ForeignKey(Session)
    course = models.ForeignKey(Course)
    call_number = models.OneToOneField(Section, primary_key=True)


class Lecture(Section):
    instruction_format = models.CharField(max_length=25, default='Lecture')
    class_format = models.CharField(max_length=2, choices=Section.CLASS_CHOICES)
    days = models.CharField(max_length=10)
    class_start = models.TimeField()
    class_end = models.TimeField()
    campus = models.CharField(max_length=50)
    classroom = models.CharField(max_length=50, blank=True)


class Lab(Section):
    instruction_format = models.CharField(max_length=25, default='Lab')
    class_format = models.CharField(max_length=2, choices=Section.CLASS_CHOICES)
    days = models.CharField(max_length=10)
    class_start = models.TimeField()
    class_end = models.TimeField()
    campus = models.CharField(max_length=50)
    classroom = models.CharField(max_length=50, blank=True)


class Recitation(Section):
    instruction_format = models.CharField(max_length=25, default='Recitation')
    class_format = models.CharField(max_length=2, choices=Section.CLASS_CHOICES)
    days = models.CharField(max_length=10)
    class_start = models.TimeField()
    class_end = models.TimeField()
    campus = models.CharField(max_length=50)
    classroom = models.CharField(max_length=50, blank=True)


class Clinical(Section):
    instruction_format = models.CharField(max_length=25, default='Clinical')
    class_format = models.CharField(max_length=2, choices=Section.CLASS_CHOICES)
    days = models.CharField(max_length=10)
    class_start = models.TimeField()
    class_end = models.TimeField()
    campus = models.CharField(max_length=50)
    classroom = models.CharField(max_length=50, blank=True)


class IndividualStudy(Section):
    instruction_format = models.CharField(max_length=25, default='Individual Study')
    class_format = models.CharField(max_length=2, choices=Section.CLASS_CHOICES)
    days = models.CharField(max_length=10)
    class_start = models.TimeField()
    class_end = models.TimeField()
    campus = models.CharField(max_length=50)
    classroom = models.CharField(max_length=50, blank=True)


class LabLecture(Section):
    instruction_format = models.CharField(max_length=25, default='Lab/Lecture')
    class_format = models.CharField(max_length=2, choices=Section.CLASS_CHOICES)
    days = models.CharField(max_length=10)
    class_start = models.TimeField()
    class_end = models.TimeField()
    campus = models.CharField(max_length=50)
    classroom = models.CharField(max_length=50, blank=True)


class Seminar(Section):
    instruction_format = models.CharField(max_length=25, default='Seminar')
    class_format = models.CharField(max_length=2, choices=Section.CLASS_CHOICES)
    days = models.CharField(max_length=10)
    class_start = models.TimeField()
    class_end = models.TimeField()
    campus = models.CharField(max_length=50)
    classroom = models.CharField(max_length=50, blank=True)


class Other(Section):
    FORMAT_CHOICES = (
        ('B2', 'Lab #2 (experiments, perfect skills, practice)'),
        ('B3', 'Lab #3 (experiments, perfect skills, practice)'),
        ('B4', 'Lab #4 (experiments, perfect skills, practice)'),
        ('B5', 'Lab #5 (experiments, perfect skills, practice)'),
        ('B6', 'Lab #6 (experiments, perfect skills, practice)'),
        ('B7', 'Lab #7 (experiments, perfect skills, practice)'),
        ('B8', 'Lab #8 (experiments, perfect skills, practice)'),
        ('CL', 'Clinical (lab meeting in health-related facility)'),
        ('DI', 'Discussion (used most often with a lab)'),
        ('FE', 'Field Experience (paid work activity, e.g. co-op)'),
        ('IS', 'Individual Studies'),
        ('L2', 'Lecture #2 (formalized instruction)'),
        ('L3', 'Lecture #3 (formalized instruction)'),
        ('L4', 'Lecture #4 (formalized instruction)'),
        ('L5', 'Lecture #5 (formalized instruction)'),
        ('L6', 'Lecture #6 (formalized instruction)'),
        ('L7', 'Lecture #7 (formalized instruction)'),
        ('L8', 'Lecture #8 (formalized instruction)'),
        ('LB', 'Laboratory (experiments, perfect skills, practice)'),
        ('LE', 'Lecture (formalized instruction)'),
        ('LL', 'Lecture and Laboratory'),
        ('OT', 'Other (not described by other categories)'),
        ('PR', 'Practicum (on or off-campus work experience)'),
        ('RE', 'Recitation (small breakout groups with lecture)'),
        ('S2', 'Seminar #2 (small,less formal than lect/discussn)'),
        ('S3', 'Seminar #3 (small,less formal than lect/discussn)'),
        ('S4', 'Seminar #4 (small,less formal than lect/discussn)'),
        ('S5', 'Seminar #5 (small,less formal than lect/discussn)'),
        ('S6', 'Seminar #6 (small,less formal than lect/discussn)'),
        ('S7', 'Seminar #7 (small,less formal than lect/discussn)'),
        ('S8', 'Seminar #8 (small,less formal than lect/discussn)'),
        ('SE', 'Seminar (small,less formal than lect/discussion)'),
        ('SP', 'Self-paced (include independent learning)'),
        ('ST', 'Studio (music, performance art & theater courses)'),
        ('TU', 'Tutorial (individuals/groups tutored by faculty)'),
    )
    instruction_format = models.CharField(max_length=25, default='Other')
    format_value = models.CharField(max_length=5, choices=FORMAT_CHOICES)
    class_format = models.CharField(max_length=2, choices=Section.CLASS_CHOICES)
    days = models.CharField(max_length=10)
    class_start = models.TimeField()
    class_end = models.TimeField()
    campus = models.CharField(max_length=50)
    classroom = models.CharField(max_length=50, blank=True)


class Seats(models.Model):
    course = models.ForeignKey(Course)
    section = models.ForeignKey(Section)
    total_seats = models.IntegerField(null=True)
    seats_available = models.IntegerField(null=True)
    current_enrollment = models.IntegerField(null=True)
    course_open = models.NullBooleanField(null=True)
    last_updated = models.DateTimeField(auto_now=True)
    curl_id = models.IntegerField()

    class Meta:
        unique_together = ('course', 'section')
