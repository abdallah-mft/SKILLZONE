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
    
    
    if quiz.max_attempts > 0:
        attempt_count = QuizAttempt.objects.filter(
            quiz=quiz,
            user=request.user.profile
        ).count()
        if attempt_count >= quiz.max_attempts:
            return Response({
                "error": "Maximum attempts reached"
            }, status=status.HTTP_400_BAD_REQUEST)
    
    
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
    
    
    percentage_score = (total_points / max_points * 100) if max_points > 0 else 0
    
    
    attempt.score = percentage_score
    attempt.is_passed = percentage_score >= quiz.passing_score
    attempt.completed_at = timezone.now()
    attempt.save()
    
    
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
    
    
    with transaction.atomic():
        profile = Profile.objects.select_for_update().get(user=user)
        achievements = []
        total_bonus_points = 0
        
        
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
        
        
        cache_key = f'quiz_streak_{user.id}_{quiz.id}'
        streak_count = cache.get(cache_key, 0)
        
        if attempt.is_passed:
            streak_count += 1
        else:
            streak_count = 0
        
        cache.set(cache_key, streak_count, timeout=86400)  
        
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
        
        
        if total_bonus_points > 0:
            profile.add_points(total_bonus_points)
            
        return achievements, total_bonus_points

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def quiz_data_for_frontend(request, course_id):
    """Get quiz data in frontend-friendly format for a specific course"""
    try:
        # Find quiz by course ID (using integer ID)
        quiz = Quiz.objects.filter(course_id=course_id).first()
        
        if not quiz:
            return Response({
                "error": "Quiz not found",
                "course_id": course_id,
                "available_quizzes": list(Quiz.objects.values_list('id', 'course_id', 'title'))
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Get all questions with their answers
        questions = []
        for question in quiz.questions.all().prefetch_related('answers'):
            # Get all answers for this question
            answer_objects = list(question.answers.all())
            
            if not answer_objects:
                # Skip questions with no answers
                continue
                
            options = [answer.text for answer in answer_objects]
            
            # Find the correct answer index, default to 0 if none found
            try:
                correct_option_index = next((i for i, answer in enumerate(answer_objects) if answer.is_correct), 0)
            except Exception as e:
                correct_option_index = 0
                
            questions.append({
                "id": f"q{question.id}",
                "question": question.text,
                "options": options,
                "correctOptionIndex": correct_option_index,
                "points": question.points
            })
        
        if not questions:
            return Response({
                "error": "No valid questions found for this quiz",
                "quiz_id": quiz.id,
                "quiz_title": quiz.title,
                "course_id": course_id,
                "debug_info": {
                    "total_questions": quiz.questions.count(),
                    "questions_with_answers": quiz.questions.filter(answers__isnull=False).distinct().count(),
                    "questions_with_correct_answers": quiz.questions.filter(answers__is_correct=True).distinct().count()
                }
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Format response to match frontend structure
        time_per_question = quiz.time_limit // len(questions) if len(questions) > 0 and quiz.time_limit else 30
        
        response_data = {
            "id": f"c{course_id}q{quiz.id}",
            "courseId": str(course_id),
            "title": quiz.title,
            "timePerQuestion": time_per_question,
            "timeUnit": "seconds",
            "questions": questions
        }
        
        return Response(response_data)
    
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        
        # Log the error
        logger.error(f"Error in quiz_data_for_frontend: {str(e)}")
        logger.error(error_details)
        
        # Return detailed error information
        return Response({
            "error": "An error occurred while retrieving quiz data",
            "details": str(e),
            "traceback": error_details if settings.DEBUG else "Enable DEBUG mode to see traceback",
            "course_id": course_id
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
