# myapp/admin.py
from django.contrib import admin, messages
from django.db.models import Count
from django.utils.html import format_html, format_html_join
from django.urls import NoReverseMatch, path, reverse
from django.shortcuts import get_object_or_404, redirect
from django.http import HttpResponseRedirect, HttpResponseNotAllowed
from django.core.exceptions import PermissionDenied
from django.middleware.csrf import get_token

from myapp.models import employee, candidate, new, repair, job


# ========== ลงทะเบียนโมเดลพื้นฐาน ==========
admin.site.register(new)
admin.site.register(repair)
admin.site.register(job)


# ========== Employee Admin ==========
@admin.register(employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = (
        "emp_id_display", "emp_name_display", "emp_position_display",
        "emp_tel_display", "username",
    )
    search_fields = ("emp_id", "emp_name", "emp_tel", "user__username", "emp_position")
    ordering = ("emp_name",)
    list_per_page = 25
    list_select_related = ("user",)
    # ปรับ path ให้ตรงกับ app/model ของคุณ
    change_list_template = "admin/myapp/employee/change_list.html"

    # ----- columns -----
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

    # ----- summary cards (ยอดรวมทั้งหมด) + ชื่อหัวข้อจากตัวกรองปัจจุบัน -----
    def changelist_view(self, request, extra_context=None):
        # ให้ Django สร้าง ChangeList + context ปกติก่อน
        response = super().changelist_view(request, extra_context=extra_context)
        try:
            # queryset ที่ถูก search/filter แล้ว (ถ้าต้องใช้)
            _ = response.context_data["cl"].queryset
        except (AttributeError, KeyError):
            return response

        # การ์ดสรุปจากข้อมูลทั้งหมด (ไม่ขึ้นกับตัวกรอง)
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

        # ชื่อหัวข้อหลัก สะท้อนตัวกรองปัจจุบัน
        current = request.GET.get("emp_position__exact")
        page_title = dict(order).get(current, "พนักงาน")

        # ส่งค่าให้เทมเพลต
        response.context_data.update({
            "summary_cards": summary_cards,
            "page_title": page_title,
        })
        return response


@admin.register(candidate)
class CandidateAdmin(admin.ModelAdmin):
    change_list_template = "admin/myapp/candidate/change_list.html"

    list_display = (
        "full_name_display",
        "cdd_nickname",
        "cdd_position_display",
        "cdd_tel",
        "cdd_email",
        "cdd_province",
        "resume_link",
        "equipment_badges",
        "start_date_display",
        "age_display",
        "birth_date_display",   # 👈 เพิ่มคอลัมน์วันเกิด
        "status_badge",
        "pdf_button",
    )
    list_display_links = ("full_name_display",)
    search_fields = (
        "cdd_first_name",
        "cdd_last_name",
        "cdd_nickname",
        "cdd_tel",
        "cdd_email",
        "cdd_province",
        "cdd_status",
    )
    list_per_page = 25
    ordering = ("cdd_first_name", "cdd_last_name")

    # ✅ เอา date_hierarchy ออก เหลือเฉพาะ list_filter
    list_filter = ("birth_date",)

    # ---------- เก็บ request ไว้ให้ status_badge ใช้สร้าง CSRF ----------
    def changelist_view(self, request, extra_context=None):
        self._request = request
        response = super().changelist_view(request, extra_context=extra_context)

        try:
            _ = response.context_data["cl"].queryset
        except (AttributeError, KeyError):
            return response

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

    # ---------- ปุ่ม badge สลับสถานะ ----------
    @admin.display(description="สถานะ", ordering="cdd_status")
    def status_badge(self, obj):
        label = obj.get_cdd_status_display()
        if obj.cdd_status == obj.Status.APPROVED:
            style = "padding:2px 8px;border-radius:8px;background:#e6ffed;color:#0a7d29;border:1px solid #b7f7c7;"
            next_title = "สลับเป็น: ยังไม่ได้อ่าน"
        else:
            style = "padding:2px 8px;border-radius:8px;background:#fff7ed;color:#b45309;border:1px solid #fde1bf;"
            next_title = "สลับเป็น: อ่านแล้ว"

        request = getattr(self, "_request", None)
        csrf = get_token(request) if request else ""
        filters = request.GET.urlencode() if request else ""
        action_url = reverse("admin:candidate_toggle_status", args=[obj.pk])

        return format_html(
            (
                '<form method="post" action="{}" style="display:inline">'
                '<input type="hidden" name="csrfmiddlewaretoken" value="{}" />'
                '<input type="hidden" name="_changelist_filters" value="{}" />'
                '<button type="submit" title="{}" style="all:unset;cursor:pointer;">'
                '<span style="{}">{}</span>'
                "</button></form>"
            ),
            action_url, csrf, filters, next_title, style, label
        )

    @admin.display(description="วันเริ่มงาน")
    def start_date_display(self, obj):
        return obj.start_date_available

    def get_urls(self):
        urls = super().get_urls()
        clear_name = f"{self.model._meta.app_label}_{self.model._meta.model_name}_clear_data"

        my_urls = [
            path("clear-data/", self.admin_site.admin_view(self.clear_data), name=clear_name),
            path("<int:pk>/toggle-status/", self.admin_site.admin_view(self.toggle_status),
                 name="candidate_toggle_status"),
        ]
        return my_urls + urls

    def clear_data(self, request):
        if request.method != "POST":
            return HttpResponseNotAllowed(["POST"])
        if not self.has_delete_permission(request):
            raise PermissionDenied

        deleted = self.model.objects.all().delete()
        total = deleted[0]
        messages.success(request, f"ล้างข้อมูลทั้งหมดแล้ว ({total} แถว)")
        return redirect(reverse(f"admin:{self.model._meta.app_label}_{self.model._meta.model_name}_changelist"))

    def toggle_status(self, request, pk, *args, **kwargs):
        if request.method != "POST":
            return HttpResponseNotAllowed(["POST"])

        obj = get_object_or_404(candidate, pk=pk)
        if not self.has_change_permission(request, obj):
            raise PermissionDenied

        obj.cdd_status = (
            candidate.Status.PENDING
            if obj.cdd_status == candidate.Status.APPROVED
            else candidate.Status.APPROVED
        )
        obj.save(update_fields=["cdd_status"])
        messages.success(request, f"อัปเดตสถานะเป็น “{obj.get_cdd_status_display()}” แล้ว")

        changelist_url = reverse(f"admin:{obj._meta.app_label}_{obj._meta.model_name}_changelist")
        cl_filters = request.POST.get("_changelist_filters", "")
        return HttpResponseRedirect(f"{changelist_url}?{cl_filters}" if cl_filters else changelist_url)

    @admin.display(description="ฟอร์ม PDF", ordering=False)
    def pdf_button(self, obj):
        try:
            url = reverse("jobform_pdf", args=[obj.pk])
            return format_html('<a class="button" href="{}" target="_blank" rel="noopener">ดาวน์โหลด</a>', url)
        except NoReverseMatch:
            return "ตั้งค่า url name='jobform_pdf' ก่อน"

    @admin.display(description="ชื่อ-นามสกุล")
    def full_name_display(self, obj):
        return obj.full_name

    @admin.display(description="ตำแหน่งที่สนใจ")
    def cdd_position_display(self, obj):
        return obj.get_cdd_position_display()

    @admin.display(description="Resume")
    def resume_link(self, obj):
        if obj.cdd_resume:
            return format_html('<a href="{}" target="_blank">ไฟล์แนบ</a>', obj.cdd_resume.url)
        return "-"

    @admin.display(description="อุปกรณ์")
    def equipment_badges(self, obj):
        items = []
        if obj.has_pc: items.append("คอมพิวเตอร์")
        if obj.has_laptop: items.append("โน้ตบุ๊ค")
        if obj.has_wifi: items.append("Wi-Fi")
        if obj.has_headphone: items.append("Headphone")
        if obj.has_anydesk: items.append("Anydesk")
        if not items:
            return "-"
        return format_html_join(
            "",
            (
                '<span style="display:inline-block;margin:0 4px 4px 0;'
                'padding:4px 8px;border-radius:8px;background:#eef2ff;'
                'color:#3730a3;font-weight:600;font-size:12px;">{}</span>'
            ),
            ((i,) for i in items),
        )

    @admin.display(description="อายุ")
    def age_display(self, obj):
        return f"{obj.cdd_age} ปี" if obj.cdd_age is not None else "-"

    @admin.display(description="วันเกิด")
    def birth_date_display(self, obj):
        return obj.birth_date