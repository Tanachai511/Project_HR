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
from reportlab.pdfgen import canvas


def index(request):
    news = new.objects.all().order_by('-news_date')[:3]
    return render(request, 'index.html', {'news': news})

def All1(request):
    news = new.objects.all().order_by('-news_date')
    return render(request, 'All1.html', {'news': news})

def aboutme(request):
    return render(request, "aboutme.html")

def Applywork(request):
    jobs = job.objects.all()
    return render(request, "Applywork.html", {'jobs': jobs})

def intern(request):
    return render(request, "intern.html")

def Jobber(request):
    return render(request, "Jobber.html")

def dashboard(request):
    return render(request, 'Dashboard.html')

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
    
@login_required
def repair_create(request):
    if not hasattr(request.user, "employee"):
        messages.error(request, "บัญชีนี้ยังไม่ได้ผูกข้อมูลพนักงาน")
        return redirect("admin:index")

    if request.method == "POST":
        form = RepairForm(request.POST, request.FILES)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.employee = request.user.employee
            obj.save()
            return redirect("repair_success")
    else:
        form = RepairForm()

    return render(request, "repaircom.html", {"form": form, "employee": request.user.employee})

def repair_success(request):
    return render(request, "repair_success.html")

def applywork(request):
    jobs = job.objects.all().order_by("job_name")
    return render(request, "Applywork.html", {"jobs": jobs})


def repair_pdf(request, pk):
    try:
        obj = repair.objects.get(pk=pk)
    except repair.DoesNotExist:
        raise Http404("Repair not found")

    # สร้าง response เป็น pdf
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="repair_{obj.id}.pdf"'

    # เขียน PDF ด้วย reportlab
    p = canvas.Canvas(response, pagesize=A4)
    p.setFont("Helvetica", 14)
    p.drawString(100, 800, f"Repair Report #{obj.id}")
    p.setFont("Helvetica", 12)
    p.drawString(100, 770, f"วันที่แจ้ง: {obj.repair_date.strftime('%Y-%m-%d %H:%M')}")
    p.drawString(100, 750, f"ผู้แจ้ง: {obj.employee.emp_name}")
    p.drawString(100, 730, f"ประเภทงาน: {obj.get_repair_type_display()}")
    p.drawString(100, 710, f"สถานะ: {obj.get_repair_status_display()}")
    p.drawString(100, 690, f"สถานที่: {obj.repair_location}")
    p.drawString(100, 670, f"ปัญหา: {obj.repair_problem}")
    p.drawString(100, 650, f"สาเหตุ: {obj.repair_cause}")

    p.showPage()
    p.save()
    return response