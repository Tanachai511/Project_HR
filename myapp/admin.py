from django.contrib import admin
from myapp.models import employee
from myapp.models import candidate
from myapp.models import new
from myapp.models import repair
from myapp.models import job
from django.db.models import Count

# Register your models here.
admin.site.register(employee)
admin.site.register(candidate)
admin.site.register(new)
admin.site.register(repair)
admin.site.register(job)

try:
    admin.site.unregister(employee)
except admin.sites.NotRegistered:
    pass

@admin.register(employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = (
        "emp_id_display", "emp_name_display", "emp_position_display",
        "emp_tel_display", "username"
    )
    search_fields = ("emp_id", "emp_name", "emp_tel", "user__username", "emp_position")
    ordering = ("emp_name",)
    list_per_page = 25
    list_select_related = ("user",)

    def emp_id_display(self, obj): return obj.emp_id
    emp_id_display.short_description = "รหัสพนักงาน"

    def emp_name_display(self, obj): return obj.emp_name
    emp_name_display.short_description = "ชื่อ-นามสกุล"

    def emp_tel_display(self, obj): return obj.emp_tel
    emp_tel_display.short_description = "หมายเลขโทรศัพท์"

    def emp_position_display(self, obj): return obj.get_emp_position_display()
    emp_position_display.short_description = "ตำแหน่งงาน"

    def username(self, obj): return obj.user.username
    username.short_description = "บัญชีผู้ใช้"