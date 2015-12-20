import random
import re
import time

from selenium import webdriver
from selenium.webdriver.support import ui
from selenium.webdriver.support.select import Select
from cssko import wsgi, settings
from course_catalog.models import Building


def get_buildings():
    url = 'https://ucdirectory.uc.edu/CampusBuildings.asp'
    driver.get(url)
    building_select = ui.Select(driver.find_element_by_name('formBLDGCODE'))
    building_options = [option.get_attribute("value") for option in building_select.options][1:]
    for bldg in building_options:
        Select(driver.find_element_by_name('formBLDGCODE')).select_by_value(bldg)
        driver.find_element_by_name('B1').click()
        time.sleep(1 + (random.random()*2))
        text = driver.find_element_by_xpath('//*[@id="content"]/div[2]/div/table[2]/tbody/tr/td').text

        building_name = name_regex.search(text).group()
        building_address = address_regex.search(text).group()
        building_code = code_regex.search(text).group()
        building_campus = campus_regex.search(text).group()

        update_dict = {'name': building_name, 'address': building_address, 'campus': building_campus}
        obj, created = Building.objects.update_or_create(building_code=building_code, defaults=update_dict)

        if created:
            print(str(obj) + ' created!')
        else:
            print(str(obj) + ' updated!')
        time.sleep(1 + (random.random()*2))
    return


if __name__ == '__main__':
    name_regex = re.compile('(?<=Name:)(.*)')
    address_regex = re.compile('(?<=Address:)(.*)')
    code_regex = re.compile('(?<=Building Code:)(.*)')
    campus_regex = re.compile('(?<=Campus:)(.*)')
    path_to_chromedriver = "./chromedriver"
    driver = webdriver.Chrome(executable_path=path_to_chromedriver)
    get_buildings()
