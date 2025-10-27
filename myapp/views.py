from django.shortcuts import render, redirect, get_object_or_404
from django.http import FileResponse, Http404, HttpResponse
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.urls import reverse
from django.template.loader import get_template
from io import BytesIO
from django.template.loader import render_to_string
from myapp.models import new, job, candidate, repair
from myapp.form import CandidateForm,RepairForm
from django.contrib.auth.decorators import login_required
from reportlab.lib.pagesizes import A4
from django.utils import timezone
from django.contrib.auth import logout

def index(request):
    news = new.objects.all().order_by('-news_date')[:3]
    return render(request, 'index.html', {'news': news})

def logout_view(request):
    if request.method != "POST":
        # ป้องกันการ logout ด้วย GET (ให้ใช้ปุ่ม/form POST เท่านั้น)
        return redirect(reverse("login"))

    logout(request)  # <-- สำคัญ! เคลียร์ session ออกจากระบบ
    messages.success(request, "ออกจากระบบเรียบร้อย")
    # รองรับ next (มาจาก hidden input ในฟอร์ม)
    next_url = request.POST.get("next") or reverse("login")
    return redirect(next_url)

def All1(request):
    news = new.objects.all().order_by('-news_date')
    return render(request, 'All1.html', {'news': news})

def All2(request):
    news = new.objects.all().order_by('-news_date')
    return render(request, 'All2.html', {'news': news})

def aboutme(request):
    return render(request, "aboutme.html")

def Applywork(request):
    jobs = job.objects.all()
    return render(request, "Applywork.html", {'jobs': jobs})

def intern(request):
    return render(request, "intern.html")

def contact(request):
    return render(request, "contact.html")

def Jobber(request):
    return render(request, "Jobber.html")

def dashboard(request):
    return render(request, 'Dashboard.html')

def document(request):
    return render(request, 'document.html')

def jangsom(request):
    return render(request, 'Jangsom.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password')

    return render(request, 'login.html')

def job_list(request):
    fulltime_jobs = job.objects.exclude(job_type="INTERN")  # เฉพาะพนักงานประจำ
    return render(request, 'jobs.html', {'jobs': fulltime_jobs})

# ---------------- Job form flow ----------------

def jobform_new(request):
    if request.method == "POST":
        form = CandidateForm(request.POST, request.FILES)
        if form.is_valid():
            obj = form.save()
            return redirect("jobform_detail", pk=obj.pk)
        else:
            # แสดงฟอร์มพร้อม error
            return render(request, "jobform.html", {"form": form, "pdf_mode": False}, status=400)
    else:
        form = CandidateForm()
    return render(request, "jobform.html", {"form": form, "pdf_mode": False})

def jobform_detail(request, pk: int):
    obj = get_object_or_404(candidate, pk=pk)
    return render(request, "jobform.html", {"obj": obj, "pdf_mode": False})

def jobform_detail_pdfview(request, pk: int):
    obj = get_object_or_404(candidate, pk=pk)
    return render(request, "jobform.html", {"obj": obj, "pdf_mode": True})

def jobform_pdf(request, pk):
    obj = get_object_or_404(candidate, pk=pk)

    # พยายามใช้ Playwright ก่อน
    try:
        from playwright.sync_api import sync_playwright

        pdfview_url = request.build_absolute_uri(
            reverse("jobform_detail_pdfview", args=[obj.pk])
        )

        with sync_playwright() as p:
            browser = p.chromium.launch(args=["--no-sandbox"])
            page = browser.new_page()
            page.goto(pdfview_url, wait_until="networkidle")
            page.emulate_media(media="print")
            pdf_bytes = page.pdf(
                format="A4",
                margin={
                    "top": "18mm",
                    "right": "16mm",
                    "bottom": "20mm",
                    "left": "16mm",
                },
                print_background=True,
            )
            browser.close()

        return FileResponse(
            BytesIO(pdf_bytes),
            as_attachment=True,
            filename=f"jobform_{obj.pk}.pdf",
        )

    # ถ้า Playwright ใช้ไม่ได้ ให้ fallback เป็น WeasyPrint
    except Exception:
        try:
            from weasyprint import HTML
        except Exception:
            return HttpResponse(
                "ยังไม่ได้ติดตั้ง Playwright หรือ WeasyPrint.\n"
                "ติดตั้งอย่างใดอย่างหนึ่ง:\n"
                "  1) pip install playwright && playwright install chromium\n"
                "  2) pip install weasyprint",
                status=500,
            )

        html = render_to_string("jobform.html", {"obj": obj, "pdf_mode": True})
        base_url = request.build_absolute_uri("/")
        pdf = HTML(string=html, base_url=base_url).write_pdf()

        return FileResponse(
            BytesIO(pdf),
            as_attachment=True,
            filename=f"jobform_{obj.pk}.pdf",
        )
    
TYPE_MAP = {
    # map ค่าที่มาจากพารามิเตอร์ -> ค่า choices จริงในโมเดล
    "general": repair.RepairType.general_repair,
    "system":  repair.RepairType.system_repair,
}
    
