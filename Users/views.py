import string
import textwrap
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from Users.models import *
from Questions.models import *
from django.http import HttpResponse
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from urllib.parse import unquote
from django.db.models import Q 
# Create your views here.

from urllib.parse import unquote
from django.db.models import Q  # To help with complex queries

def index_view(request):
    department = request.GET.get('department', '').strip()
    scheme = request.GET.get('scheme', '').strip()
    semester = request.GET.get('semester', '').strip()

    query_filters = False


    if department:
        query_filters = True
        filtered_subjects = Subject.objects.filter(department=department)
    if scheme:
        query_filters = True
        filtered_subjects = filtered_subjects.filter(scheme=scheme)    
    if semester:
        query_filters = True
        filtered_subjects = filtered_subjects.filter(semester=semester)


    if not query_filters:
        all_subjects = Subject.objects.all()
    else:
        all_subjects = filtered_subjects.all()

        
    question_set_subjects = Subject.objects.filter(
        question_sets__in=QuestionSet.objects.all()
    ).distinct()

    question_paper_subjects = Subject.objects.filter(
        question_papers__in=QuestionPaper.objects.all()
    ).distinct()

    context = {
        'question_set_subjects': question_set_subjects[:3],
        'question_paper_subjects': question_paper_subjects[:3],
        'subjects': all_subjects,
    }

    return render(request, 'users/index.html', context)

def question_sets_view(request, subject_id):
    subject = Subject.objects.prefetch_related(
        'question_sets__questions' 
    ).get(id=subject_id)
    question_sets = subject.question_sets.all()
    for qs in question_sets:
        qs.sorted_questions = qs.questions.all().order_by('question_mark')
    return render(request, 'users/question_sets.html', context={'question_sets':question_sets, 'subject':subject})

def assignments_view(request, subject_id):
    subject = Subject.objects.get(id=subject_id)
    assignments = QuestionPaper.objects.filter(question_paper_type='Assignment', question_paper_subject=subject, status="Complete").order_by('question_paper_title')
    return render(request, 'users/assignments.html', context={'assignments':assignments, 'subject':subject})

def assignment_view(request, assignment_id):
    assignment = QuestionPaper.objects.get(id=assignment_id)
    institute = Profile.objects.filter(subjects=assignment.question_paper_subject).first().user.institute
    return render(request, 'users/assignment.html', context={'assignment':assignment, 'institute':institute})

