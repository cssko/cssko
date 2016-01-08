import random
import string
import time
import re
from time import strftime, localtime
import requests
import django
from django.core.exceptions import ObjectDoesNotExist
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support import ui
from selenium.webdriver.support.select import Select
from cssko import wsgi, settings
import win32com.client

from course_catalog.models import *


def format_time(course_hours):
    """ A function to take UCs section time format and
    :param course_hours: String containing the times for a section.
    :return:  A list containing strings start_time and end_time.
    """
    hours = course_hours.split(' - ')
    if len(hours) > 1:
        start_time = hours[0]
        end_time = hours[1]
        temp_time = ''
        for x in start_time.split(':'):
            if len(x) == 3:
                am_pm = x[2]
                if am_pm == 'p':
                    am_pm = 'pm'
                elif am_pm == 'a':
                    am_pm = 'am'
                temp_time += " " + x[:2] + " " + am_pm
            else:
                temp_time += x
        temp_time += '|'
        for x in end_time.split(':'):
            if len(x) == 3:
                am_pm = x[2]
                if am_pm == 'p':
                    am_pm = 'pm'
                elif am_pm == 'a':
                    am_pm = 'am'
                temp_time += " " + x[:2] + " " + am_pm
            else:
                temp_time += x

        times = temp_time.split('|')
        s_time = time.strftime('%H:%M', time.strptime(times[0], "%I %M %p"))
        e_time = time.strftime('%H:%M', time.strptime(times[1], "%I %M %p"))
        formatted_time = [s_time, e_time]
        return formatted_time
    else:
        return ['00:00', '00:00']


