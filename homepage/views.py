from django.shortcuts import render


def index(request):
    return render(request, 'index.html')


def contact_page(request):
    return render(request, 'contact.html')


def about_page(request):
    return render(request, 'about.html')