@login_required
def repair_create(request, forced_type: str | None = None):
    """
    ฟอร์มแจ้งซ่อมตัวเดียว:
    - ดึงข้อมูลพนักงาน (ของเก่า) -> ส่งไปให้ template: employee.emp_name
    - รองรับล็อกประเภทงานซ่อมจากการเลือกหน้าเมนู (ของใหม่) ผ่าน:
        1) forced_type จาก urls.py (เช่น path('repairs/new/system/', ... {'forced_type': 'system'}))
        2) หรือ querystring ?type=system / ?type=general
    """
    # ----- ดึงข้อมูลพนักงาน (ของเก่า) -----
    employee = getattr(request.user, "employee", None)
    if not employee:
        messages.error(request, "บัญชีนี้ยังไม่ได้ผูกกับข้อมูลพนักงาน")
        return redirect("login")  # หรือเปลี่ยนปลายทางตามที่ต้องการ

    # ----- อ่านชนิดงานซ่อมที่ต้องล็อก (ของใหม่) -----
    # ลำดับความสำคัญ: forced_type จาก URL > ?type=... จาก querystring
    type_param = (forced_type or request.GET.get("type") or "").lower()
    locked_type = TYPE_MAP.get(type_param)  # None ถ้าไม่ล็อก

    # ตั้งหัวข้อหน้าฟอร์มให้เข้ากับประเภท
    if locked_type == repair.RepairType.general_repair:
        page_title = "แจ้งซ่อมทั่วไปของบริษัท"
    elif locked_type == repair.RepairType.system_repair:
        page_title = "แจ้งซ่อมระบบ"
    else:
        page_title = "แจ้งซ่อม"

    if request.method == "POST":
        form = RepairForm(request.POST, request.FILES)
        # กันผู้ใช้ดัดแปลง HTML: ถ้าถูกล็อกไว้ บังคับค่า server-side เสมอ
        if locked_type:
            form.instance.repair_type = locked_type

        if form.is_valid():
            obj = form.save(commit=False)
            obj.employee = employee
            if locked_type:
                obj.repair_type = locked_type
            # ถ้าอยากให้ default วันที่เป็นวันนี้ในกรณีฟอร์มไม่ส่งมา
            if not obj.repair_date:
                obj.repair_date = timezone.now().date()
            obj.save()
            messages.success(request, "ส่งแจ้งซ่อมเรียบร้อยแล้ว")
            # กลับมาหน้าเดิม พร้อมล็อกประเภทเดิม เพื่อส่งต่อ workflow เดิม
            next_qs = f"?type={type_param}" if type_param else ""
            return redirect(f"{request.path}{next_qs}")
    else:
        initial = {"repair_date": timezone.now().date()}
        if locked_type:
            initial["repair_type"] = locked_type  # ให้ select มีค่าตรงกับที่ล็อก
        form = RepairForm(initial=initial)

    # label ภาษาไทยของค่าที่ล็อก (ไว้โชว์เป็นช่อง readonly ใน template)
    locked_type_label = dict(repair.RepairType.choices).get(locked_type, "")

    return render(
        request,
        "repaircom.html",  # ใช้ template เดิมของคุณ
        {
            # ของเก่า: ส่ง employee ไปให้ template ใช้ {{ employee.emp_name }}
            "employee": employee,

            # ของใหม่: ใช้ล็อก/โชว์ประเภทงาน
            "locked_type": locked_type,
            "locked_type_label": locked_type_label,
            "page_title": page_title,

            # ฟอร์ม
            "form": form,
        },
    )

    
