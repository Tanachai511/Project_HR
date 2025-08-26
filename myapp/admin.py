from django.contrib import admin
from myapp.models import employee
from myapp.models import candidate
from myapp.models import news
from myapp.models import repair
from myapp.models import job

# Register your models here.
admin.site.register(employee)
admin.site.register(candidate)
admin.site.register(news)
admin.site.register(repair)
admin.site.register(job)