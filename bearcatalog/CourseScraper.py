import re

from bs4 import BeautifulSoup
from requests_futures.sessions import FuturesSession


class CourseScraper:
    RE_EXPAND_ALL = re.compile('DERIVED_SSS_BCC_SSS_EXPAND_ALL\$')
    RE_COURSE_TITLE = re.compile('CRSE_TITLE\$')
    HEAD = "http://www.classes.catalystatuc.org"
    URL = "http://www.classes.catalystatuc.org/psc/psclass/EMPLOYEE/HRMS/c/COMMUNITY_ACCESS.SSS_BROWSE_CATLG.GBL"

    def __init__(self, letter, courses):
        self.letter = letter
        self.letter_id = "DERIVED_SSS_BCC_SSR_ALPHANUM_{0}".format(self.letter)
        self.courses = courses
        self.scraped_courses = []
        return

    def scrape_courses(self):
        f_session = FuturesSession()
        base_soup = BeautifulSoup(f_session.get(self.URL).result().text, 'lxml')
        expand_all = base_soup.find('a', id=self.RE_EXPAND_ALL)['id']
        base_form = self.populate_form(base_soup, self.letter_id)

        base_response = f_session.post(self.URL, data=base_form)
        expanded_form = self.populate_form(base_response.result(), expand_all)
        expanded_response = f_session.post(self.URL, data=expanded_form)

        for course in self.courses:
            course_form = self.populate_form(expanded_response.result(), course['expanded_id'],
                                             course['multiple_offerings'])
            course_dict_multiple = {}
            if course['multiple_offerings']:
                multiple_offering_form = self.populate_form(f_session.post(self.URL, course_form).result(), 'CAREER$0',
                                                            course['multiple_offerings'])
                multiple_offerings_response = f_session.post(self.URL, multiple_offering_form)
                course_dict_multiple = self.multiple_course_dict(multiple_offerings_response)

            response = f_session.post(self.URL, course_form)
            course_dict_base = self.course_dict(course, response)
            merged_dict = {**course_dict_base, **course_dict_multiple}
            self.scraped_courses.append(merged_dict)
        return

    @staticmethod
    def multiple_course_dict(response):
        soup = BeautifulSoup(response.result().text, 'lxml')
        c = {
            "academic_credits": soup.find(id='DERIVED_CRSECAT_UNITS_RANGE$0'),
            "prerequisites": soup.find(id='DERIVED_CRSECAT_DESCR254A$0'),
            "description": soup.find(id='SSR_CRSE_OFF_VW_DESCRLONG$0'),
            "attributes": soup.find(id='DERIVED_CRSECAT_SSR_CRSE_ATTR_LONG$0'),
        }
        for key, value in c.items():
            if value:
                c[key] = value.text
        return {k: v for k, v in c.items() if v is not None}

    @staticmethod
    def course_dict(course, response):
        soup = BeautifulSoup(response.result().text, 'lxml')

        c = {
            "academic_credits": soup.find(id='DERIVED_CRSECAT_UNITS_RANGE$0'),
            "academic_career": soup.find(id='SSR_CRSE_OFF_VW_ACAD_CAREER$0'),
            "academic_group": soup.find(id='ACAD_GROUP_TBL_DESCR$0'),
            "prerequisites": soup.find(id='DERIVED_CRSECAT_DESCR254A$0'),
            "description": soup.find(id='SSR_CRSE_OFF_VW_DESCRLONG$0'),
            "attributes": soup.find(id='DERIVED_CRSECAT_SSR_CRSE_ATTR_LONG$0'),
        }
        for key, value in c.items():
            if value:
                c[key] = value.text

        c['number'] = course.number
        c['title'] = course.title
        c['expanded_id'] = course.expanded_id
        c['multiple_offerings'] = course.multiple_offerings
        return {k: v for k, v in c.items() if v is not None}

    @staticmethod
    def populate_form(response, ICAction=None, multiple_offerings=False):
        soup = BeautifulSoup(response.text, 'lxml')
        form = {}
        for hidden_input in soup.find_all('input', type='hidden'):
            form[hidden_input['id']] = hidden_input['value']
        if ICAction:
            form['ICAction'] = ICAction
        if multiple_offerings:
            form['ICAJAX'] = 1
        return form

    def __repr__(self):
        return "{}: {}".format(self.letter, self.courses)
