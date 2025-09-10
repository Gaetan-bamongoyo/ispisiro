from django.shortcuts import render

# Create your views here.

def indexPage(request):
    return render(request, 'client/index.html')

def bibliothequePage(request):
    return render(request, 'client/bibliotheque.html')
