from django.http import HttpResponseRedirect, FileResponse, Http404
from django.shortcuts import render
from django.views import View
from .forms import ContactForm
from django.core.mail import send_mail


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
    # template_name = 'home/resume.html'

    def get(self, request, *args, **kwargs):
        try:  # Let's just return the pdf for now
            return FileResponse(open('media/Chris Kothman.pdf', 'rb'), content_type='application/pdf')
        except FileNotFoundError:
            raise Http404()
        # return render(request, self.template_name, {'active_nav': 'resume'})


class Contact(View):
    template_name = 'home/contact_me.html'

    def get(self, request, *args, **kwargs):
        form = ContactForm()
        return render(request, self.template_name, {'active_nav': 'contact', 'form': form})

    def post(self, request, *args, **kwargs):
        form = ContactForm(request.POST)
        if form.is_valid():
            pass
        return render(request, self.template_name, {'form': form})
