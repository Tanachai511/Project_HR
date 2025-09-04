from django.db import models
from django.contrib.auth.models import User

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
    

class candidate(models.Model):
    id = models.BigAutoField(auto_created=True, primary_key=True ,serialize=False)
    cdd_name = models.CharField(max_length=255)

    class Position_cdd (models.TextChoices):
        WFH = "WFH", "Telesales work from home"
        OFFICE = "OFFICE", "Telesales office"
        TRAINER = "TRAINER", "Trainer"
        MKT = "MKT", "Manager Marketing"
    cdd_position = models.CharField(choices=Position_cdd.choices, max_length=64)

    cdd_tel = models.CharField(max_length=10)
    cdd_resume = models.FileField(upload_to='resumes/', blank=True, null=True)

    def __str__(self):
        resume_name = self.cdd_resume.name if self.cdd_resume else "No resume uploaded"
        return f"{self.cdd_name} - {self.cdd_position} - {self.cdd_tel} - {resume_name}"
    

class job(models.Model):
    id = models.BigAutoField(auto_created=True, primary_key=True ,serialize=False)
    job_name = models.CharField(max_length=255)

    class jobtype (models.TextChoices):
        Nesws_poster = "ข่าวประชาสัมพันธ์"
        Company_Activity = "กิจกรรมบริษัท"
        News = "ข่าวสาร"
        Other = "อื่น ๆ "
    job_type = models.CharField(choices=jobtype.choices, max_length=64)   
     
    job_subhead = models.TextField()
    job_qualification = models.TextField()
    job_benefit = models.TextField()
    job_description = models.TextField()

    def __str__(self):
        return f"{self.job_name} - {self.job_subhead} - {self.job_type} - {self.job_qualification} - {self.job_benefit} - {self.job_description}"


class repair(models.Model):
    repair_date = models.DateField(auto_now_add=True)

    class repair (models.TextChoices):
        system_repair = "System repair"
        general_repair = "General repair"
    repair_type = models.CharField(choices=repair.choices, max_length=64)
    repair_date = models.DateTimeField(auto_now_add=True)

    repair_problem = models.TextField()
    repair_cause = models.TextField()

    class location (models.TextChoices):
        first_floor = "ชั้น 1"
        second_floor = "ชั้น 2"
        third_floor = "ชั้น 3"
    repair_location = models.CharField(choices=repair.choices, max_length=64)

    repair_img = models.ImageField(upload_to='repair_report/', blank=True, null=True)
    
    class repairstatus (models.TextChoices):
        in_progress = "กำลังดำเนินการ"
        completed = "ดำเนินการเรียบร้อย"
    repair_status = models.CharField(choices=repairstatus.choices , max_length=64 , default=repairstatus.in_progress)

    employee = models.ForeignKey(employee, on_delete=models.CASCADE, related_name="repairs")
    
    def __str__(self):
        return f"Repair #{self.pk} - {self.repair_status} - {self.repair_date.strftime('%Y-%m-%d %H:%M:%S')} - {self.employee.emp_name}"

    def repair_details(self):
        return f"Repair #{self.pk} - {self.repair_status} - {self.repair_date.strftime('%Y-%m-%d %H:%M:%S')} - {self.employee.emp_name} - {self.repair_type} - {self.repair_cause} - {self.repair_img.url if self.repair_img else 'No image'}"
    

class new (models.Model):
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
