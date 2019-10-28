from django.contrib import admin
from .models import ExamPaPer,QuestionExam

@admin.register(ExamPaPer)
class ExamPaPerAdmin(admin.ModelAdmin):
    list_display = ('id','name','status')
@admin.register(QuestionExam)
class QuestionExamAdmin(admin.ModelAdmin):
    list_display = ('id','title','type')
