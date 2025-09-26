from datetime import date
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class employee(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    emp_id = models.CharField(max_length=64)
    emp_name = models.CharField(max_length=255)

    class Position_emp (models.TextChoices):
        WFH = "WFH", "Telesales work from home"
        OFFICE = "OFFICE", "Telesales office"
        TRAINER = "TRAINER", "Trainer"
        MKT = "MKT", "Manager Marketing"
    emp_position = models.CharField(choices=Position_emp.choices, max_length=64)

    emp_tel = models.CharField(max_length=10)

    def __str__(self):
        return f"{self.emp_id} - {self.emp_name} - {self.emp_position} - {self.emp_tel}"

    class Meta:
        verbose_name = "พนักงาน"
        verbose_name_plural = "พนักงาน"
    

class candidate(models.Model):
    class Title(models.TextChoices):
        MR = "MR", "นาย"
        MRS = "MRS", "นาง"
        MS = "MS", "นางสาว"

    class Gender(models.TextChoices):
        MALE = "MALE", "ชาย"
        FEMALE = "FEMALE", "หญิง"

    class Position(models.TextChoices):
        WFH = "WFH", "Telesales work from home"
        OFFICE = "OFFICE", "Telesales office"
        TRAINER = "TRAINER", "Trainer"
        MKT = "MKT", "Manager Marketing"

    id = models.BigAutoField(primary_key=True)

    # === ข้อมูลผู้สมัคร ===
    cdd_title = models.CharField("คำนำหน้า", max_length=8, choices=Title.choices)
    cdd_first_name = models.CharField("ชื่อจริง", max_length=128)
    cdd_last_name = models.CharField("นามสกุล", max_length=128)
    cdd_nickname = models.CharField("ชื่อเล่น", max_length=64, blank=True)

    cdd_gender = models.CharField("เพศ", max_length=8, choices=Gender.choices)
    cdd_age = models.PositiveIntegerField("อายุ", null=True, blank=True)
    birth_date = models.DateField(null=True, blank=True, verbose_name="วันเดือนปีเกิด") 

    cdd_position = models.CharField("ตำแหน่งที่สนใจสมัคร", max_length=32, choices=Position.choices)
    work_exp = models.TextField("ประสบการณ์ทำงาน (ระบุคร่าว ๆ)", blank=True)
    education = models.CharField("วุฒิการศึกษา", max_length=255, blank=True)
    start_date_available = models.DateField("วันที่สามารถเริ่มงานได้", null=True, blank=True)

    # === ข้อมูลการติดต่อ ===
    cdd_tel = models.CharField("เบอร์โทรศัพท์", max_length=20)
    cdd_email = models.EmailField("อีเมล", blank=True)
    cdd_province = models.CharField("จังหวัด", max_length=100, blank=True)

    # === เอกสาร ===
    cdd_resume = models.FileField("Resume / CV", upload_to="resumes/", blank=True, null=True)
    cdd_photo = models.ImageField("รูปถ่ายผู้สมัคร", upload_to="candidate_photos/", blank=True, null=True)


    # === อุปกรณ์ (checkbox) ===
    has_pc = models.BooleanField("คอมพิวเตอร์ (Windows 10+)", default=False)
    has_laptop = models.BooleanField("โน้ตบุ้ค (Windows 10+)", default=False)
    has_wifi = models.BooleanField("Wi-Fi", default=False)
    has_headphone = models.BooleanField("Headphone", default=False)
    has_anydesk = models.BooleanField("Anydesk", default=False)

    class Status(models.TextChoices):
        APPROVED = "approved", "อ่านแล้ว"
        PENDING  = "pending",  "ยังไม่ได้อ่าน"

    cdd_status = models.CharField("สถานะ", max_length=20, choices=Status.choices, default=Status.PENDING)

    class Meta:
        verbose_name = "ผู้สมัคร"
        verbose_name_plural = "ผู้สมัคร"
        ordering = ["cdd_first_name", "cdd_last_name"]

    @property
    def full_name(self):
        return f"{self.get_cdd_title_display()}{self.cdd_first_name} {self.cdd_last_name}"

    def __str__(self):
        return f"{self.full_name} - {self.get_cdd_position_display()}"
    

class job(models.Model):
    id = models.BigAutoField(auto_created=True, primary_key=True ,serialize=False)
    job_name = models.CharField(max_length=255)
    job_salary = models.IntegerField(blank=True, null=True) 

    class jobtype (models.TextChoices):
        WFH = "WFH", "Telesales work from home"
        OFFICE = "OFFICE", "Telesales office"
        TRAINER = "TRAINER", "Trainer"
        MKT = "MKT", "Manager Marketing"
        INT = "INTERN", "Internship"
    job_type = models.CharField(choices=jobtype.choices, max_length=64)   
     
    job_subhead = models.TextField()
    job_qualification = models.TextField()
    job_benefit = models.TextField()
    job_description = models.TextField()

    def __str__(self):
        return f"{self.job_name} - {self.job_subhead} - {self.job_type} - {self.job_qualification} - {self.job_benefit} - {self.job_description}"
    
    class Meta:
        verbose_name = "รับสมัครงาน"
        verbose_name_plural = "รับสมัครงาน"


class repair(models.Model):
    class Meta:
        verbose_name = "แจ้งซ่อม"
        verbose_name_plural = "แจ้งซ่อม"

    repair_date = models.DateField(default=timezone.now)

    class RepairType(models.TextChoices):
        system_repair = "System repair", "แจ้งซ่อมระบบ"
        general_repair = "General repair", "แจ้งซ่อมทั่วไป"
    repair_type = models.CharField(choices=RepairType.choices, max_length=64)

    repair_problem = models.TextField()
    repair_cause = models.TextField(blank=True)

    class Location(models.TextChoices):
        first_floor = "ชั้น 1", "ชั้น 1"
        second_floor = "ชั้น 2", "ชั้น 2"
        third_floor = "ชั้น 3", "ชั้น 3"
    repair_location = models.CharField(choices=Location.choices, max_length=64)

    repair_img = models.ImageField(upload_to="repair_report/", blank=True, null=True)

    class RepairStatus(models.TextChoices):
        in_progress = "กำลังดำเนินการ", "กำลังดำเนินการ"
        completed = "ดำเนินการเรียบร้อย", "ดำเนินการเรียบร้อย"
    repair_status = models.CharField(
        choices=RepairStatus.choices, max_length=64, default=RepairStatus.in_progress
    )

    employee = models.ForeignKey("myapp.employee", on_delete=models.CASCADE, related_name="repairs")

    created_at = models.DateTimeField(auto_now_add=True)  # สำหรับ track ภายใน

    def __str__(self):
        return f"Repair #{self.pk} - {self.repair_status} - {self.repair_date} - {self.employee.emp_name}"
    

class new (models.Model):
    class Meta:
        verbose_name = "ข่าวประชาสัมพันธ์"
        verbose_name_plural = "ข่าวประชาสัมพันธ์"

    news_head = models.CharField(max_length=255)
    news_subhead = models.CharField(max_length=255)
    news_date = models.DateTimeField(auto_now_add=True)
    news_img = models.ImageField(upload_to='new_images/', blank=True, null=True)
    news_description = models.TextField()

    def __str__(self):
        if self.news_date:
            date_str = self.news_date.strftime('%Y-%m-%d %H:%M:%S')
        else:
            date_str = 'No date'

        image_url = self.news_img.url if self.news_img else 'No image'
        return f"{self.news_head} - {self.news_subhead} - {date_str} - {self.news_description} - {image_url}"
