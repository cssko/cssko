import django
import requests
from cssko import wsgi, settings
from course_catalog.models import Discipline
from bs4 import BeautifulSoup


url = "http://webapps.uc.edu/registrar/courseplanningguide/SemesterCoursePlanningGuide.aspx"
soup = BeautifulSoup(requests.get(url).text, 'lxml')
ddl = soup.find(id='ctl00_StaticPlaceHolder_DisciplineDDL')
dropdown_items = ddl.find_all('option')

for item in dropdown_items[1:]:
    disc = item['value']
    name = item.text.strip(disc).strip(' - ')
    Discipline.objects.update_or_create(discipline=disc, name=name)
