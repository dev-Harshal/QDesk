from django.urls import path, include
from Users.views import *

urlpatterns = [
    path('', index_view, name='index-view'),
    path('register/', register_view, name='register-view'),
    path('login/', login_view, name='login-view'),
    path('logout/', logout_view, name='logout-view'),

    path('<str:role>/login/', members_login_view, name='members-login-view'),
    path('members/update/profile/', members_update_profile_view, name='members-update-profile-view'),
    path('members/change-password/', members_change_password_view, name='members-change-password-view'),
    path('members/delete/<int:user_id>/', members_delete_user_view, name='members-delete-user-view' ),
    
    path('admin/', admin_index_view, name='admin-index-view'),
    path('admin/profile/', admin_profile_view, name='admin-profile-view'),
    path('admin/create/hod/', admin_create_hod_view, name='admin-create-hod-view'),
    path('admin/update/hod/<int:user_id>/', admin_update_hod_view, name='admin-update-hod-view'),
    path('admin/list/users/<str:role>/', admin_list_users_view, name='admin-list-users-view'),

    path('hod/', hod_index_view, name='hod-index-view'),
    path('hod/profile/', hod_profile_view, name='hod-profile-view'),

    path('hod/create/subject/', hod_create_subject_view, name='hod-create-subject-view'),
    path('hod/update/subject/<int:subject_id>/', hod_update_subject_view, name='hod-update-subject-view'),
    path('hod/delete/subject/<int:subject_id>/', hod_delete_subject_view, name='hod-delete-subject-view'),
    path('hod/list/subjects/', hod_list_subjects_view, name='hod-list-subjects-view'),

    path('hod/create/teacher/', hod_create_teacher_view, name='hod-create-teacher-view'),
    path('hod/update/teacher/<int:user_id>/', hod_update_teacher_view, name='hod-update-teacher-view'),
    path('hod/list/users/<str:role>/', hod_list_users_view, name='hod-list-users-view'),

    path('teacher/', include('Questions.urls')),
    path('teacher/', teacher_index_view, name='teacher-index-view'),
    path('teacher/profile/', teacher_profile_view, name='teacher-profile-view'),
    path('teacher/list/students/', teacher_list_students_view, name='teacher-list-students-view'),
]
