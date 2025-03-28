import traceback
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib import messages
from django.db.models import Min, Prefetch
from Users.models import *
from Questions.models import *
from Questions.services import *
# Create your views here.

def create_question_set_view(request):
    if request.method == 'POST':
        try:
            subject_code = request.POST.get('subject_code')
            subject = Subject.objects.get(subject_code=subject_code)

            unit = int(request.POST.get('unit'))
            unit_title = request.POST.get('unit_title')
            co = int(request.POST.get('co'))
            co_title = request.POST.get('co_title')

            if QuestionSet.objects.filter(subject=subject, unit=unit).exists():
                return JsonResponse({'status':'error', 'message':f'{subject} Question set for Unit :{unit} already exists'})
            if QuestionSet.objects.filter(subject=subject, co=co).exists():
                return JsonResponse({'status':'error', 'message':f'{subject} Question set for Co :{co} already exists'})

            question_set = QuestionSet.objects.create(
                subject = subject,
                unit = unit,
                unit_title = unit_title,
                co = co,
                co_title = co_title
            )

            messages.success(request, f'Question set for {question_set} created successfully.')
            return JsonResponse({'status':'success', 'success_url':f'/teacher/create/questions/{question_set.id}/'})
        except Exception as error:
            return JsonResponse({'status':'error', 'message':f'BACKEND ERROR: {error}'})
    subjects = request.user.profile.subjects.all()
    return render(request, 'question_sets/create_question_set.html', context={'subjects':subjects})

def create_questions_view(request, question_set_id):
    question_set = QuestionSet.objects.get(id=question_set_id)

    if request.method == 'POST':
        try:
            question_titles = request.POST.getlist('question_title[]')
            question_marks = request.POST.getlist('question_mark[]')

            created_questions = []
            for title, mark in zip(question_titles, question_marks):
                levels = classify_blooms_taxonomy(title)
                question = Question.objects.create(question_title=title, question_mark=int(mark), question_levels=levels)
                created_questions.append(question)
            question_set.questions.add(*created_questions)

            messages.success(request, f'Questions added for {question_set}.')
            return JsonResponse({'status':'success', 'success_url':f'/teacher/update/questions/{question_set.subject.id}/{question_set.unit}/'})
        except Exception as error:
            return JsonResponse({'status':'error', 'message':f'BACKEND ERROR: {error}'})
    return render(request, 'question_sets/questions/create_questions.html', context={'question_set':question_set})

def update_questions_view(request, subject_id, unit):
    subject = Subject.objects.get(id=subject_id)
    question_set = QuestionSet.objects.get(subject=subject, unit=unit)

    if request.method == 'POST':
        try:
            old_question_ids = request.POST.getlist('old_question_id[]')
            old_question_titles = request.POST.getlist('old_question_title[]')
            old_question_marks = request.POST.getlist('old_question_mark[]')
            
            question_titles = request.POST.getlist('question_title[]')
            question_marks = request.POST.getlist('question_mark[]')

            for id, title, mark in zip(old_question_ids, old_question_titles, old_question_marks):
                levels = classify_blooms_taxonomy(title)
                question = Question.objects.get(id=int(id))
                question.question_title = title
                question.question_mark = int(mark)
                question.question_levels = levels
                question.save()
            
            for question in question_set.questions.all():
                if question.id not in [int(x) for x in old_question_ids]:
                    question.delete()

            new_questions = []
            for title, mark in zip(question_titles, question_marks):
                levels = classify_blooms_taxonomy(title)
                question = Question.objects.create(question_title=title, question_mark=int(mark), question_levels=levels)
                new_questions.append(question)

            question_set.questions.add(*new_questions)

            messages.success(request, f'Questions updated for Question set of {question_set}.')
            return JsonResponse({'status':'success', 'success_url':f'/teacher/update/questions/{question_set.subject.id}/{question_set.unit}/'})
        except Exception as error:
            return JsonResponse({'status':'error', 'message':f'Error(Contant Dev): {error}'})
    else:
        question_sets =QuestionSet.objects.filter(subject=question_set.subject)
        units = list(set(question_sets.values_list('unit', flat=True).order_by('unit')))
        questions = question_set.questions.all()
        return render(request, 'question_sets/questions/update_questions.html', context={'question_set':question_set,'questions':questions, 'units':units, 'current_unit':question_set.unit})

