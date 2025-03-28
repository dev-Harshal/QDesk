from django.db import models
from Users.models import *
# Create your models here.

class Question(models.Model):
    id = models.BigAutoField(primary_key=True)
    question_title = models.CharField(max_length=255, null=False, blank=False)
    question_mark = models.IntegerField(null=False, blank=False, default=0)
    question_levels = models.CharField(max_length=255, null=False, blank=False)

    def __str__(self):
        return self.question_title

    class Meta:
        db_table = 'Questions'

class QuestionSet(models.Model):
    id = models.BigAutoField(primary_key=True)
    subject = models.ForeignKey(Subject, related_name='question_sets', on_delete=models.CASCADE)
    unit = models.IntegerField(null=False, blank=False, default=0)
    unit_title = models.CharField(max_length=255, null=False, blank=False)
    co = models.IntegerField(null=False, blank=False, default=0)
    co_title = models.CharField(max_length=255, null=False, blank=False)
    questions = models.ManyToManyField(Question, related_name='question_sets', blank=True)
    created_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f'{self.subject} (Unit {self.unit})'

    class Meta:
        db_table = 'Question Sets'

class Division(models.Model):
    id = models.BigAutoField(primary_key=True)
    division_no = models.IntegerField(name=False, blank=False, default=1)
    division_title = models.CharField(max_length=255, null=False, blank=False)
    division_mark = models.IntegerField(null=False, blank=False, default=0)
    mark_per_question = models.IntegerField(null=False, blank=False, default=0)
    extra_question = models.IntegerField(null=False, blank=False, default=0)
    division_questions = models.ManyToManyField(Question, related_name='divisions', blank=True)
    status = models.CharField(max_length=100, null=False, blank=False, default='Incomplete')

    def __str__(self):
        return self.division_title
    
    def status_check(self ,*args, **kwargs):
        if self.division_questions.all().count() == (self.division_mark / self.mark_per_question) + (self.extra_question):
            self.status = "Complete"
        else:
            self.status = "Incomplete"
        super().save(*args, **kwargs)

    class Meta:
        db_table = 'Divisions'

class QuestionPaper(models.Model):
    id = models.BigAutoField(primary_key=True)
    question_paper_type = models.CharField(max_length=20, null=False, blank=False)
    question_paper_title = models.CharField(max_length=255, null=False, blank=False)
    question_paper_subject = models.ForeignKey(Subject, related_name='question_papers', on_delete=models.CASCADE)
    question_paper_total_marks = models.IntegerField(null=False, blank=False, default=0)
    question_count = models.IntegerField(null=False, blank=False, default=1)
    academic_year_start =  models.IntegerField(null=False, blank=False, default=2024)
    academic_year_end =  models.PositiveIntegerField(null=False, blank=False, default=2025)
    exam_date = models.DateField(null=True, blank=True)
    exam_hour = models.PositiveIntegerField(null=True, blank=True)
    exam_minute = models.PositiveIntegerField(null=True, blank=True)
    
    divisions = models.ManyToManyField(Division, related_name='question_papers')
    status = models.CharField(max_length=100, null=False, blank=False, default='Incomplete')
    created_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f'{self.question_paper_title} ({self.academic_year_start}-{self.academic_year_end})'

    def status_check(self ,*args, **kwargs):
        status = 'Complete'

        print(self.divisions.all().values_list('status', flat=True),"DIV")
        for division in self.divisions.all().values_list('status', flat=True):
            if division == 'Incomplete':
                status = 'Incomplete'
        
        if self.divisions.all().count() < self.question_count:
            status = 'Incomplete'

        divisions_marks = self.divisions.values_list('division_mark', flat=True)
        if sum(divisions_marks) > self.question_paper_total_marks:
            status = 'Incomplete'

        self.status = status
        super().save(*args, **kwargs)

    class Meta:
        db_table = 'Question Papers'

