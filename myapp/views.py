from django.shortcuts import render

# Create your views here.
def index(request):
    return render(request,"index.html")

def All1(request):
    return render(request,"All1.html")

def aboutme(request):
    return render(request,"aboutme.html")

def Applywork(request):
    return render(request,"Applywork.html")

def intern(request):
    return render(request,"intern.html")

def Jobber(request):
    return render(request,"Jobber.html")