def update_question_set_view(request, question_set_id):
    question_set = QuestionSet.objects.get(id=question_set_id)   
    
    if request.method == 'POST':
        try:
            subject_code = request.POST.get('subject_code')
            subject = Subject.objects.get(subject_code=subject_code)

            unit = int(request.POST.get('unit'))
            unit_title = request.POST.get('unit_title')
            co = int(request.POST.get('co'))
            co_title = request.POST.get('co_title')

            question_set_units = QuestionSet.objects.filter(subject=subject, unit=unit)

            if question_set_units.exists() and question_set_units[0] != question_set:
                return JsonResponse({'status':'error', 'message':f'Question set for Unit :{unit} already exists'})
            
            question_set_cos = QuestionSet.objects.filter(subject=subject, co=int(co))
            if question_set_cos.exists() and question_set_cos[0] != question_set:
                return JsonResponse({'status':'error', 'message':f'Question set for Co :{co} already exists'})

            question_set.subject = subject
            question_set.unit = unit
            question_set.unit_title = unit_title
            question_set.co = co
            question_set.co_title = co_title
            question_set.save()

            messages.success(request, f'Question set for {question_set} saved successfuully.')
            return JsonResponse({'status':'success', 'success_url':f'/teacher/update/question-set/{question_set.id}/'})
        except Exception as error:
            return JsonResponse({'status':'error', 'message':f'BACKEND ERROR: {error}'})
    subjects = request.user.profile.subjects.all()
    return render(request, 'question_sets/update_question_set.html', context={'question_set':question_set,'subjects':subjects})

def list_question_sets_view(request):
    distinct_question_set_subjects = request.user.profile.subjects.filter(
        question_sets__in=QuestionSet.objects.filter(subject__in=request.user.profile.subjects.all())
    ).distinct().annotate(min_unit=Min('question_sets__unit'))
    return render(request, 'question_sets/list_question_sets.html', context={'subjects':distinct_question_set_subjects})

def delete_question_set_view(request, subject_id, unit):
    try:
        subject = Subject.objects.get(id=subject_id)
        question_set = QuestionSet.objects.get(subject=subject, unit=unit)

        for question in question_set.questions.all():
            question.delete()
        question_set.delete()
        messages.success(request, f'Question set for {question_set} deleted successfully.')

        remaining_question_sets = QuestionSet.objects.filter(subject=subject).values_list('unit', flat=True)
        if remaining_question_sets:
            remaining_question_sets = sorted([int(u) for u in remaining_question_sets])
            closest_unit = min(remaining_question_sets, key=lambda x: abs(x - unit))
            return redirect('update-questions-view', subject_id=subject.id, unit=closest_unit)
        return redirect('list-question-sets-view')
    except Exception as error:
        messages.error(request, f'BACKEND ERROR: {error}')
        return redirect('list-question-sets-view')

def delete_question_sets_view(request, subject_id):
    try:
        subject = Subject.objects.get(id=subject_id)
        question_sets = QuestionSet.objects.filter(subject=subject)

        for question_set in question_sets:
            for question in question_set.questions.all():
                question.delete()
        question_sets.delete()

        messages.success(request, f'Question sets for {subject} deleted successfully.')
        return redirect('list-question-sets-view')
    except Exception as error:
        messages.error(request, f'BACKEND ERROR: {error}')
        return redirect('list-question-sets-view')
        
def list_questions_view(request, question_set_id):
    question_set = QuestionSet.objects.get(id=question_set_id)
    questions = question_set.questions.all().order_by('question_mark', 'question_levels')
    return render(request, 'question_sets/questions/list_questions.html', context={'question_set':question_set,'questions':questions})


# QUESTION PAPERS VIEWS

