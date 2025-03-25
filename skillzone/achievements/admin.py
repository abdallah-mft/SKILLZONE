from django.contrib import admin
from .models import Achievement, UserAchievement

@admin.register(Achievement)
class AchievementAdmin(admin.ModelAdmin):
    list_display = ('title', 'type', 'points_reward')
    list_filter = ('type',)
    search_fields = ('title', 'description')

@admin.register(UserAchievement)
class UserAchievementAdmin(admin.ModelAdmin):
    list_display = ('user', 'achievement', 'earned_date')
    list_filter = ('achievement__type', 'earned_date')
    search_fields = ('user__username', 'achievement__title')