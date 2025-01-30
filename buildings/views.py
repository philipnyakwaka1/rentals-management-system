from django.shortcuts import render


def buildings_template(request):
    return render(request, 'buildings/buildings.html')
