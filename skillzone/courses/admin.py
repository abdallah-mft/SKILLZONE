from django.contrib import admin
from .models import Course, Lesson

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'course_type', 'points_required')
    search_fields = ('title',)
    list_filter = ('course_type',)

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if obj and obj.course_type == 'HARD':
            form.base_fields['points_required'].required = True
            form.base_fields['points_required'].help_text = 'Points required to unlock this HARD skill course'
        return form

@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'points_required')
    list_filter = ('course',)
    search_fields = ('title',)
# Register your models here.
