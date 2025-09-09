from django.urls import path
from myapp import views

urlpatterns = [
    path('', views.index),
    path('aboutme', views.aboutme, name='aboutme'),
    path('All1',  views.All1, name='All1'),
    path('Applywork', views.Applywork, name='Applywork'),
    path('intern', views.intern, name='Applywork'),
    path('Jobber', views.Jobber, name='Jobber'),
    path('Applywork', views.Applywork, name='job_list'),
    path('login', views.login_view, name='login'),
    path('dashboard', views.dashboard, name='dashboard'),  
    path("apply/", views.jobform_new, name="jobform_new"),
    path("apply/<int:pk>/", views.jobform_detail, name="jobform_detail"),
    path("apply/<int:pk>/pdfview/", views.jobform_detail_pdfview, name="jobform_detail_pdfview"),
    path("apply/<int:pk>/pdf/", views.jobform_pdf, name="jobform_pdf"),
]