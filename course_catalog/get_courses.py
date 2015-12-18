import random
import django
import time

from django.core.exceptions import ObjectDoesNotExist
from django.db.models import query

from cssko import wsgi, settings
from course_catalog.models import Discipline, Course

from selenium.common.exceptions import NoSuchElementException
from selenium import webdriver
from selenium.webdriver.support.select import Select


# TODO Make this a callable class for less efforts sake
# TODO Make this UNIX friendly w/r/t chromedriver/phantomjs
def save_or_update_course(course_id, discipline, course_title, course_desc, credit_hours, fall_availability,
                          spring_availability, summer_availability, alt_yr):
    """ Saves or updates course information via django's ORM.

    :param course_id: Course ID
    :param discipline: Discipline the course falls under
    :param course_title: Title of course
    :param course_desc: Description of course
    :param credit_hours: Number of credit hours for course
    :param fall_availability: Fall semester availability of course
    :param spring_availability: Spring semester availability of course
    :param summer_availability: Summer semester availability of course
    :param alt_yr: Alternating Year availability for course
    :return:
    """

    update_data = {
        'discipline': discipline, 'course_title': course_title, 'description': course_desc,
        'credit_hours': credit_hours, 'fall_availability': fall_availability,
        'spring_availability': spring_availability, 'summer_availability': summer_availability,
        'alternating_years': alt_yr, 'graduate_level': graduate_level
    }

    obj, created = Course.objects.update_or_create(course_number=course_id, defaults=update_data)
    if created:
        print(str(obj) + ' created!')
    else:
        print(str(obj) + ' updated!')
    return


def get_course_information(course_id, link, links, skipped_rows, discipline):
    """ Gets course information for current course.

    :param course_id: Course ID of the current course
    :param link: Link for the current Course ID
    :param links: List of links
    :param skipped_rows: Number of skipped rows, based on pagination.
    :param discipline: Discipline
    :return:
    """
    time.sleep(random.random())
    popup = driver.window_handles[1]
    driver.switch_to.window(popup)

    course_title = unicode((driver.find_element_by_id("CourseTitle")).text).strip()
    course_desc = unicode(driver.find_element_by_id("CourseDes").text).strip(course_id).strip()

    time.sleep(1 + (random.random() * 2))
    driver.close()
    driver.switch_to.window(driver.window_handles[0])

    info = driver.find_elements_by_css_selector('#ctl00_StaticPlaceHolder_CourseGridView '
                                                'tr:nth-child(' + str((links.index(link) + skipped_rows)) + ') td+ td')
    credit_hours = info[1].text
    fall_availability = info[2].text.replace(" ", "N").replace("ConsultNDepartment", "Consult Department")
    spring_availability = info[3].text.replace(" ", "N").replace("ConsultNDepartment", "Consult Department")
    summer_availability = info[4].text.replace(" ", "N").replace("ConsultNDepartment", "Consult Department")
    alt_yr = info[5].text.replace(" ", "N").replace("ConsultNDepartment", "Consult Department")
    save_or_update_course(course_id, discipline, course_title, course_desc, credit_hours, fall_availability,
                          spring_availability, summer_availability, alt_yr)
    return


