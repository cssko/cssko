from celery import shared_task
from django.db import DataError
from django.utils import timezone

# Scraping specific imports
from .models import TopLevelCatalog, Letter, Subject, Course
from .CourseScraper import CourseScraper
import re

import requests
from bs4 import BeautifulSoup
from requests_futures.sessions import FuturesSession

EXPAND_ALL = re.compile('DERIVED_SSS_BCC_SSS_EXPAND_ALL\$')
BROWSE_URL = "http://www.classes.catalystatuc.org/psc/psclass/EMPLOYEE/HRMS/c/COMMUNITY_ACCESS.SSS_BROWSE_CATLG.GBL"


# TODO: Rename this
@shared_task
def _scrape(subject_string=None):
    if subject_string:
        subject = Subject.objects.get(short_name=subject_string)
    else:
        subject = Subject.objects.filter(last_scraped=None).first()
        if subject is None:
            subject = Subject.objects.earliest('last_scraped')
    # Set the last scraped time to now, to help prevent overlapping attempts to scrape the same subject.
    # This is a less than ideal fix.
    subject.last_scraped = timezone.now()
    subject.save()
    catalog = TopLevelCatalog.objects.filter(short=subject.short_name)
    letter = "DERIVED_SSS_BCC_SSR_ALPHANUM_{0}".format(subject.short_name[0])

    with FuturesSession() as session:
        base_soup = BeautifulSoup(session.get(BROWSE_URL).result().text, 'lxml')
        base_form = CourseScraper.populate_form(base_soup, letter)
        base_response = session.post(BROWSE_URL, data=base_form)
        soup = BeautifulSoup(base_response.result().text, 'lxml')
        subject_div = soup.find('a', string=re.compile("{} - ".format(subject.short_name)))
        if subject_div:
            expanded_form = CourseScraper.populate_form(base_response.result(), subject_div['id'])
            expanded_response = session.post(BROWSE_URL, data=expanded_form).result()

            for course in catalog:
                course_form = CourseScraper.populate_form(expanded_response, course.expanded_id,
                                                          course.multiple_offerings)

                multiple_dict = {}
                if course.multiple_offerings:
                    multiple_offering_form = CourseScraper.populate_form(session.post(BROWSE_URL, course_form).result(),
                                                                         'CAREER$0', course.multiple_offerings)
                    multiple_dict = CourseScraper.multiple_course_dict(session.post(BROWSE_URL, multiple_offering_form))

                response = session.post(BROWSE_URL, course_form)
                course_dict = CourseScraper.course_dict(course, response)

                merged_dict = {**course_dict, **multiple_dict}

                try:
                    Course.objects.update_or_create(subject=subject, number=merged_dict['number'],
                                                    defaults=merged_dict)
                except DataError as e:
                    print(e)  # ????
            subject.last_scraped = timezone.now()
            subject.save()
            return "SCRAPED {}: {} ({} courses) @{}.".format(subject.short_name, subject.long_name, len(catalog),
                                                             timezone.now())
        else:
            return


@shared_task
def update_tlc():
    letter = Letter.objects.earliest('last_updated')
    letter.save()  # In the event of overlap during scheduled tasks.
    with FuturesSession() as session:
        base_soup = BeautifulSoup(session.get(BROWSE_URL).result().text, 'lxml')
        base_response = session.post(BROWSE_URL, data=CourseScraper.populate_form(base_soup,
                                                                                  "DERIVED_SSS_BCC_SSR_ALPHANUM_{0}"
                                                                                  .format(letter.letter)))

        response_soup = BeautifulSoup(base_response.result().text, 'lxml')

        for group in response_soup.select('a[id^="DERIVED_SSS_BCC_GROUP_BOX_1$147$"]'):

            form = CourseScraper.populate_form(base_response.result(), group['id'])
            response = session.post(BROWSE_URL, data=form).result().text
            soup = BeautifulSoup(response, 'lxml')
            x = soup.find(id=group['id']).find_parent('table', class_='PABACKGROUNDINVISIBLEWBO')
            try:
                subject = x.find("td", class_="PAGROUPBOXLABELINVISIBLE").text
                short = re.match("^[0-Z]{2,4}(?= - )", subject)
                if short:
                    short = short.group()
                else:  # Peoplesoft, why are you doing this to me? Why? Who hurt you?
                    continue
                if short in ["MED1", "MED2", "MED3", "MED4"]:
                    # University of Medicine can go straight to hell, their formatting breaks everything.
                    continue

                long = subject[2 * len(short) + 4:]
                course_div = x.select("tr[id^='trCOURSE_LIST']")

                for course in course_div:
                    a_tags = course.find_all('a')
                    course_id = a_tags[0].text
                    title = re.sub('\s+', ' ', a_tags[1].text).strip()  # Dump all the extra whitespace in some titles
                    multiple_offerings = False

                    if course_id.find("(") >= 0:
                        course_id = course_id.strip("(").strip(")")
                    if title.find("**") > 0:
                        if re.search("\*\*\* view multiple off", title):
                            multiple_offerings = True
                        title = title[:title.find("**")]

                    TopLevelCatalog.objects.update_or_create(
                        short=short, number=course_id,
                        defaults={'long': long, 'title': title, 'expanded_id': a_tags[1]['id'],
                                  'multiple_offerings': multiple_offerings}
                    )
            except ValueError or AttributeError as e:
                print(e)
                continue
            base_response = session.post(BROWSE_URL, data=CourseScraper.populate_form(base_soup,
                                                                                      "DERIVED_SSS_BCC_SSR_ALPHANUM_{0}"
                                                                                      .format(letter.letter)))

    letter.save()
    return letter.letter


@shared_task
def update_subjects():
    SEARCH_URL = "http://www.classes.catalystatuc.org/psc/psclass/EMPLOYEE/HRMS/c/COMMUNITY_ACCESS.CLASS_SEARCH.GBL"

    base_soup = BeautifulSoup(requests.get(SEARCH_URL).text, 'lxml')
    options = base_soup.select("#SSR_CLSRCH_WRK_SUBJECT_SRCH\$0")[0].find_all('option')[1:]
    subjects = [{'short': option['value'], 'long': option.text.strip(option['value']).strip()} for option in options]

    for subject in subjects:
        Subject.objects.update_or_create(short_name=subject['short'],
                                         defaults={'short_name': subject['short'], 'long_name': subject['long']})
    return