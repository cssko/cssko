from django.shortcuts import render


def index(request):
    return render(request, 'home/home_page.html')


def about(request):
    return render(request, 'about.html')
