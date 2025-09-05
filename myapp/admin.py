from django.contrib import admin
from myapp.models import employee
from myapp.models import candidate
from myapp.models import new
from myapp.models import repair
from myapp.models import job
from django.db.models import Count
from django.utils.html import format_html, format_html_join
from django.contrib import admin, messages
from django.urls import path, reverse
from django.shortcuts import redirect, get_object_or_404

admin.site.register(new)
admin.site.register(repair)
admin.site.register(job)

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
    # ปรับ path ให้ตรงกับ app/model ของคุณ
    change_list_template = "admin/myapp/employee/change_list.html"

    # ===== columns =====
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

    # ===== summary cards (ยอดรวมทั้งหมด) + ชื่อหัวข้อจากตัวกรองปัจจุบัน =====
    def changelist_view(self, request, extra_context=None):
        # ให้ Django Admin สร้าง ChangeList + context ปรกติก่อน
        response = super().changelist_view(request, extra_context=extra_context)
        try:
            # queryset ที่ถูก search/filter แล้ว (ใช้สำหรับตารางล่างเท่านั้น)
            qs_filtered = response.context_data["cl"].queryset
        except (AttributeError, KeyError):
            return response

        # --- 1) การ์ด: นับจากข้อมูลทั้งหมด (ไม่ผูกกับตัวกรอง) ---
        raw_all = employee.objects.values("emp_position").annotate(total=Count("id"))
        by_pos_all = {r["emp_position"]: r["total"] for r in raw_all}

        order = [
            (employee.Position_emp.WFH, "Telesales WFH"),
            (employee.Position_emp.OFFICE, "Telesales Office"),
            (employee.Position_emp.TRAINER, "Trainer"),
            (employee.Position_emp.MKT, "Manager Marketing"),
        ]
        summary_cards = [
            {
                "key": key,
                "label": label,
                "total": by_pos_all.get(key, 0),
                "url": f"?emp_position__exact={key}",  # ลิงก์กรองตารางเมื่อกดการ์ด
            }
            for key, label in order
        ]

        # --- 2) ชื่อหัวข้อหลัก สะท้อนตัวกรองปัจจุบันของหน้า ---
        current = request.GET.get("emp_position__exact")
        page_title = dict(order).get(current, "พนักงาน")

        # ใส่ค่าให้เทมเพลต
        response.context_data.update({
            "summary_cards": summary_cards,
            "page_title": page_title,
        })
        return response


@admin.register(candidate)
class CandidateAdmin(admin.ModelAdmin):
    list_display = (
        "full_name_display", "cdd_nickname", "cdd_position_display",
        "cdd_tel", "cdd_email", "cdd_province",
        "resume_link", "equipment_badges", "start_date_available",
        "age_display", "status_toggle",   # ใช้ปุ่มสลับสถานะ
    )
    list_display_links = ("full_name_display",)  # ห้ามชนกับคอลัมน์ที่ editable
    search_fields = (
        "cdd_first_name", "cdd_last_name", "cdd_nickname",
        "cdd_tel", "cdd_email", "cdd_province", "cdd_status"
    )
    list_per_page = 25
    ordering = ("cdd_first_name", "cdd_last_name")

    # ----- ปุ่มสถานะในตาราง -----
    @admin.display(description="สถานะ", ordering="cdd_status")
    def status_toggle(self, obj):
        url = reverse("admin:candidate_toggle_status", args=[obj.pk])
        if obj.cdd_status == candidate.Status.APPROVED:
            return format_html(
                '<a class="badge badge-ok" style="color:#fff;" href="{}">อ่านแล้ว</a>', url
            )
        return format_html(
            '<a class="badge badge-no" style="color:#fff;" href="{}">ยังไม่ได้อ่าน</a>', url
        )

    # ----- view สำหรับสลับสถานะ -----
    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path(
                "<int:pk>/toggle-status/",
                self.admin_site.admin_view(self.toggle_status),
                name="candidate_toggle_status",
            ),
        ]
        return my_urls + urls

    def toggle_status(self, request, pk, *args, **kwargs):
        obj = get_object_or_404(candidate, pk=pk)
        obj.cdd_status = (
            candidate.Status.PENDING
            if obj.cdd_status == candidate.Status.APPROVED
            else candidate.Status.APPROVED
        )
        obj.save(update_fields=["cdd_status"])
        messages.success(request, f"อัปเดตสถานะเป็น “{obj.get_cdd_status_display()}” แล้ว")
        return redirect(request.META.get("HTTP_REFERER", ".."))

    # ====== helpers ======
    def full_name_display(self, obj):
        return obj.full_name
    full_name_display.short_description = "ชื่อ-นามสกุล"

    def cdd_position_display(self, obj):
        return obj.get_cdd_position_display()
    cdd_position_display.short_description = "ตำแหน่งที่สนใจ"

    def resume_link(self, obj):
        if obj.cdd_resume:
            return format_html('<a href="{}" target="_blank">ไฟล์แนบ</a>', obj.cdd_resume.url)
        return "-"
    resume_link.short_description = "Resume"

    def equipment_badges(self, obj):
        items = []
        if obj.has_pc: items.append("คอมพิวเตอร์")
        if obj.has_laptop: items.append("โน้ตบุ้ค")
        if obj.has_wifi: items.append("Wi-Fi")
        if obj.has_headphone: items.append("Headphone")
        if obj.has_anydesk: items.append("Anydesk")
        if not items:
            return "-"
        return format_html_join(
            "",
            '<span style="display:inline-block;margin:0 4px 4px 0;padding:4px 8px;'
            'border-radius:8px;background:#eef2ff;color:#3730a3;font-weight:600;'
            'font-size:12px;">{}</span>',
            ((i,) for i in items)
        )
    equipment_badges.short_description = "อุปกรณ์"

    def age_display(self, obj):
        return f"{obj.cdd_age} ปี" if obj.cdd_age is not None else "-"
    age_display.short_description = "อายุ"

    # ====== การ์ดสรุป ======
    def changelist_view(self, request, extra_context=None):
        response = super().changelist_view(request, extra_context=extra_context)
        try:
            _ = response.context_data["cl"].queryset
        except (AttributeError, KeyError):
            return response

        from django.db.models import Count
        raw_all = candidate.objects.values("cdd_position").annotate(total=Count("id"))
        by_pos = {r["cdd_position"]: r["total"] for r in raw_all}

        order = [
            (candidate.Position.WFH, "Telesales WFH"),
            (candidate.Position.OFFICE, "Telesales Office"),
            (candidate.Position.TRAINER, "Trainer"),
            (candidate.Position.MKT, "Manager Marketing"),
        ]
        cards = [
            {"key": k, "label": lbl, "total": by_pos.get(k, 0), "url": f"?cdd_position__exact={k}"}
            for k, lbl in order
        ]
        current = request.GET.get("cdd_position__exact")
        title = dict(order).get(current, "ผู้สมัครงาน")
        response.context_data.update({"summary_cards": cards, "page_title": title})
        return response