from django.urls import path
from myapp import views

urlpatterns = [
    path('', views.index),
    path('All1', views.All1, name='All1'),
    path('All2', views.All2, name='All2')
]