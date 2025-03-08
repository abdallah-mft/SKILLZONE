from django.utils import timezone
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import Quiz, QuizAttempt, Question, Answer
from .serializers import (
    QuizListSerializer, 
    QuizDetailSerializer, 
    QuizAttemptSerializer
)
from django.urls import get_resolver

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
    """Start a new quiz attempt"""
    quiz = get_object_or_404(Quiz, id=quiz_id)
    
    # Check for existing incomplete attempt
    existing_attempt = QuizAttempt.objects.filter(
        quiz=quiz,
        user=request.user.profile,
        completed_at__isnull=True
    ).first()
    
    if existing_attempt:
        # Check if time limit exceeded
        time_elapsed = timezone.now() - existing_attempt.started_at
        if time_elapsed.total_seconds() > quiz.time_limit:
            existing_attempt.is_passed = False
            existing_attempt.completed_at = timezone.now()
            existing_attempt.save()
        else:
            # Return existing attempt with remaining time
            remaining_time = quiz.time_limit - int(time_elapsed.total_seconds())
            return Response({
                'attempt_id': existing_attempt.id,
                'remaining_time': remaining_time,
                'quiz': QuizDetailSerializer(quiz).data
            })
    
    # Create new attempt
    attempt = QuizAttempt.objects.create(
        quiz=quiz,
        user=request.user.profile
    )
    
    return Response({
        'attempt_id': attempt.id,
        'remaining_time': quiz.time_limit,
        'quiz': QuizDetailSerializer(quiz).data
    })

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def submit_quiz(request, quiz_id):
    """Submit quiz answers and calculate score"""
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
    answers = request.data.get('answers', {})  # Format: {question_id: answer_id}
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
    
    # Award points if passed
    if attempt.is_passed:
        profile = request.user.profile
        profile.points += quiz.points_reward
        profile.save()
    
    return Response({
        'score': percentage_score,
        'is_passed': attempt.is_passed,
        'points_earned': quiz.points_reward if attempt.is_passed else 0,
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