class ScheduleOfClassesScraper(object):
    def __init__(self, browser, debug=False):
        """
        :param browser: Chrome or Phantom JS
        :return:
        """
        self.debug = debug
        self.url = "https://webapps2.uc.edu/scheduleofclasses/"
        self.class_id_regex = re.compile('((?<=ClassId)[0-9]+)')
        if browser == 'chrome':
            self.path_to_chromedriver = "./chromedriver"
            self.driver = webdriver.Chrome(executable_path=self.path_to_chromedriver)
        elif browser == 'phantomjs':
            self.dcap = dict()
            self.dcap["phantomjs.page.settings.userAgent"] = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/53 "
                                                              "(KHTML, like Gecko) Chrome/15.0.87")
            self.path_to_phantomjs = './phantomjs'
            self.driver = webdriver.PhantomJS(executable_path=self.path_to_phantomjs, desired_capabilities=self.dcap)
        self.session_code = None
        self.disciplines = None
        self.term_code = None

    def select_term(self, term_index=None):
        """

        :param term_index:
        :return:
        """
        Select(self.driver.find_element_by_id('MainContent_Term')).select_by_index(term_index)
        term_name = Select(self.driver.find_element_by_id('MainContent_Term')).first_selected_option.text
        self.term_code = Select(
                self.driver.find_element_by_id('MainContent_Term')).first_selected_option.get_attribute('value')
        Term.objects.update_or_create(term_code=self.term_code, defaults={'term_name': term_name})
        return

    def select_session(self, session_index):
        """
        :param session_index:
        :return:
        """
        Select(self.driver.find_element_by_id('MainContent_TermSession')).select_by_index(session_index)
        self.session_code = Select(
                self.driver.find_element_by_id('MainContent_TermSession')).first_selected_option.get_attribute('value')
        selected_text = Select(self.driver.find_element_by_id('MainContent_TermSession')).first_selected_option.text
        Session.objects.update_or_create(session_code=self.session_code, defaults={'session_name': selected_text})
        return

    @staticmethod
    def get_disciplines(starting_discipline, full_scan):
        """
        :param starting_discipline:
        :param full_scan: Whether or not we're scanning everything or just a single section.
        :return: A list of disciplines
        """
        if full_scan:
            disciplines = [discipline.discipline for discipline in Discipline.objects.all()]
            while 1:
                if starting_discipline is not None:
                    disc = Discipline.objects.get(pk=starting_discipline)
                    index = disciplines.index(disc.discipline)
                    return disciplines[index:]
                else:
                    return disciplines
        else:
            return [Discipline.objects.get(pk=starting_discipline)]

    def scrape(self, term_index=0, session_index=2, starting_discipline=None, full_scan=False):
        """

        :param term_index: Index of desired term in term drop-down list.
        :param session_index: Index of desired session in session drop-down list.
        :param starting_discipline: The starting Discipline for a list of disciplines.
        :param full_scan:
        :return:
        """
        self.driver.get(self.url)
        self.select_term(term_index)
        self.select_session(session_index)
        disciplines = self.get_disciplines(starting_discipline, full_scan)
        for discipline in disciplines:
            if self.debug:
                print discipline.center(80, '_')
            if len(discipline) < 4:  # Here we go again, UC padding things with spaces for some unfathomable reason.
                for i in range(len(discipline), 4):
                    discipline += ' '
            try:
                Select(self.driver.find_element_by_xpath('//*[@id="MainContent_Discipline"]')).select_by_value(
                        discipline)
            except NoSuchElementException:
                continue
            self.navigate_sections()
        self.driver.quit()

    def navigate_sections(self):
        class_id_regex = re.compile('((?<=ClassId)[0-9]+)')
        time.sleep(1 + random.random())
        self.driver.find_element_by_id('MainContent_Submit').click()
        time.sleep(1 + random.random())
        rows = self.driver.find_elements_by_tag_name('tr')
        current_course = None
        current_section = None
        for row in rows[4:]:
            td = rows[int(rows.index(row))].find_elements_by_tag_name('td')
            if len(td) == 4:
                course = td[0].text.strip()
                current_course = Course.objects.get(pk=course)
                if self.debug:
                    print
                    print (str(current_course)).center(80)
                    print 'Section Number'.ljust(16), 'Format'.ljust(16), 'Professor'.ljust(16), 'Class Time'.ljust(
                            16), 'Days'.ljust(16)
                    print('-' * 80)
            if len(td) == 12:
                if td[1].text and td[2].text != ' ':
                    section_number = td[1].text
                    call_number = td[2].text
                    cm_link = td[11].find_element_by_tag_name('a').get_attribute('href')
                    try:
                        email = td[10].find_element_by_tag_name('a').get_attribute('href')[7:]
                    # using .strip('mailto:') above got overzealous in some instances, removing more characters than
                    # necessary and leading to some interesting errors.
                    except NoSuchElementException:
                        # Sometimes the professor for a section will be listed as Staff, which we can't do much with.
                        continue
                    instructor = self.get_professor(email)
                    update_data = {'course': current_course, 'section_number': section_number,
                                   'course_materials_link': cm_link, 'instructor': instructor}
                    current_section, created = Section.objects.update_or_create(pk=call_number, defaults=update_data)
                    curl_id = class_id_regex.search(((td[1].find_element_by_tag_name('a')).get_attribute('id'))).group()
                    self.save_curl(current_course, curl_id, current_section)

                self.save_section(current_course, current_section, td)

    @staticmethod
    def save_curl(course, curl_id, section):
        """ A baby sized method to save the cURL id for a section so we can go back later and politely query for Seats.

        :param course: Course object
        :param curl_id: curl_id string
        :param section: Section object
        :return:
        """
        try:
            update_data = {'course': course, 'curl_id': curl_id}
            Seats.objects.update_or_create(section=section, defaults=update_data)
        except Section.DoesNotExist:
            print('Welp. Try again later.')
        return

    def save_section(self, current_course, current_section, td):
        """

            :param current_course:
            :param current_section:
            :param td:
            :return:
            """
        course_time = format_time(td[7].text)
        update_data = {
            'section_number': current_section.section_number, 'instructor': current_section.instructor,
            'course_materials_link': current_section.course_materials_link, 'course': current_course,
            'campus': td[4].text, 'class_start': course_time[0], 'class_end': course_time[1], 'days': td[6].text,
            'class_format': td[8].text, 'classroom': td[9].text
        }
        section_term_data = {'course': current_course, 'term': Term.objects.get(pk=self.term_code)}
        section_session_data = {'course': current_course, 'session': Session.objects.get(pk=self.session_code)}
        call_number = current_section.call_number
        if td[5].text == 'LE':
            update_data['instruction_format'] = 'Lecture'
            Lecture.objects.update_or_create(call_number=call_number, defaults=update_data)
        elif td[5].text == 'LB':
            update_data['instruction_format'] = 'Lab'
            Lab.objects.update_or_create(call_number=call_number, defaults=update_data)
        elif td[5].text == 'RE':
            update_data['instruction_format'] = 'Recitation'
            Recitation.objects.update_or_create(call_number=call_number, defaults=update_data)
        elif td[5].text == 'LL':
            update_data['instruction_format'] = 'Lab/Lecture'
            LabLecture.objects.update_or_create(call_number=call_number, defaults=update_data)
        elif td[5].text == 'SE':
            update_data['instruction_format'] = 'Seminar'
            Seminar.objects.update_or_create(call_number=call_number, defaults=update_data)
        elif td[5].text == 'IS':
            update_data['instruction_format'] = 'Individual Study'
            IndividualStudy.objects.update_or_create(call_number=call_number, defaults=update_data)
        else:
            update_data['instruction_format'] = 'Other'
            update_data['format_value'] = td[5].text
            Other.objects.update_or_create(call_number=call_number, defaults=update_data)
        SectionTerm.objects.update_or_create(call_number=current_section, defaults=section_term_data)
        SectionSession.objects.update_or_create(call_number=current_section, defaults=section_session_data)

        if self.debug:
            print (update_data['section_number']).ljust(16), (update_data['instruction_format']).ljust(16),
            print (str(update_data['instructor'].alias)).ljust(16), (
                update_data['class_start'] + '-' + update_data['class_end']).ljust(16),
            print (update_data['days']).ljust(16)
        return

    def get_professor(self, email):
        """
        :param email:
        :return:
        """
        alias = email.split('@')[0]
        try:
            prof = Professor.objects.get(pk=alias)
        except Professor.DoesNotExist:
            prof = self.update_professor(alias, email)
        return prof

    def update_professor(self, alias, email):
        """

        :param alias:
        :param email:
        :return:
        """
        outlook = win32com.client.gencache.EnsureDispatch('Outlook.Application')
        user = outlook.Session.CreateRecipient(email).AddressEntry.GetExchangeUser()
        if user is None:
            user = outlook.Session.CreateRecipient(alias).AddressEntry.GetExchangeUser()

        update_data = {'last_name': user.LastName, 'first_name': user.FirstName,
                       'email': user.PrimarySmtpAddress.lower(), 'title': user.JobTitle,
                       'office_phone_number': user.BusinessTelephoneNumber, 'dep': user.Department}
        try:
            update_data['office_building'] = Building.objects.get(pk=user.OfficeLocation)
        except Building.DoesNotExist:
            update_data['office_building'] = None
        phone_search = update_data['office_phone_number'][7:].replace(' ', '')
        if phone_search != '':
            update_data = self.scrape_professor(alias, update_data, phone_search)
        obj, created = Professor.objects.update_or_create(pk=alias, defaults=update_data)
        outlook = None
        return obj

    def scrape_professor(self, alias, update_data, phone_search):
        """

        :param alias:
        :param update_data:
        :param phone_search:
        :return:
        """
        office_regex = re.compile('[A-Z ]+')
        dcap = dict()
        dcap['phantomjs.page.settings.userAgent'] = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/53"
                                                     "(KHTML, like Gecko) Chrome/15.0.87")
        prof_driver = webdriver.PhantomJS(desired_capabilities=dcap)
        for i in range(0, 3):
            # The origin of this strange for-loop is an interesting story. Initially I used all three items to search
            # for a professor; First name, last name, and phone number. But some professors do not show up if you
            # include their first name. So here we are.
            prof_driver.get('https://ucdirectory.uc.edu/FacultyStaffSearch.asp?ExpSearchFields=Y')
            prof_driver.find_element_by_name('formPriphone').send_keys(phone_search)

            # The input boxes for formLastname and formFirstname refuse to accept anything other than characters.
            if i >= 1:
                prof_driver.find_element_by_name('formLastname').send_keys(
                        re.sub("(\W)+", "", update_data['last_name']))
            if i == 2:
                prof_driver.find_element_by_name('formFirstname').send_keys(
                        re.sub("(\W)+", "", update_data['first_name']))
            prof_driver.find_element_by_name('B4').click()
            time.sleep(1 + random.random())
            rows = prof_driver.find_elements_by_tag_name('tr')[2:]
            if len(rows) == 1:
                break
            elif i == 2:  # I give up.
                return update_data

        td = rows[0].find_elements_by_tag_name('td')
        link = td[0].find_element_by_tag_name('a').get_attribute('href')
        prof_driver.get(link)
        info = prof_driver.find_element_by_tag_name('tr').find_elements_by_tag_name('font')
        if update_data['office_building'] == '':
            update_data['office_building'] = office_regex.search(info[4].text.split('\n')[0].strip()).group().strip()
        if update_data['office_building'] is not None:
            update_data['office_number'] = info[4].text.split('\n')[0].strip(
                    update_data['office_building'].building_code).strip()
        else:
            update_data['office_number'] = None
        update_data['full_name'] = info[1].text
        prof_driver.quit()
        return update_data
