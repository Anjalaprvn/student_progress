from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('verify_otp/<int:user_id>/', views.verify_otp, name='verify_otp'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('students/', views.student_list_view, name='student_list'),
    path('students/add/', views.add_student_view, name='add_student'),
    path('students/edit/<int:student_id>/', views.edit_student_view, name='edit_student'),
    path('students/delete/<int:student_id>/', views.delete_student_view, name='delete_student'),
    path('students/<int:student_id>/', views.student_detail_view, name='student_detail'),
    path('students/<int:student_id>/add-progress/', views.add_progress_sheet_view, name='add_progress_sheet'),
    path('students/<int:student_id>/edit-progress/<int:sheet_id>/', views.edit_progress_sheet_view, name='edit_progress_sheet'),
    path('logout/', views.logout_view, name='logout'),
]