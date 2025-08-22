from django.shortcuts import render

# Create your views here.
def index(request):
    return render(request,"index.html")

def All1(request):
    return render(request,"All1.html")

def All2(request):
    return render(request,"All2.html")