from django import forms
from .models import Student, ProgressSheet

class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['full_name', 'email', 'roll_number', 'class_batch', 'date_of_birth']
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'input-field', 'placeholder': 'Full Name'}),
            'email': forms.EmailInput(attrs={'class': 'input-field', 'placeholder': 'Email'}),
            'roll_number': forms.TextInput(attrs={'class': 'input-field', 'placeholder': 'Roll Number'}),
            'class_batch': forms.TextInput(attrs={'class': 'input-field', 'placeholder': 'Class / Batch'}),
            'date_of_birth': forms.DateInput(attrs={'class': 'input-field', 'type': 'date'}),
        }

class ProgressSheetForm(forms.ModelForm):
    class Meta:
        model = ProgressSheet
        fields = ['exam_type', 'subject', 'marks']
        widgets = {
            'marks': forms.NumberInput(attrs={'class': 'input-field', 'placeholder': 'Marks (0-100)', 'min': 0, 'max': 100}),
        }