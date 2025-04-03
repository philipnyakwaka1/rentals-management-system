from django.shortcuts import render


def home_template(request):
    return render(request, 'buildings/home.html')

def buildings_template(request):
    return render(request, 'buildings/buildings.html')