def create_question_paper_view(request):
    if request.method == 'POST':
        try:
            question_paper_type = request.POST.get('question_paper_type')
            question_paper_title = request.POST.get('question_paper_title')
            question_paper_subject = Subject.objects.get(subject_code=request.POST.get('subject_code'))
            question_paper_total_marks = request.POST.get('question_paper_total_marks')
            question_count = request.POST.get('question_count')
            academic_year_start = request.POST.get('academic_year_start')
            academic_year_end = request.POST.get('academic_year_end')
            exam_date = request.POST.get('exam_date')
            exam_hour = request.POST.get('exam_hour')
            exam_minute = request.POST.get('exam_minute')

            if int(academic_year_end) - int(academic_year_start) > 1:
                return JsonResponse({'status':'error', 'message':f'Academic Year cannot be more than 1 Year.'})
            
            if question_paper_type != 'Assignment':
                if question_paper_type == 'Unit Test':
                    if QuestionPaper.objects.filter(question_paper_type=question_paper_type, question_paper_title__iexact=question_paper_title ,question_paper_subject=question_paper_subject, academic_year_start=academic_year_start, academic_year_end=academic_year_end).exists():
                        return JsonResponse({'status':'error', 'message':f'{question_paper_subject.subject_name} {question_paper_title} paper for {academic_year_start}-{academic_year_end} already exists.'})
                else:
                    if QuestionPaper.objects.filter(question_paper_type=question_paper_type, question_paper_title__iexact=question_paper_title,question_paper_subject=question_paper_subject, academic_year_start=academic_year_start, academic_year_end=academic_year_end).exists():
                        return JsonResponse({'status':'error', 'message':f'Exam Paper for {question_paper_subject.subject_name} for {academic_year_start}-{academic_year_end} already exists.'})
            else:
                if QuestionPaper.objects.filter(question_paper_type=question_paper_type, question_paper_title__iexact=question_paper_title ,question_paper_subject=question_paper_subject, academic_year_start=academic_year_start, academic_year_end=academic_year_end).exists():
                    return JsonResponse({'status':'error', 'message':f'{question_paper_title} for {question_paper_subject.subject_name} for {academic_year_start}-{academic_year_end} already exists.'})
            
            question_paper = QuestionPaper.objects.create(
                question_paper_type = question_paper_type,
                question_paper_title = question_paper_title,
                question_paper_subject = question_paper_subject,
                question_paper_total_marks = int(question_paper_total_marks),
                question_count = int(question_count),
                academic_year_start = int(academic_year_start),
                academic_year_end = int(academic_year_end),
                exam_date = exam_date if exam_date != "" else None,
                exam_hour = int(exam_hour) if exam_hour != "" else None,
                exam_minute = int(exam_minute) if exam_minute != "" else None
            )

            messages.success(request, f'Question Paper for {question_paper} created successfully.')
            return JsonResponse({'status':'success', 'success_url':f'/teacher/create/division/{question_paper.id}/'})
            
        except Exception as error:
            return JsonResponse({'status':'error', 'message':f'Error(Contant Dev): {error}'})
            
    question_sets_subjects = Subject.objects.filter(
            question_sets__in=QuestionSet.objects.filter(subject__in=request.user.profile.subjects.all())
        ).distinct()
    return render(request, 'question_papers/create_question_paper.html', context={'question_sets_subjects':question_sets_subjects})

def create_division_view(request, question_paper_id):
    question_paper = QuestionPaper.objects.get(id=question_paper_id)
    if request.method == 'POST':
        try:
            division_no = request.POST.get('division_no') 
            division_title = request.POST.get('division_title')
            division_mark = request.POST.get('division_mark')
            mark_per_question = request.POST.get('mark_per_question')
            extra_question = request.POST.get('extra_question')

            if question_paper.divisions.all().count() == question_paper.question_count:
                return JsonResponse({'status':'error', 'message':f'{question_paper} contains only {question_paper.question_count} questions.'})

            divisons = question_paper.divisions.all().values_list('division_mark', flat=True)
            if sum(divisons) + int(division_mark) > question_paper.question_paper_total_marks:
                return JsonResponse({'status':'error', 'message':f'{question_paper} total mark limit exceeded.'})

            if question_paper.divisions.filter(division_no=division_no).exists():
                return JsonResponse({'status':'error', 'message':f'Question {division_no} already exists in {question_paper}.'})
            
            division = Division.objects.create(
                division_no = int(division_no),
                division_title = division_title,
                division_mark = int(division_mark),
                mark_per_question = int(mark_per_question),
                extra_question = int(extra_question)
            )

            question_paper.divisions.add(division)
            division.status_check()
            question_paper.status_check()
            

            messages.success(request, f'Question {division_no} for {question_paper} created successfully.')
            return JsonResponse({'status':'success', 'success_url':f'/teacher/add/questions/{division.id}/{question_paper.id}/'})
        except Exception as error:
            return JsonResponse({'status':'error', 'message':f'Error(Contant Dev): {error}'})
    question_paper = QuestionPaper.objects.get(id=question_paper_id)
    return render(request, 'question_papers/divisions/create_division.html', context={'question_paper':question_paper})

def list_question_papers_view(request):
    subjects = request.user.profile.subjects.filter(
        question_papers__in=QuestionPaper.objects.filter(question_paper_subject__in=request.user.profile.subjects.all())
    ).distinct()
    return render(request, 'question_papers/list_question_papers.html', context={'subjects':subjects})

def question_papers_list_view(request, subject_id):
    subject = Subject.objects.get(id=subject_id)
    question_papers = QuestionPaper.objects.filter(question_paper_subject=subject).order_by('question_paper_type')
    return render(request, 'question_papers/question_papers_list.html', context={'question_papers':question_papers, 'subject':subject})

def detail_question_paper_view(request, question_paper_id):
    question_paper = QuestionPaper.objects.get(id=question_paper_id)
    return render(request, 'question_papers/detail_question_paper.html', context={'question_paper':question_paper})

