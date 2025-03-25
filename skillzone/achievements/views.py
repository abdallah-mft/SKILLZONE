from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Achievement, UserAchievement
from .serializers import AchievementSerializer, UserAchievementSerializer

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