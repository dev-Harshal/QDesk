from django.urls import path
from Questions.views import *

urlpatterns = [
    path('create/question-set/', create_question_set_view, name='create-question-set-view'),
    path('update/question-set/<int:question_set_id>/', update_question_set_view, name='update-question-set-view'),
    path('list/question-sets/', list_question_sets_view, name='list-question-sets-view'),
    path('delete/question-sets/<int:subject_id>/', delete_question_sets_view, name='delete-question-sets-view'),
    path('delete/question-set/<int:subject_id>/<int:unit>/', delete_question_set_view, name='delete-question-set-view'),
    path('create/questions/<int:question_set_id>/', create_questions_view, name='create-questions-view'),
    path('update/questions/<int:subject_id>/<int:unit>/', update_questions_view, name='update-questions-view'),
    path('list/questions/<int:question_set_id>/', list_questions_view, name='list-questions-view'),

    path('create/question-paper/', create_question_paper_view, name='create-question-paper-view'),
    path('list/question-papers/', list_question_papers_view, name='list-question-papers-view'),
    path('question-papers/list/<int:subject_id>', question_papers_list_view, name='question-papers-list-view'),
    path('detail/question-paper/<int:question_paper_id>/', detail_question_paper_view, name='detail-question-paper-view'),
    path('create/division/<int:question_paper_id>/', create_division_view, name='create-division-view'),
    path('update/division/<int:division_id>/<int:question_paper_id>/', update_division_view, name='update-division-view'),
    path('add/questions/<int:division_id>/<int:question_paper_id>/', add_questions_view, name='add-questions-view'),
    path('update/questions-list/<int:division_id>/<int:question_paper_id>/', update_questions_list_view, name='update-questions-list-view'),

]
