from django.contrib import admin
from .models import LearnPlan, LearnProgress
# Register your models here.
@admin.register(LearnPlan)
class LearnPlanAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'status')


@admin.register(LearnProgress)
class LearnProgressAdmin(admin.ModelAdmin):
    list_display = ('id', 'status', 'trainer')