def navigate_courses(discipline):
    """ Moves through the courses in a discipline.
    Changes pages if needed.
    :param discipline: Current discipline
    :return:
    """
    try:  # Checks for links at the top of the class table, which will only exist if there are more than one page.
        driver.find_element_by_css_selector('tr+ tr td:nth-child(2) a')
        pagination = True
    except NoSuchElementException:
        # To my knowledge selenium lacks the ability to determine if an element exists without looking for it
        # and throwing an exception if it does not.
        pagination = False

    pages = 1
    cont = True

    while cont:
        links = driver.find_elements_by_partial_link_text(str(discipline.discipline))
        # If the discipline is PD then webdriver is going to want to click on 'Save PDF' and throw itself off.
        # This way we save itself the trouble.
        if discipline.discipline == "PD":
            for i in links:
                if i.text == "Save to PDF":
                    del links[links.index(i)]
                    break

        # If there is more than one page we want to start a row lower than otherwise.
        if pagination:
            skipped_rows = 3
        else:
            skipped_rows = 2

        for link in links:
            if links.__sizeof__() < 1:
                cont = False
                break

            time.sleep(1 + (random.random() * 2))
            course_id = str(link.text)
            link.click()
            get_course_information(course_id, link, links, skipped_rows, discipline)

        if pagination:
            try:  # Attempts to click on link that matches pages
                pages += 1
                if pages == 11:
                    driver.execute_script("javascript:__doPostBack('ctl00$StaticPlaceHolder$CourseGridView'"
                                          ",'Page$11')")  # Page 11 is a special snowflake and has the text '...'
                else:
                    next_page = driver.find_element_by_link_text(str(pages))
                    next_page.click()
            except NoSuchElementException:
                # Returns to the first page and breaks out of loop. Going back to the first page is necessary with how
                # the university's site works. If you go from one discipline to another, and they both have multiple
                # pages, you can end up on a later page
                driver.execute_script("javascript:__doPostBack('ctl00$StaticPlaceHolder$CourseGridView','Page$1')")
                cont = False
        elif not pagination:
            driver.execute_script("javascript:__doPostBack('ctl00$StaticPlaceHolder$CourseGridView','Page$1')")
            cont = False
        time.sleep(1 + (random.random() * 2))
    return


def select_grad_level():
    """ Prompts for desired graduate level.
    :return: String containing U or G. """
    global graduate_level
    grad = raw_input('Select graduate level.\nEnter U for undergraduate or G for graduate: ').upper()
    while 1:
        if grad == 'U' or grad == 'G':
            if grad == 'U':
                graduate_level = 'undergraduate'
            else:
                graduate_level = 'graduate'
            break
        else:
            grad = raw_input('Incorrect input. Please enter either U or G: ').upper()
    Select(driver.find_element_by_id("ctl00_StaticPlaceHolder_GradTypeDDL")).select_by_value(grad)
    return


def get_disciplines():
    """
    Prompting for desired starting discipline,  allowing for continuation in the event of script errors or timeouts.
    :return: list of Discipline objects
    """
    start = raw_input(
            'Input Starting Discipline\nE.G. "BIOL", "WGSS", etc.\nPress Enter to start from the beginning: ').strip().upper()
    disciplines = list(Discipline.objects.all())
    while 1:
        if start != '':
            try:
                disc = Discipline.objects.get(pk=start)
                index = disciplines.index(disc)
                return disciplines[index:]
            except ObjectDoesNotExist:
                start = raw_input(
                    'Try again.\nInput a starting discipline or press enter to start from beginning: ').strip().upper()
                pass
        else:
            return disciplines


def main():
    select_grad_level()
    d = get_disciplines()
    for discipline in d:
        Select(driver.find_element_by_id("ctl00_StaticPlaceHolder_DisciplineDDL")).select_by_value(
                discipline.discipline)
        time.sleep(1 + (random.random() * 2))
        print('Working on ' + str(discipline) + " now!")
        navigate_courses(discipline)
    driver.close()


if __name__ == '__main__':
    url = "http://webapps.uc.edu/registrar/courseplanningguide/SemesterCoursePlanningGuide.aspx"
    while 1:
        browser = raw_input('Enter desired browser, either phantomjs or chrome: ').lower()
        if browser == 'chrome':
            path_to_chromedriver = "./chromedriver"
            driver = webdriver.Chrome(executable_path=path_to_chromedriver)
            driver.get(url)
            break
        elif browser == 'phantomjs':
            dcap = dict()
            dcap["phantomjs.page.settings.userAgent"] = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/53 "
                                                         "(KHTML, like Gecko) Chrome/15.0.87")
            path_to_phantomjs = './phantomjs'
            driver = webdriver.PhantomJS(executable_path=path_to_phantomjs, desired_capabilities=dcap)
            driver.get(url)
            break
    main()
