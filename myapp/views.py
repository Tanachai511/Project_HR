from django.shortcuts import render

# Create your views here.
def index(request):
    news = new.objects.all().order_by('-news_date')[:3]
    return render(request, 'index.html', {'news': news})

def All1(request):
    news = new.objects.all().order_by('-news_date')
    return render(request, 'All1.html', {'news': news})

def aboutme(request):
    return render(request,"aboutme.html")

def Applywork(request):
    return render(request,"Applywork.html")

def intern(request):
    return render(request,"intern.html")

def Jobber(request):
    return render(request,"Jobber.html")
