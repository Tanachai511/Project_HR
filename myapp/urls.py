from django.urls import path
from myapp import views

urlpatterns = [
    path('', views.index),
    path('aboutme', views.aboutme, name='aboutme'),
    path('All1', views.All1, name='All1'),
    path('Applywork', views.Applywork, name='Applywork'),
    path('intern', views.intern, name='Applywork'),
    path('Jobber', views.Jobber, name='Jobber')
]