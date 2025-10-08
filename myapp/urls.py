from django.urls import path
from myapp import views
from myapp.views import repair_create
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.index, name='Home'),
    path('aboutme', views.aboutme, name='aboutme'),
    path('All1',  views.All1, name='All1'),
    path('contact',  views.contact, name='contact'),
    path("applywork/", views.applywork, name="Applywork"),
    path('intern', views.intern, name='intern'),
    path('Jobber', views.Jobber, name='Jobber'),
    path('Applywork', views.Applywork, name='job_list'),
    path('login', views.login_view, name='login'),
    path('dashboard', views.dashboard, name='dashboard'),  
    path("apply/", views.jobform_new, name="jobform_new"),
    path("apply/<int:pk>/", views.jobform_detail, name="jobform_detail"),
    path("apply/<int:pk>/pdfview/", views.jobform_detail_pdfview, name="jobform_detail_pdfview"),
    path("apply/<int:pk>/pdf/", views.jobform_pdf, name="jobform_pdf"),
    path("repaircom/", views.repair_create, name="repair-create"),
    path("repairsystem/", views.repair_create1, name="repair-create1"),
    path("repaircom/success/", views.repair_success, name="repair_success"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("admin/repair/<int:pk>/pdf/", views.repair_pdf, name="repair-pdf"),
    path("repair/<int:pk>/pdfview/", views.repair_detail_pdfview, name="repair_detail_pdfview"),
    path("repair/<int:pk>/pdf/", views.repair_pdf,name="repair_pdf"),
    path("document/", views.document, name="document"),
    path("Jangsom/", views.jangsom, name="Jangsom"),
    path("waiting-repair/", views.waiting_repair, name="waiting_repair"),
    path("news/<int:pk>/", views.news_detail, name="news_detail"),
]