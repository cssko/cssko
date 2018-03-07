from django.shortcuts import render
from django.views import View


class IndexView(View):
    template_name = 'home/home_page.html'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, {'active_nav': 'index'})



class WorkExperience(View):
    template_name = 'home/work_experience.html'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, {'active_nav': 'work_experience'})


class Activities(View):
    template_name = 'home/activities.html'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, {'active_nav': 'activities'})


class Resume(View):
    template_name = 'home/resume.html'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, {'active_nav': 'resume'})


class Contact(View):
    template_name = 'home/contact_me.html'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, {'active_nav': 'contact'})
