from django.shortcuts import render , redirect
from myapp.models import new
from myapp.models import job
from django.contrib.auth import authenticate, login
from django.contrib import messages

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
    jobs = job.objects.all()
    return render(request,"Applywork.html", {'jobs': jobs})

def intern(request):
    return render(request,"intern.html")

def Jobber(request):
    return render(request,"Jobber.html")

def dashboard(request):
    return render(request, 'Dashboard.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)  # ทำการเข้าสู่ระบบ
            return redirect('dashboard')  # เปลี่ยนเส้นทางไปที่หน้า dashboard
        else:
            messages.error(request, 'Invalid username or password')
    return render(request, 'login.html')
