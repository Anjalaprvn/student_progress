from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
#from django.core.mail import send_mail
from django.conf import settings
from django.db.models import Q
from .models import Profile, Student, ProgressSheet
from .forms import StudentForm, ProgressSheetForm
import random
import string


def generate_otp():
    """Generate a 6-digit OTP"""
    return ''.join(random.choices(string.digits, k=6))

def signup_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        
        # Check if passwords match
        if password != confirm_password:
            messages.error(request, 'Passwords do not match!')
            return render(request, 'signup.html')
        
        # Check if user already exists
        if User.objects.filter(email=email).exists():
            messages.error(request, 'User with this email already exists!')
            return render(request, 'signup.html')
        
        # Create user
        user = User.objects.create_user(username=email, email=email, password=password)
        
        # Create profile (without actual OTP)
        profile = Profile.objects.create(user=user, otp='123456', is_verified=False)  # Placeholder OTP
        
        # Show message that OTP was sent (without actual sending)
        messages.success(request, 'OTP has been sent to your email. Please verify your account.')
        return redirect('verify_otp', user_id=user.id)
    
    return render(request, 'signup.html')

def verify_otp(request, user_id):
    try:
        user = User.objects.get(id=user_id)
        profile = Profile.objects.get(user=user)
    except (User.DoesNotExist, Profile.DoesNotExist):
        messages.error(request, 'Invalid user.')
        return redirect('signup')
    
    if request.method == 'POST':
        # Skip actual OTP verification and just verify the account
        profile.is_verified = True
        profile.save()
        messages.success(request, 'OTP verified successfully. You can now login.')
        return redirect('login')
    
    return render(request, 'verify_otp.html', {'user_id': user_id})

def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        # Authenticate user
        user = authenticate(request, username=email, password=password)
        
        if user is not None:
            # Check if user is verified
            try:
                profile = Profile.objects.get(user=user)
                if profile.is_verified:
                    login(request, user)
                    return redirect('dashboard')  # Redirect to dashboard after login
                else:
                    messages.error(request, 'Please verify your account before logging in.')
            except Profile.DoesNotExist:
                messages.error(request, 'Account not found.')
        else:
            messages.error(request, 'Invalid email or password.')
    
    return render(request, 'login.html')

@login_required
def dashboard_view(request):
  
    total_students = Student.objects.count()
    top_performer = None
    
  
    students_with_avg = []
    for student in Student.objects.all():
        avg_marks = 0
        count = 0
        for sheet in student.progress_sheets.all():
            avg_marks += float(sheet.marks)
            count += 1
        if count > 0:
            avg_marks = avg_marks / count
            students_with_avg.append((student, avg_marks))
    
    if students_with_avg:
        top_performer = max(students_with_avg, key=lambda x: x[1])[0] if students_with_avg else None
    
    context = {
        'total_students': total_students,
        'top_performer': top_performer,
    }
    return render(request, 'dashboard.html', context)

@login_required
def student_list_view(request):
 
    exam_type = request.GET.get('exam_type', '')
    search_query = request.GET.get('search', '')
    class_filter = request.GET.get('class', '')
    
    
    students = Student.objects.all()
    
   
    if class_filter:
        students = students.filter(class_batch=class_filter)
    
    if search_query:
        students = students.filter(
            Q(full_name__icontains=search_query) | 
            Q(roll_number__icontains=search_query)
        )
    
   
    if exam_type:
        
        exam_sheets = ProgressSheet.objects.filter(exam_type=exam_type)
        
        student_ids = exam_sheets.values_list('student_id', flat=True).distinct()
        
      
        students = students.filter(id__in=student_ids)
        
  
        student_averages = {}
        for sheet in exam_sheets:
            student = sheet.student
            if student not in student_averages:
                
                student_exam_sheets = exam_sheets.filter(student=student)
                total_marks = sum([s.marks for s in student_exam_sheets])
                avg_marks = total_marks / len(student_exam_sheets) if len(student_exam_sheets) > 0 else 0
                student_averages[student] = avg_marks
        
        
        students = sorted(students, key=lambda s: student_averages.get(s, 0), reverse=True)
    
    # Get all available classes for the filter dropdown
    all_classes = Student.objects.values_list('class_batch', flat=True).distinct().order_by('class_batch')
    
    # Add pagination
    paginator = Paginator(students, 10)  # Show 10 students per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'students': page_obj,  # Use paginated students
        'exam_types': ProgressSheet.EXAM_TYPES,
        'selected_exam': exam_type,
        'search_query': search_query,
        'selected_class': class_filter,
        'all_classes': all_classes,
    }
    return render(request, 'student_list.html', context)

