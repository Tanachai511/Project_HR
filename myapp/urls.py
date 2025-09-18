from django.urls import path
from myapp import views
from myapp.views import repair_create
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('', views.index),
    path('aboutme', views.aboutme, name='aboutme'),
    path('All1',  views.All1, name='All1'),
    path("applywork/", views.applywork, name="Applywork"),
    path('intern', views.intern, name='Applywork'),
    path('Jobber', views.Jobber, name='Jobber'),
    path('Applywork', views.Applywork, name='job_list'),
    path('login', views.login_view, name='login'),
    path('dashboard', views.dashboard, name='dashboard'),  
    path("apply/", views.jobform_new, name="jobform_new"),
    path("apply/<int:pk>/", views.jobform_detail, name="jobform_detail"),
    path("apply/<int:pk>/pdfview/", views.jobform_detail_pdfview, name="jobform_detail_pdfview"),
    path("apply/<int:pk>/pdf/", views.jobform_pdf, name="jobform_pdf"),
    path("repaircom/", views.repair_create, name="repair-create"),
    path("repaircom/success/", views.repair_success, name="repair_success"),
    path("logout/", LogoutView.as_view(next_page="login"), name="logout"),
    path("admin/repair/<int:pk>/pdf/", views.repair_pdf, name="repair-pdf"),
]