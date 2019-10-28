from django.contrib import admin
from .models import ExamPlan, ExamProgress
# Register your models here.
@admin.register(ExamPlan)
class ExamPlanAdmin(admin.ModelAdmin):
    list_display = ('id','name','status')

@admin.register(ExamProgress)
class ExamProgressAdmin(admin.ModelAdmin):
    list_display = ('id', 'status','trainer')