def add_questions_view(request, division_id, question_paper_id):
    division = Division.objects.get(id=division_id)
    question_paper = QuestionPaper.objects.get(id=question_paper_id)

    if request.method == 'POST':
        try:
            selected_question_ids = request.POST.getlist('selected_question_id[]')

            if len(selected_question_ids) > (division.division_mark / division.mark_per_question) + (division.extra_question):
                return JsonResponse({'status':'error', 'message':f'Select only {int(division.division_mark / division.mark_per_question)} Questions and {division.extra_question} Extras. (Selected: {len(selected_question_ids)})'})
        
            selected_questions = []   

            for id in selected_question_ids:
                question = Question.objects.get(id=int(id))
                selected_questions.append(question)
            division.division_questions.add(*selected_questions)
            division.status_check()
            question_paper.status_check()

            messages.success(request, f'Questions added for Q.({division.division_no} of {question_paper}).')
            return JsonResponse({'status':'success', 'success_url':f'/teacher/detail/question-paper/{question_paper.id}/'})
        except Exception as error:
            return JsonResponse({'status':'error', 'message':f'Error(Contant Dev): {error}'})
    
    question_sets = QuestionSet.objects.filter(subject=question_paper.question_paper_subject).order_by('unit')
    question_sets = question_sets.prefetch_related(
        Prefetch(
            'questions',
            queryset=Question.objects.filter(question_mark=division.mark_per_question),
            to_attr='filtered_questions'
        )
    )
    return render(request, 'question_papers/questions/add_questions.html', context={'division':division, 'question_sets':question_sets, 'question_paper':question_paper})

def update_division_view(request, division_id, question_paper_id):
    division = Division.objects.get(id=division_id)
    question_paper = QuestionPaper.objects.get(id=question_paper_id)

    if request.method == 'POST':
        try:
            division_no = request.POST.get('division_no') 
            division_title = request.POST.get('division_title')
            division_mark = request.POST.get('division_mark')
            mark_per_question = request.POST.get('mark_per_question')
            extra_question = request.POST.get('extra_question')

            divisions = question_paper.divisions.filter(division_no=int(division_no))

            if divisions.exists() and divisions[0] != division:
                return JsonResponse({'status':'error', 'message':f'Question {division_no} already exists in {question_paper}.'})

            division_total = question_paper.divisions.all().values_list('division_mark', flat=True)
            total = sum([int(x) for x in division_total]) - int(division.division_mark)
            if total + int(division_mark) > question_paper.question_paper_total_marks:
                return JsonResponse({'status':'error', 'message':f'{question_paper} total mark limit exceeded.'})
            
            division.division_no = int(division_no)
            division.division_title = division_title
            division.division_mark = int(division_mark)
            division.extra_question = int(extra_question)

            if int(mark_per_question) != division.mark_per_question:
                division.division_questions.clear()
            division.mark_per_question = int(mark_per_question)

            division.save()
            division.status_check()
            question_paper.status_check()

            messages.success(request, f'Question {division_no} for {question_paper} saved successfully.')
            return JsonResponse({'status':'success', 'success_url':f'/teacher/update/questions-list/{division.id}/{question_paper.id}/'})
        except Exception as error:
            return JsonResponse({'status':'error', 'message':f'Error(Contant Dev): {error}'})

def update_questions_list_view(request, division_id, question_paper_id):
    division = Division.objects.get(id=division_id)
    question_paper = QuestionPaper.objects.get(id=question_paper_id)

    if request.method == 'POST':
        try:
            current_selected_questions = set(division.division_questions.values_list('id', flat=True))

            selected_question_ids = set(map(int, request.POST.getlist('selected_question_id[]')))

            max_questions = (division.division_mark // division.mark_per_question) + division.extra_question
            if len(selected_question_ids) > max_questions:
                return JsonResponse({'status': 'error', 'message': f'Select only {int(division.division_mark / division.mark_per_question)} Questions and {division.extra_question} Extras. (Selected: {len(selected_question_ids)})'})

            questions_to_add = selected_question_ids - current_selected_questions
            questions_to_remove = current_selected_questions - selected_question_ids

            if questions_to_add:
                division.division_questions.add(*questions_to_add)

            if questions_to_remove:
                division.division_questions.remove(*questions_to_remove)

            division.status_check()
            question_paper.status_check()
            messages.success(request, f'Questions added for Q.({division.division_no} of {question_paper}).')
            return JsonResponse({'status':'success', 'success_url':f'/teacher/update/questions-list/{division.id}/{question_paper.id}/'})

        except Exception as error:
            return JsonResponse({'status': 'error', 'message': f'BACKEND ERROR: {error}'})

    # Fetch question sets based on the subject of the question paper
    question_sets = QuestionSet.objects.filter(subject=question_paper.question_paper_subject).order_by('unit')
    question_sets = question_sets.prefetch_related(
        Prefetch(
            'questions',
            queryset=Question.objects.filter(question_mark=division.mark_per_question),
            to_attr='filtered_questions'
        )
    )
    return render(request, 'question_papers/questions/update_questions_list.html', context={'division': division, 'question_paper': question_paper, 'question_sets': question_sets})
   