@login_required
def repair_create1(request, forced_type: str | None = None):
    """
    ฟอร์มแจ้งซ่อมตัวเดียว:
    - ดึงข้อมูลพนักงาน (ของเก่า) -> ส่งไปให้ template: employee.emp_name
    - รองรับล็อกประเภทงานซ่อมจากการเลือกหน้าเมนู (ของใหม่) ผ่าน:
        1) forced_type จาก urls.py (เช่น path('repairs/new/system/', ... {'forced_type': 'system'}))
        2) หรือ querystring ?type=system / ?type=general
    """
    # ----- ดึงข้อมูลพนักงาน (ของเก่า) -----
    employee = getattr(request.user, "employee", None)
    if not employee:
        messages.error(request, "บัญชีนี้ยังไม่ได้ผูกกับข้อมูลพนักงาน")
        return redirect("login")  # หรือเปลี่ยนปลายทางตามที่ต้องการ

    # ----- อ่านชนิดงานซ่อมที่ต้องล็อก (ของใหม่) -----
    # ลำดับความสำคัญ: forced_type จาก URL > ?type=... จาก querystring
    type_param = (forced_type or request.GET.get("type") or "").lower()
    locked_type = TYPE_MAP.get(type_param)  # None ถ้าไม่ล็อก

    # ตั้งหัวข้อหน้าฟอร์มให้เข้ากับประเภท
    if locked_type == repair.RepairType.general_repair:
        page_title = "แจ้งซ่อมทั่วไปของบริษัท"
    elif locked_type == repair.RepairType.system_repair:
        page_title = "แจ้งซ่อมระบบ"
    else:
        page_title = "แจ้งซ่อม"

    if request.method == "POST":
        form = RepairForm(request.POST, request.FILES)
        # กันผู้ใช้ดัดแปลง HTML: ถ้าถูกล็อกไว้ บังคับค่า server-side เสมอ
        if locked_type:
            form.instance.repair_type = locked_type

        if form.is_valid():
            obj = form.save(commit=False)
            obj.employee = employee
            if locked_type:
                obj.repair_type = locked_type
            # ถ้าอยากให้ default วันที่เป็นวันนี้ในกรณีฟอร์มไม่ส่งมา
            if not obj.repair_date:
                obj.repair_date = timezone.now().date()
            obj.save()
            messages.success(request, "ส่งแจ้งซ่อมเรียบร้อยแล้ว")
            # กลับมาหน้าเดิม พร้อมล็อกประเภทเดิม เพื่อส่งต่อ workflow เดิม
            next_qs = f"?type={type_param}" if type_param else ""
            return redirect(f"{request.path}{next_qs}")
    else:
        initial = {"repair_date": timezone.now().date()}
        if locked_type:
            initial["repair_type"] = locked_type  # ให้ select มีค่าตรงกับที่ล็อก
        form = RepairForm(initial=initial)

    # label ภาษาไทยของค่าที่ล็อก (ไว้โชว์เป็นช่อง readonly ใน template)
    locked_type_label = dict(repair.RepairType.choices).get(locked_type, "")

    return render(
        request,
        "repairsystem.html",  # ใช้ template เดิมของคุณ
        {
            # ของเก่า: ส่ง employee ไปให้ template ใช้ {{ employee.emp_name }}
            "employee": employee,

            # ของใหม่: ใช้ล็อก/โชว์ประเภทงาน
            "locked_type": locked_type,
            "locked_type_label": locked_type_label,
            "page_title": page_title,

            # ฟอร์ม
            "form": form,
        },
    )


def repair_success(request):
    return render(request, "repair_success.html")

def applywork(request):
    jobs = job.objects.all().order_by("job_name")
    return render(request, "Applywork.html", {"jobs": jobs})


def repair_detail_pdfview(request, pk):
    obj = get_object_or_404(repair, pk=pk)
    return render(request, "repair_pdf.html", {"obj": obj, "pdf_mode": True})

def repair_pdf(request, pk):
    obj = get_object_or_404(repair, pk=pk)

    # 1) Playwright (ถ้ามี)
    try:
        from playwright.sync_api import sync_playwright
        pdfview_url = request.build_absolute_uri(
            reverse("repair_detail_pdfview", args=[obj.pk])
        )
        with sync_playwright() as p:
            browser = p.chromium.launch(args=["--no-sandbox"])
            page = browser.new_page()
            page.goto(pdfview_url, wait_until="networkidle")
            page.emulate_media(media="print")
            pdf_bytes = page.pdf(
                format="A4",
                margin={"top":"16mm","right":"14mm","bottom":"18mm","left":"14mm"},
                print_background=True
            )
            browser.close()
        return FileResponse(BytesIO(pdf_bytes),
                            as_attachment=True,
                            filename=f"repair_{obj.pk}.pdf")

    except Exception:
        # 2) Fallback: WeasyPrint
        try:
            from weasyprint import HTML
        except Exception:
            return HttpResponse(
                "ต้องติดตั้ง Playwright หรือ WeasyPrint ก่อน",
                status=500
            )
        html = render_to_string("repair_pdf.html", {"obj": obj, "pdf_mode": True})
        base_url = request.build_absolute_uri("/")  # สำหรับโหลดรูป/สไตล์
        pdf = HTML(string=html, base_url=base_url).write_pdf()
        return FileResponse(BytesIO(pdf),
                            as_attachment=True,
                            filename=f"repair_{obj.pk}.pdf")
    
@login_required
def waiting_repair(request):
    qs = repair.objects.select_related("employee").all().order_by("-repair_date", "-created_at")

    pending = qs.filter(repair_status=repair.RepairStatus.in_progress)
    general_pending_count = pending.filter(repair_type=repair.RepairType.general_repair).count()
    system_pending_count  = pending.filter(repair_type=repair.RepairType.system_repair).count()

    return render(request, "Waitingrepair.html", {
        "tickets": qs,
        "general_pending_count": general_pending_count,
        "system_pending_count": system_pending_count,
    })

def news_detail(request, pk):
    post = get_object_or_404(new, pk=pk)
    # ข่าวอื่น ๆ ไว้โชว์ด้านล่าง (ยกเว้นตัวเอง)
    others = new.objects.exclude(pk=pk).order_by("-news_date")[:3]
    return render(request, "news/detail.html", {"post": post, "others": others})
