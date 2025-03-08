from django.contrib import admin
from .models import Quiz, Question, Answer, QuizAttempt

class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 4
    fields = ['text', 'is_correct']

class QuestionAdmin(admin.ModelAdmin):
    inlines = [AnswerInline]
    list_display = ['text', 'quiz', 'points']
    search_fields = ['text', 'quiz__title']

class QuestionInline(admin.StackedInline):
    model = Question
    extra = 1
    show_change_link = True

@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ['title', 'course', 'time_limit', 'points_reward', 'passing_score', 'question_count']
    list_filter = ['course', 'time_limit']
    search_fields = ['title', 'description']
    inlines = [QuestionInline]

    def question_count(self, obj):
        return obj.questions.count()
    question_count.short_description = 'Questions'

@admin.register(QuizAttempt)
class QuizAttemptAdmin(admin.ModelAdmin):
    list_display = ['user', 'quiz', 'score', 'started_at', 'completed_at', 'is_passed', 'time_taken']
    list_filter = ['is_passed', 'quiz']
    search_fields = ['user__user__username', 'quiz__title']
    readonly_fields = ['started_at', 'completed_at', 'score', 'is_passed']

    def time_taken(self, obj):
        if obj.completed_at and obj.started_at:
            seconds = (obj.completed_at - obj.started_at).total_seconds()
            return f"{int(seconds)} seconds"
        return "Incomplete"
    time_taken.short_description = 'Time Taken'

admin.site.register(Question, QuestionAdmin)