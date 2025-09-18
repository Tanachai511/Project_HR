from django import forms
from myapp.models import candidate,repair

class CandidateForm(forms.ModelForm):
    class Meta:
        model = candidate
        fields = [
            "cdd_title","cdd_first_name","cdd_last_name","cdd_nickname",
            "cdd_gender","birth_date","cdd_age","cdd_position","work_exp","education",
            "start_date_available","cdd_tel","cdd_email","cdd_province",
            "cdd_resume","has_pc","has_laptop","has_wifi","has_headphone","has_anydesk",
        ]
        widgets = {
            "cdd_first_name": forms.TextInput(attrs={"class": "form-control"}),
            "cdd_last_name": forms.TextInput(attrs={"class": "form-control"}),
            "birth_date": forms.DateInput(attrs={"type": "date"}), 
            "start_date_available": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
        }

class RepairForm(forms.ModelForm):
    class Meta:
        model = repair
        fields = [
            "repair_date",
            "repair_type",
            "repair_problem",
            "repair_cause",
            "repair_location",
            "repair_img",
        ]
        widgets = {
            "repair_date": forms.DateInput(attrs={"type": "date"}),
            "repair_problem": forms.Textarea(attrs={"rows": 4}),
            "repair_cause": forms.Textarea(attrs={"rows": 3}),
        }   