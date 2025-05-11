from django.utils import timezone
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import Quiz, QuizAttempt, Question, Answer, QuizAchievement, QuizProgress
from .serializers import (
    QuizListSerializer, 
    QuizDetailSerializer, 
    QuizAttemptSerializer
)
from django.urls import get_resolver
from django.db import transaction
from django.core.cache import cache
from users.models import Profile

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def quiz_list(request, course_id):
    """Get all quizzes for a course"""
    quizzes = Quiz.objects.filter(course_id=course_id)
    serializer = QuizListSerializer(quizzes, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def quiz_detail(request, quiz_id):
    """Get quiz details without questions"""
    quiz = get_object_or_404(Quiz, id=quiz_id)
    serializer = QuizListSerializer(quiz)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def start_quiz(request, quiz_id):
    """Start a new quiz attempt with randomization"""
    quiz = get_object_or_404(Quiz, id=quiz_id)
    
    # Check max attempts
    if quiz.max_attempts > 0:
        attempt_count = QuizAttempt.objects.filter(
            quiz=quiz,
            user=request.user.profile
        ).count()
        if attempt_count >= quiz.max_attempts:
            return Response({
                "error": "Maximum attempts reached"
            }, status=status.HTTP_400_BAD_REQUEST)
    
    # Check for existing incomplete attempt
    existing_attempt = QuizAttempt.objects.filter(
        quiz=quiz,
        user=request.user.profile,
        completed_at__isnull=True
    ).first()
    
    if existing_attempt:
        time_elapsed = timezone.now() - existing_attempt.started_at
        if time_elapsed.total_seconds() > quiz.time_limit:
            existing_attempt.is_passed = False
            existing_attempt.completed_at = timezone.now()
            existing_attempt.save()
        else:
            remaining_time = quiz.time_limit - int(time_elapsed.total_seconds())
            return Response({
                'attempt_id': existing_attempt.id,
                'remaining_time': remaining_time,
                'quiz': QuizDetailSerializer(quiz, context={'randomize': quiz.is_randomized}).data
            })
    
    # Create new attempt
    attempt = QuizAttempt.objects.create(
        quiz=quiz,
        user=request.user.profile
    )
    
    return Response({
        'attempt_id': attempt.id,
        'remaining_time': quiz.time_limit,
        'quiz': QuizDetailSerializer(quiz, context={'randomize': quiz.is_randomized}).data
    })

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def submit_quiz(request, quiz_id):
    """Submit quiz answers and calculate score with achievements"""
    quiz = get_object_or_404(Quiz, id=quiz_id)
    attempt = get_object_or_404(
        QuizAttempt,
        quiz=quiz,
        user=request.user.profile,
        completed_at__isnull=True
    )
    
    # Check time limit
    time_elapsed = timezone.now() - attempt.started_at
    if time_elapsed.total_seconds() > quiz.time_limit:
        attempt.is_passed = False
        attempt.completed_at = timezone.now()
        attempt.save()
        return Response({
            'message': 'Time limit exceeded',
            'score': 0,
            'is_passed': False
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Process answers
    answers = request.data.get('answers', {})
    total_points = 0
    max_points = 0
    
    for question in quiz.questions.all():
        max_points += question.points
        if str(question.id) in answers:
            answer = get_object_or_404(Answer, 
                id=answers[str(question.id)],
                question=question
            )
            if answer.is_correct:
                total_points += question.points
    
    # Calculate percentage score
    percentage_score = (total_points / max_points * 100) if max_points > 0 else 0
    
    # Update attempt
    attempt.score = percentage_score
    attempt.is_passed = percentage_score >= quiz.passing_score
    attempt.completed_at = timezone.now()
    attempt.save()
    
    # Update QuizProgress
    progress, _ = QuizProgress.objects.get_or_create(
        user=request.user.profile,
        quiz=quiz
    )
    progress.attempts_count += 1
    progress.total_time_spent += int(time_elapsed.total_seconds())
    progress.last_attempt_date = timezone.now()
    if percentage_score > progress.best_score:
        progress.best_score = percentage_score
    progress.completed = attempt.is_passed
    progress.save()
    
    # Award points and achievements
    points_earned = quiz.points_reward if attempt.is_passed else 0
    if points_earned > 0:
        profile = request.user.profile
        profile.points += points_earned
        profile.save()
    
    achievements, bonus_points = award_achievements(attempt)
    
    return Response({
        'score': percentage_score,
        'is_passed': attempt.is_passed,
        'points_earned': points_earned,
        'bonus_points': bonus_points,
        'achievements': achievements,
        'attempt': QuizAttemptSerializer(attempt).data
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def quiz_statistics(request, quiz_id):
    """Get quiz statistics"""
    quiz = get_object_or_404(Quiz, id=quiz_id)
    
    # Get user's best attempt
    user_attempts = QuizAttempt.objects.filter(
        quiz=quiz,
        user=request.user.profile,
        completed_at__isnull=False
    ).order_by('-score')
    
    user_stats = {
        'attempts_count': user_attempts.count(),
        'best_score': user_attempts.first().score if user_attempts.exists() else 0,
        'passed': user_attempts.filter(is_passed=True).exists()
    }
    
    # Get overall quiz statistics
    quiz_stats = quiz.get_statistics()
    
    return Response({
        'user_statistics': user_stats,
        'overall_statistics': quiz_stats
    })

@api_view(['GET'])
def list_urls(request):
    """Temporary view to list all URLs"""
    urls = get_resolver().reverse_dict
    available_paths = []
    
    for key, value in urls.items():
        if isinstance(key, str):
            available_paths.append({
                'name': key,
                'path': value[0][0][0]
            })
    
    return Response({
        'available_urls': available_paths
    })

def award_achievements(attempt):
    """Award achievements based on quiz performance"""
    quiz = attempt.quiz
    user = attempt.user
    
    # Use select_for_update to prevent race conditions
    with transaction.atomic():
        profile = Profile.objects.select_for_update().get(user=user)
        achievements = []
        total_bonus_points = 0
        
        # Perfect Score Achievement
        if attempt.score == 100:
            achievement, created = QuizAchievement.objects.get_or_create(
                user=user,
                quiz=quiz,
                achievement_type='PERFECT',
                defaults={'bonus_points': 50}
            )
            if created:
                achievements.append('PERFECT')
                total_bonus_points += 50
        
        # Speed Demon Achievement
        time_taken = (attempt.completed_at - attempt.started_at).total_seconds()
        if time_taken < (quiz.time_limit * 0.5):
            achievement, created = QuizAchievement.objects.get_or_create(
                user=user,
                quiz=quiz,
                achievement_type='FAST',
                defaults={'bonus_points': 30}
            )
            if created:
                achievements.append('FAST')
                total_bonus_points += 30
        
        # Winning Streak (using cached query)
        cache_key = f'quiz_streak_{user.id}_{quiz.id}'
        streak_count = cache.get(cache_key, 0)
        
        if attempt.is_passed:
            streak_count += 1
        else:
            streak_count = 0
        
        cache.set(cache_key, streak_count, timeout=86400)  # 24 hours
        
        if streak_count >= 3:
            achievement, created = QuizAchievement.objects.get_or_create(
                user=user,
                quiz=quiz,
                achievement_type='STREAK',
                defaults={'bonus_points': 40}
            )
            if created:
                achievements.append('STREAK')
                total_bonus_points += 40
        
        # Add bonus points atomically
        if total_bonus_points > 0:
            profile.add_points(total_bonus_points)
            
        return achievements, total_bonus_points