def register_view(request):
    if request.method == 'POST':
        try:
            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')
            institute = request.POST.get('institute')
            email = request.POST.get('email')
            username = request.POST.get('username')
            password = request.POST.get('password')
            confirm_password = request.POST.get('confirm_password')

            if User.objects.filter(email=email).exists():
                return JsonResponse({'status':'error', 'message':'Email address already exists.'})
            
            if User.objects.filter(username=username).exists():
                return JsonResponse({'status':'error', 'message':'Username already exists.'})
        
            if password != confirm_password:
                return JsonResponse({'status':'error', 'message':'Passwords does not match.'})
            
            user = User.objects.create_user(
                first_name = first_name,
                last_name = last_name,
                institute = institute,
                email = email,
                username = username,
                password = password,
                role = 'Student'
            )

            messages.success(request, f'{user} registered successfully.')
            return JsonResponse({'status':'success', 'success_url':'/login/'})
        except Exception as error:
            return JsonResponse({'status':'error', 'message':f'BACKEND ERROR: {error}'})
    return render(request, 'users/register.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(username=username, password=password)
        if user is not None and user.role == 'Student':
            login(request, user)
            messages.success(request, f'{user} logged in successfully.')
            return JsonResponse({'status':'success', 'success_url':'/'})
        else:
            return JsonResponse({'status':'error', 'message':'Invalid username or password.'})
    return render(request, 'users/login.html')

def members_login_view(request, role):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(username=username, password=password)
        if user is not None and user.role == role:
            login(request, user)
            messages.success(request, f'{user.profile} logged in successfully.')
            return JsonResponse({'status':'success', 'success_url':f'/{role.lower()}/'})
        else:
            return JsonResponse({'status':'error', 'message':'Invalid username or password.'})
    return render(request, 'members/login.html', context={'role':role})

def logout_view(request):
    try:
        user = request.user
        logout(request)
        messages.success(request, f'{user} logged out successfully.')
    except Exception as error:
        messages.error(request, f'BACKEND ERROR: {error}')
    else:
        return redirect('index-view')
        
def about_us_view(request):
    return render(request, 'users/about_us.html')

def members_update_profile_view(request):
    if request.method == 'POST':
        try:
            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')
            email = request.POST.get('email')
            phone_number = request.POST.get('phone_number')
            username = request.POST.get('username')
            user = request.user

            if User.objects.filter(email=email).exists():
                if email != user.email:
                    return JsonResponse({'status':'error', 'message':'Email address already exists.'})
            
            if User.objects.filter(username=username).exists():
                if username != user.username:
                    return JsonResponse({'status':'error', 'message':'Username already exists.'})

            if Profile.objects.filter(phone_number=phone_number).exists():
                if phone_number != user.profile.phone_number:
                    return JsonResponse({'status':'error', 'message':'Phone number already exists.'})

            user.first_name = first_name
            user.last_name = last_name
            user.email = email
            user.username = username
            user.save()

            profile = Profile.objects.get(user=user)
            profile.phone_number = phone_number
            profile.save()
            
            messages.success(request, f'Profile of {profile} saved successfully.')
            return JsonResponse({'status':'success', 'success_url':request.META.get('HTTP_REFERER')})
        except Exception as error:
            return JsonResponse({'status':'error', 'message':f'BACKEND ERROR: {error}'})
    return redirect(f'{request.user.role.lower()}-profile-view')

def members_change_password_view(request):
    if request.method == 'POST':
        try:
            current_password = request.POST.get('current_password')
            new_password = request.POST.get('new_password')
            confirm_password = request.POST.get('confirm_password')
            username = request.user.username

            if new_password != confirm_password:
                    return JsonResponse({'status':'error', 'message':'Passwords does not match.'})

            user = authenticate(username=username, password=current_password)
            if user is not None:
                user.set_password(new_password)
                user.save()
                login(request,user)
                messages.success(request, f'Password for {user} changed successfully.')
                return JsonResponse({'status':'success', 'success_url':request.META.get('HTTP_REFERER')})
            else:
                return JsonResponse({'status':'error', 'message':'Current Password does not match.'})
        except Exception as error:
            return JsonResponse({'status':'error', 'message':f'BACKEND ERROR: {error}'})
    return redirect(f'{request.user.role.lower()}-profile-view')    

def members_delete_user_view(request, user_id):
    try:
        user = User.objects.get(id=user_id)
        deleted_user = user
        user.delete()
        messages.success(request, f'{deleted_user.role} {deleted_user} deleted successfully.')
        return redirect(request.META.get('HTTP_REFERER'))
    except Exception as error:
        messages.error(request, f'BACKEND ERROR: {error}')
        return redirect(f'{request.user.role.lower()}-index-view')



def admin_index_view(request):
    total_users = User.objects.all().count()
    hods = User.objects.filter(role='HOD').all().count()
    teachers = User.objects.filter(role='Teacher').all().count()
    students = User.objects.filter(role='Student').all().count()
    context = {
        'total_users':total_users,
        'hods':hods,
        'teachers':teachers,
        'students':students,
    }
    return render(request, 'members/admin/index.html', context=context)

def admin_profile_view(request):
    return render(request, 'members/admin/profile.html')

def admin_create_hod_view(request):
    if request.method == 'POST':
        try:
            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')
            email = request.POST.get('email')
            phone_number = request.POST.get('phone_number')
            department = request.POST.get('department')
            designation = request.POST.get('designation')
            username = request.POST.get('username')
            password = request.POST.get('password')
            confirm_password = request.POST.get('confirm_password')

            if User.objects.filter(email=email).exists():
                return JsonResponse({'status':'error', 'message':'Email address already exists.'})
            
            if User.objects.filter(username=username).exists():
                return JsonResponse({'status':'error', 'message':'Username already exists.'})
        
            if password != confirm_password:
                return JsonResponse({'status':'error', 'message':'Passwords does not match.'})

            if Profile.objects.filter(phone_number=phone_number).exists():
                return JsonResponse({'status':'error', 'message':'Phone number already exists.'})

            if Profile.objects.filter(department=department, user__role='HOD').exists():        
                    return JsonResponse({'status':'error', 'message':f'HOD for {department} already exists.'})

            user = User.objects.create_user(
                first_name = first_name,
                last_name = last_name,
                email = email,
                username = username,
                password = password,
                role = 'HOD'
            )
            profile = Profile.objects.create(
                user = user,
                phone_number = phone_number,
                designation = designation,
                department = department
            )

            messages.success(request, f'{profile} created successfully.')
            return JsonResponse({'status':'success', 'success_url':f'/admin/update/hod/{user.id}/'})
        except Exception as error:
            return JsonResponse({'status':'error', 'message':f'BACKEND ERROR: {error}'})
    return render(request, 'members/admin/create_hod.html')

def admin_update_hod_view(request, user_id):
    user = User.objects.get(id=user_id)

    if request.method == 'POST':
        try:
            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')
            email = request.POST.get('email')
            username = request.POST.get('username')
            phone_number = request.POST.get('phone_number')
            department = request.POST.get('department')
            designation = request.POST.get('designation')

            if User.objects.filter(email=email).exists():
                if email != user.email:
                    return JsonResponse({'status':'error', 'message':'Email address already exists.'})
            
            if User.objects.filter(username=username).exists():
                if username != user.username:
                    return JsonResponse({'status':'error', 'message':'Username already exists.'})

            if Profile.objects.filter(phone_number=phone_number).exists():
                if phone_number != user.profile.phone_number:
                    return JsonResponse({'status':'error', 'message':'Phone number already exists.'})

            if Profile.objects.filter(department=department, user__role='HOD').exists():        
                if department != user.profile.department:
                    return JsonResponse({'status':'error', 'message':f'HOD for {department} already exists.'})
            
            user.first_name = first_name
            user.last_name = last_name
            user.email = email
            user.username = username
            user.save()

            profile = Profile.objects.get(user=user)
            profile.phone_number = phone_number
            profile.department = department
            profile.designation = designation
            profile.save()

            messages.success(request, f'Profile {profile} saved successfully.')
            return JsonResponse({'status':'success', 'success_url':f'/admin/update/hod/{user.id}/'})
        except Exception as error:
            return JsonResponse({'status':'error', 'message':f'BACKEND ERROR: {error}'})
    return render(request, 'members/admin/update_hod.html', context={'user':user})

def admin_list_users_view(request, role):
    users = User.objects.filter(role=role).all()
    return render(request, 'members/admin/list_users.html', context={'users':users, 'role':role})


def hod_index_view(request):
    total_teachers = Profile.objects.filter(user__role = 'Teacher', department=request.user.profile.department).all().count()
    total_subjects = Subject.objects.filter(department=request.user.profile.department).all().count()
    recent_subjects = Subject.objects.filter(department=request.user.profile.department).all().reverse()
    teachers = User.objects.filter(role='Teacher').all().count()
    students = User.objects.filter(role='Student').all().count()
    context = {
        'total_teachers':total_teachers,
        'total_subjects':total_subjects,
        'recent_subjects':recent_subjects[:5],
        'teachers':teachers,
        'students':students,
    }
    return render(request, 'members/hod/index.html', context=context)

def hod_profile_view(request):
    return render(request, 'members/hod/profile.html')

def hod_create_subject_view(request):
    if request.method == 'POST':
        try:
            subject_name = request.POST.get('subject_name')
            subject_code = request.POST.get('subject_code')
            scheme = request.POST.get('scheme')
            semester = request.POST.get('semester')
            department = request.user.profile.department

            if Subject.objects.filter(subject_code=subject_code).exists():
                return JsonResponse({'status':'error', 'message':'Subject code already exists.'})
            
            if Subject.objects.filter(subject_name=subject_name, scheme=scheme, department=department).exists():
                return JsonResponse({'status':'error', 'message':f'{subject_name} exists for Scheme({scheme}) :{department}.'})
            
            subject = Subject.objects.create(subject_name=subject_name, subject_code=subject_code, scheme=scheme, semester=semester, department=department)
            messages.success(request, f'Subject {subject} created successfully.')
            return JsonResponse({'status':'success', 'success_url':f'/hod/update/subject/{subject.id}/'})
        except Exception as error:
            return JsonResponse({'status':'error', 'message':f'BACKEND ERROR: {error}'})
    return render(request, 'members/hod/subjects/create_subject.html')

def hod_update_subject_view(request, subject_id):
    subject = Subject.objects.get(id=subject_id)

    if request.method == 'POST':
        try:
            subject_name = request.POST.get('subject_name')
            subject_code = request.POST.get('subject_code')
            scheme = request.POST.get('scheme')
            semester = request.POST.get('semester')
            department = request.user.profile.department

            if Subject.objects.filter(subject_code=subject_code).exists():
                if subject_code != subject.subject_code:
                    return JsonResponse({'status':'error', 'message':'Subject code already exists.'})

            subjects = Subject.objects.filter(subject_name=subject_name,scheme=scheme,department=department)
            if subjects.exists() and subjects[0] != subject:    
                return JsonResponse({'status':'error', 'message':f'{subject_name} exists for Scheme({scheme}): {department}.'})
            
            subject.subject_name = subject_name
            subject.subject_code = subject_code 
            subject.scheme = scheme 
            subject.semester = semester
            subject.department = department
            subject.save()

            messages.success(request, f'Subject {subject} saved successfully.')
            return JsonResponse({'status':'success', 'success_url':f'/hod/update/subject/{subject.id}/'})
        except Exception as error:
            return JsonResponse({'status':'error', 'message':f'BACKEND ERROR: {error}'})
    return render(request, 'members/hod/subjects/update_subject.html', context={'subject':subject})

def hod_delete_subject_view(request, subject_id):
    try:
        subject = Subject.objects.get(id=subject_id)
        deleted_subject = subject
        subject.delete()
        messages.success(request, f'Subject {deleted_subject} deleted successfully.')
    except Exception as error:
        messages.error(request, f'BACKEND ERROR: {error}')
    else:
        return redirect('hod-list-subjects-view')

def hod_list_subjects_view(request):
    subjects = Subject.objects.filter(department=request.user.profile.department).all()
    return render(request, 'members/hod/subjects/list_subjects.html', context={'subjects':subjects})

def hod_create_teacher_view(request):
    if request.method == 'POST':
        try:
            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')
            email = request.POST.get('email')
            phone_number = request.POST.get('phone_number')
            department = request.POST.get('department')
            designation = request.POST.get('designation')
            experience = request.POST.get('experience')
            username = request.POST.get('username')
            password = request.POST.get('password')
            confirm_password = request.POST.get('confirm_password')

            if User.objects.filter(email=email).exists():
                return JsonResponse({'status':'error', 'message':'Email address already exists.'})
            
            if User.objects.filter(username=username).exists():
                return JsonResponse({'status':'error', 'message':'Username already exists.'})
        
            if password != confirm_password:
                return JsonResponse({'status':'error', 'message':'Passwords does not match.'})

            if Profile.objects.filter(phone_number=phone_number).exists():
                return JsonResponse({'status':'error', 'message':'Phone number already exists.'})
            
            selected_subjects = []
            for subject_code in request.POST.getlist('subject_codes'):
                subject = Subject.objects.get(subject_code=subject_code)
                if Profile.objects.filter(subjects=subject).exists():
                    return JsonResponse({'status':'error', 'message':f'Subject {subject} is already assigned to a teacher.'})
                selected_subjects.append(subject)

            user = User.objects.create_user(
                first_name = first_name,
                last_name = last_name,
                email = email,
                username = username,
                password = password,
                role = 'Teacher'
            )

            profile = Profile.objects.create(
                user = user,
                phone_number = phone_number,
                designation = designation,
                department = department,
                experience = float(experience)
            )
            profile.subjects.add(*selected_subjects)
            profile.save()

            messages.success(request, f'{profile} created successfully.')
            return JsonResponse({'status':'success', 'success_url':f'/hod/update/teacher/{user.id}/'})
        except Exception as error:
            return JsonResponse({'status':'error', 'message':f'BACKEND ERROR: {error}'})
    subjects = Subject.objects.filter(department=request.user.profile.department).all()
    return render(request, 'members/hod/create_teacher.html', context={'subjects':subjects})

def hod_update_teacher_view(request, user_id):
    user = User.objects.get(id=user_id)
    
    if request.method == 'POST':
        try:
            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')
            email = request.POST.get('email')
            phone_number = request.POST.get('phone_number')
            department = request.POST.get('department')
            designation = request.POST.get('designation')
            experience = request.POST.get('experience')
            username = request.POST.get('username')

            if User.objects.filter(email=email).exists():
                if email != user.email:
                    return JsonResponse({'status':'error', 'message':'Email address already exists.'})
            
            if User.objects.filter(username=username).exists():
                if username != user.username:
                    return JsonResponse({'status':'error', 'message':'Username already exists.'})

            if Profile.objects.filter(phone_number=phone_number).exists():
                if phone_number != user.profile.phone_number:
                    return JsonResponse({'status':'error', 'message':'Phone number already exists.'})

            user.first_name = first_name
            user.last_name = last_name
            user.email = email
            user.username = username
            user.save()

            profile = Profile.objects.get(user=user)
            profile.phone_number = phone_number
            profile.department = department
            profile.designation = designation
            profile.experience = float(experience)
            
            selected_subjects = []
            for subject_code in request.POST.getlist('subject_codes'):
                subject = Subject.objects.get(subject_code=subject_code)
                subject_profiles = Profile.objects.filter(subjects=subject)

                if subject_profiles.exists() and subject_profiles[0] != profile:
                    return {'status':'error', 'message':f'Subject {subject} is already assigned to a teacher.'}
                selected_subjects.append(subject)


            profile.subjects.clear()
            profile.subjects.add(*selected_subjects)
            profile.save()

            messages.success(request, f'Profile of {profile} saved successfully.')
            return JsonResponse({'status':'success', 'success_url':f'/hod/update/teacher/{user.id}/'})
        except Exception as error:
            return JsonResponse({'status':'error', 'message':f'BACKEND ERROR: {error}'})
    else:
        subjects = Subject.objects.all()
        selected_subjects = user.profile.subjects.values_list('subject_code', flat=True)
        return render(request, 'members/hod/update_teacher.html', context={'user':user,'subjects':subjects,'selected_subjects':selected_subjects})

def hod_list_users_view(request, role):
    users = User.objects.filter(role=role).all()
    return render(request, 'members/hod/list_users.html', context={'users':users, 'role':role})


def teacher_index_view(request):
    subjects = request.user.profile.subjects.all().count()
    question_sets = QuestionSet.objects.filter(subject__in=request.user.profile.subjects.all()).all().count()
    questions = Question.objects.filter(question_sets__in=QuestionSet.objects.filter(subject__in=request.user.profile.subjects.all())).all().count()

    total_question_papers = QuestionPaper.objects.all().count()
    question_papers = QuestionPaper.objects.filter(question_paper_subject__in=request.user.profile.subjects.all()).all().count()
    question_papers_complete = QuestionPaper.objects.filter(question_paper_subject__in=request.user.profile.subjects.all(), status="Complete").all().count()
    question_papers_pending = QuestionPaper.objects.filter(question_paper_subject__in=request.user.profile.subjects.all(), status="Incomplete").all().count()

    assignment_papers = QuestionPaper.objects.filter(question_paper_subject__in=request.user.profile.subjects.all(), question_paper_type="Assignment").all().count()
    unit_papers = QuestionPaper.objects.filter(question_paper_subject__in=request.user.profile.subjects.all(), question_paper_type="Unit Test").all().count()
    exam_papers = QuestionPaper.objects.filter(question_paper_subject__in=request.user.profile.subjects.all(), question_paper_type="Exam").all().count()


    context = {
        'subjects':subjects,
        'question_sets':question_sets,
        'questions':questions,
        'total_question_papers':total_question_papers,
        'question_papers':question_papers,
        'question_papers_complete':question_papers_complete,
        'question_papers_pending':question_papers_pending,
        'assignment_papers':assignment_papers,
        'unit_papers':unit_papers,
        'exam_papers':exam_papers,
    }
    print(assignment_papers, unit_papers, exam_papers)
    return render(request, 'members/teacher/index.html', context=context)

def teacher_profile_view(request):
    return render(request, 'members/teacher/profile.html')

def teacher_list_students_view(request):
    users = User.objects.filter(role='Student')
    return render(request, 'members/teacher/list_students.html', context={'users':users})

def assignment_pdf_view(request, pk):
    # Get the assignment object (example data fetching, replace as needed)
    assignment = QuestionPaper.objects.get(id=pk)
    
    # Create a response object
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{assignment.question_paper_title}.pdf"'

    # Create a PDF object using reportlab
    p = canvas.Canvas(response, pagesize=letter)
    width, height = letter

    
    # Set fonts and styles
    p.setFont("Helvetica-Bold", 10)

    # Add the institute name and other details (center aligned)
    p.drawCentredString(width / 2, height - 50, f"{Profile.objects.filter(subjects=assignment.question_paper_subject).first().user.institute}")
    p.setFont("Helvetica", 12)
    p.drawCentredString(width / 2, height - 70, f"Department of {assignment.question_paper_subject.department}")
    p.setFont("Helvetica-Bold", 12)
    p.drawCentredString(width / 2, height - 90, f"{assignment.question_paper_title}")
    p.setFont("Helvetica", 10)
    p.drawCentredString(width / 2, height - 110, f"(Academic Year {assignment.academic_year_start} - {assignment.academic_year_end})")

    # Add course details on the left and marks on the right
    p.setFont("Helvetica-Bold", 10)
    p.drawString(100, height - 140, "Course Title: ")
    p.setFont("Helvetica", 10)
    p.drawString(180, height - 140, f"{assignment.question_paper_subject.subject_name}")

    p.setFont("Helvetica-Bold", 10)
    p.drawString(100, height - 160, "Course Code: ")
    p.setFont("Helvetica", 10)
    p.drawString(180, height - 160, f"{assignment.question_paper_subject.subject_code}")

    p.setFont("Helvetica-Bold", 10)
    p.drawString(100, height - 180, "Semester: ")
    p.setFont("Helvetica", 10)
    p.drawString(180, height - 180, f"CO{assignment.question_paper_subject.semester[-1]}i")


    right_y = height - 140  # Starting Y position for the first item
    label_x = width - 120    # X position for the labels
    value_x = width - 50     # X position for the values (farther right for better spacing)

    if assignment.question_paper_type != 'Assignment':
        # Date
        p.setFont("Helvetica-Bold", 10)
        p.drawRightString(label_x, right_y, "Date: ")
        p.setFont("Helvetica", 10)
        formatted_date = assignment.exam_date.strftime("%d/%m/%y")
        p.drawRightString(value_x, right_y, f"{formatted_date}")
        right_y -= 20  # Move Y position down by 20 units

        # Time
        p.setFont("Helvetica-Bold", 10)
        p.drawRightString(label_x, right_y, "Time: ")
        p.setFont("Helvetica", 10)
        time_text = f'{assignment.exam_hour} Hour' if assignment.exam_minute is None else f'{assignment.exam_hour} Hour {assignment.exam_minute} Min.'
        p.drawRightString(value_x, right_y, time_text)
        right_y -= 20  # Move Y position down by 20 units

    # Marks (regardless of assignment type, marks are displayed)
    p.setFont("Helvetica-Bold", 10)
    p.drawRightString(label_x, right_y, "Marks: ")
    p.setFont("Helvetica", 10)
    p.drawRightString(value_x, right_y, f"{assignment.question_paper_total_marks}")



    # Draw a line separator
    p.setLineWidth(1)
    p.line(50, height - 200, width - 50, height - 200)

    # Iterate through the divisions and questions
    current_y = height - 220
    for division in assignment.divisions.all():
        # Division title and marks
        p.setFont("Helvetica-Bold", 10)
        p.drawString(100, current_y, f"Q({division.division_no}). {division.division_title}")
        p.setFont("Helvetica", 10)
        p.drawRightString(width - 100, current_y, f"(Marks: {division.division_mark})")
        current_y -= 20

        # List the questions under the division
        max_width = 400  # Max width in points that text should occupy
        line_height = 14  # Space between wrapped lines

        for i, question in enumerate(division.division_questions.all()):
            char = string.ascii_lowercase[i]
            question_text = f"{char}. {question.question_title}"

            # Wrap text to fit in max_width
            wrapped_lines = textwrap.wrap(question_text, width=90)  # Adjust width based on font size & page width

            p.setFont("Helvetica", 10)
            for line in wrapped_lines:
                p.drawString(120, current_y, line)
                current_y -= line_height

        current_y -= 10  # Add a little more space between divisions

    # Finish the PDF
    p.showPage()
    p.save()

    return response