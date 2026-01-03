from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    otp = models.CharField(max_length=6, null=True, blank=True)
    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username

class Student(models.Model):
    full_name = models.CharField(max_length=100)
    email = models.EmailField()
    roll_number = models.CharField(max_length=20, unique=True)
    class_batch = models.CharField(max_length=50, verbose_name="Class / Batch")
    date_of_birth = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.full_name
    
class ProgressSheet(models.Model):
    EXAM_TYPES = [
        ('quarterly', 'Quarterly'),
        ('midterm', 'Midterm'),
        ('model', 'Model'),
        ('end_term', 'End-Term'),
    ]
    
    SUBJECTS = [
        ('mathematics', 'Mathematics'),
        ('science', 'Science'),
        ('english', 'English'),
    ]
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='progress_sheets')
    exam_type = models.CharField(max_length=20, choices=EXAM_TYPES)
    subject = models.CharField(max_length=20, choices=SUBJECTS)
    marks = models.DecimalField(max_digits=5, decimal_places=2, help_text="Enter marks (0-100)")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('student', 'exam_type', 'subject')
    
    def clean(self):
        if self.marks is not None and (self.marks < 0 or self.marks > 100):
            raise ValidationError('Marks must be between 0 and 100.')
    
    def __str__(self):
        return f"{self.student.full_name} - {self.exam_type} - {self.subject} - {self.marks}"