@login_required
def add_student_view(request):
    if request.method == 'POST':
        form = StudentForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Student added successfully.')
            return redirect('student_list')
    else:
        form = StudentForm()
    
    return render(request, 'add_student.html', {'form': form})

@login_required
def edit_student_view(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    
    if request.method == 'POST':
        form = StudentForm(request.POST, instance=student)
        if form.is_valid():
            form.save()
            messages.success(request, 'Student updated successfully.')
            return redirect('student_list')
    else:
        form = StudentForm(instance=student)
    
    return render(request, 'edit_student.html', {'form': form, 'student': student})

@login_required
def delete_student_view(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    
    if request.method == 'POST':
        student.delete()
        messages.success(request, 'Student deleted successfully.')
        return redirect('student_list')
    
    return render(request, 'delete_student.html', {'student': student})

@login_required
def student_detail_view(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    
     
    progress_sheets = student.progress_sheets.all()
    
    
    exam_data = {}
    for sheet in progress_sheets:
        if sheet.exam_type not in exam_data:
            exam_data[sheet.exam_type] = []
        exam_data[sheet.exam_type].append(sheet)
    
   
    total_marks = sum(float(sheet.marks) for sheet in progress_sheets)
    average_score = 0
    if progress_sheets.count() > 0:
        average_score = total_marks / progress_sheets.count()
    
    return render(request, 'student_detail.html', {
        'student': student,
        'exam_data': exam_data,
        'total_marks': total_marks,
        'average_score': round(average_score, 2)
    })

@login_required
def add_progress_sheet_view(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    
    if request.method == 'POST':
        form = ProgressSheetForm(request.POST)
        if form.is_valid():
            exam_type = form.cleaned_data['exam_type']
            subject = form.cleaned_data['subject']
            
            # Check if a progress sheet already exists for this student, exam type, and subject
            existing_sheet = ProgressSheet.objects.filter(
                student=student,
                exam_type=exam_type,
                subject=subject
            ).first()
            
            if existing_sheet:
                messages.error(request, f'A progress sheet already exists for {exam_type.title()} exam in {subject.title()} subject. Please edit the existing entry instead.')
                # Redirect to student detail page instead of staying on add page
                return redirect('student_detail', student_id=student.id)
            
            progress_sheet = form.save(commit=False)
            progress_sheet.student = student
            progress_sheet.save()
            messages.success(request, 'Progress sheet added successfully.')
            return redirect('student_detail', student_id=student.id)
    else:
        form = ProgressSheetForm()
    
    return render(request, 'add_progress_sheet.html', {
        'form': form,
        'student': student
    })

def edit_progress_sheet_view(request, student_id, sheet_id):
    student = get_object_or_404(Student, id=student_id)
    progress_sheet = get_object_or_404(ProgressSheet, id=sheet_id, student=student)
    
    if request.method == 'POST':
        form = ProgressSheetForm(request.POST, instance=progress_sheet)
        if form.is_valid():
            form.save()
            messages.success(request, 'Progress sheet updated successfully.')
            return redirect('student_detail', student_id=student.id)
    else:
        form = ProgressSheetForm(instance=progress_sheet)
    
    return render(request, 'add_progress_sheet.html', {
        'form': form,
        'student': student,
        'edit_mode': True,
        'sheet': progress_sheet
    })

def logout_view(request):
    from django.contrib.auth import logout
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('login')
