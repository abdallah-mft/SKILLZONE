from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Achievement, UserAchievement
from .serializers import AchievementSerializer, UserAchievementSerializer
from django.db.models import Count, Sum, F, Q
from django.utils import timezone

class AchievementViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Achievement.objects.all()
    serializer_class = AchievementSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=['GET'])
    def my_achievements(self, request):
        user_achievements = UserAchievement.objects.filter(
            user=request.user
        ).select_related('achievement')
        serializer = UserAchievementSerializer(user_achievements, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['GET'])
    def available(self, request):
        earned_achievements = UserAchievement.objects.filter(
            user=request.user
        ).values_list('achievement_id', flat=True)
        
        available_achievements = Achievement.objects.exclude(
            id__in=earned_achievements
        )
        serializer = AchievementSerializer(available_achievements, many=True)
        return Response(serializer.data)
        
    @action(detail=True, methods=['GET'])
    def progress(self, request, pk=None):
        """Get detailed progress for a specific achievement"""
        achievement = self.get_object()
        try:
            user_achievement = UserAchievement.objects.get(
                user=request.user,
                achievement=achievement
            )
            serializer = UserAchievementSerializer(user_achievement)
            return Response(serializer.data)
        except UserAchievement.DoesNotExist:
            return Response({
                'achievement': AchievementSerializer(achievement).data,
                'progress': {},
                'earned': False
            })
            
    @action(detail=False, methods=['GET'])
    def leaderboard(self, request):
        """Get global achievement leaderboard"""
        from users.models import Profile
        
        leaderboard = Profile.objects.annotate(
            achievements_count=Count('achievements'),
            total_points=Sum('achievements__achievement__points_reward')
        ).order_by('-total_points', '-achievements_count')[:20]
        
        result = []
        for profile in leaderboard:
            result.append({
                'username': profile.user.username,
                'achievements_count': profile.achievements_count,
                'total_points': profile.total_points or 0,
                'rank': len(result) + 1
            })
            
        return Response(result)
        
    @action(detail=False, methods=['GET'])
    def statistics(self, request):
        """Get achievement statistics for the user"""
        user_achievements = UserAchievement.objects.filter(user=request.user)
        total_achievements = Achievement.objects.count()
        earned_achievements = user_achievements.count()
        
        # Group by type
        achievements_by_type = {}
        for achievement_type, _ in Achievement.TYPES:
            total = Achievement.objects.filter(type=achievement_type).count()
            earned = user_achievements.filter(achievement__type=achievement_type).count()
            achievements_by_type[achievement_type] = {
                'total': total,
                'earned': earned,
                'percentage': round((earned / total * 100) if total > 0 else 0, 1)
            }
            
        # Recent achievements
        recent = UserAchievementSerializer(
            user_achievements.order_by('-earned_date')[:5], 
            many=True
        ).data
        
        return Response({
            'total': total_achievements,
            'earned': earned_achievements,
            'percentage': round((earned_achievements / total_achievements * 100) if total_achievements > 0 else 0, 1),
            'by_type': achievements_by_type,
            'recent': recent,
            'points_earned': user_achievements.aggregate(
                total=Sum('achievement__points_reward')
            )['total'] or 0
        return Response(serializer.data)
