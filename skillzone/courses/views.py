from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q
from .models import Course, Lesson, UnlockedLesson, UnlockedCourse
from .serializers import CourseSerializer

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def courses_list(request):
    """Enhanced course listing with filters"""
    try:
        search = request.GET.get('search', '')
        course_type = request.GET.get('type', '')
        category = request.GET.get('category', '')
        difficulty = request.GET.get('difficulty', '')
        tags = request.GET.get('tags', '').split(',')
        page = int(request.GET.get('page', 1))
        per_page = int(request.GET.get('per_page', 10))

        # Filter courses
        courses = Course.objects.all()
        
        if search:
            courses = courses.filter(
                Q(title__icontains=search) |
                Q(description__icontains=search)
            )
        
        if course_type:
            courses = courses.filter(course_type=course_type)
            
        if category:
            courses = courses.filter(category=category)
            
        if difficulty:
            courses = courses.filter(difficulty_level=difficulty)
            
        if tags and tags[0]:  # Check if tags list is not empty
            for tag in tags:
                courses = courses.filter(tags__icontains=tag.strip())

        # Pagination
        start = (page - 1) * per_page
        end = start + per_page
        total = courses.count()

        # Get categories and tags for filters
        all_categories = Course.objects.values_list('category', flat=True).distinct()
        all_tags = set()
        for tags_str in Course.objects.values_list('tags', flat=True):
            if tags_str:
                all_tags.update(tag.strip() for tag in tags_str.split(','))

        courses = courses[start:end]
        serializer = CourseSerializer(courses, many=True, context={'request': request})

        return Response({
            "success": True,
            "message": "Courses retrieved successfully",
            "data": {
                'courses': serializer.data,
                'total': total,
                'page': page,
                'total_pages': (total + per_page - 1) // per_page,
                'user_points': request.user.profile.points,
                'filters': {
                    'categories': list(all_categories),
                    'tags': list(all_tags),
                    'difficulties': ['BEGINNER', 'INTERMEDIATE', 'ADVANCED']
                }
            }
        })
    except Exception as e:
        return Response({
            "success": False,
            "message": str(e),
            "data": None
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def course_detail(request, course_id):
    try:
        course = get_object_or_404(Course, id=course_id)
        user_profile = request.user.profile
        
        serializer = CourseSerializer(course, context={'request': request})
        data = serializer.data
        data['user_points'] = user_profile.points
        
        return Response({
            "success": True,
            "message": "Course details retrieved successfully",
            "data": data
        })
    except Exception as e:
        return Response({
            "success": False,
            "message": str(e),
            "data": None
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def unlock_lesson(request, lesson_id):
    """Unlock a lesson by spending points"""
    try:
        lesson = get_object_or_404(Lesson, id=lesson_id)
        user_profile = request.user.profile
        
        # Check if already unlocked
        if UnlockedLesson.objects.filter(user=user_profile, lesson=lesson).exists():
            return Response({
                "success": False,
                "message": "Lesson already unlocked",
                "data": None
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if user has enough points
        if user_profile.points < lesson.points_required:
            return Response({
                "success": False,
                "message": f"Not enough points. Required: {lesson.points_required}, Available: {user_profile.points}",
                "data": None
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Deduct points and create unlock record
        user_profile.points -= lesson.points_required
        user_profile.save()
        
        UnlockedLesson.objects.create(user=user_profile, lesson=lesson)
        
        return Response({
            "success": True,
            "message": "Lesson unlocked successfully",
            "data": {
                "remaining_points": user_profile.points,
                "lesson_id": lesson.id,
                "points_spent": lesson.points_required
            }
        })
        
    except Exception as e:
        return Response({
            "success": False,
            "message": str(e),
            "data": None
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def unlock_course(request, course_id):
    """Unlock a HARD skill course by spending points"""
    try:
        course = get_object_or_404(Course, id=course_id)
        user_profile = request.user.profile

        # Check if it's a HARD skill course
        if course.course_type != 'HARD':
            return Response({
                "success": False,
                "message": "Only HARD skill courses need to be unlocked",
                "data": None
            }, status=status.HTTP_400_BAD_REQUEST)

        # Check if already unlocked
        if UnlockedCourse.objects.filter(user=user_profile, course=course).exists():
            return Response({
                "success": False,
                "message": "Course already unlocked",
                "data": None
            }, status=status.HTTP_400_BAD_REQUEST)

        # If points are required, check if user has enough
        if course.points_required > 0:
            if user_profile.points < course.points_required:
                return Response({
                    "success": False,
                    "message": f"Not enough points. Required: {course.points_required}, Available: {user_profile.points}",
                    "data": None
                }, status=status.HTTP_400_BAD_REQUEST)

            # Deduct points only if points are required
            user_profile.points -= course.points_required
            user_profile.save()

        UnlockedCourse.objects.create(
            user=user_profile,
            course=course,
            points_spent=course.points_required
        )

        return Response({
            "success": True,
            "message": "Course unlocked successfully",
            "data": {
                "remaining_points": user_profile.points,
                "course_id": course.id,
                "points_spent": course.points_required
            }
        })

    except Exception as e:
        return Response({
            "success": False,
            "message": str(e),
            "data": None
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mark_lesson_complete(request, lesson_id):
    """Mark a lesson as completed"""
    try:
        lesson = get_object_or_404(Lesson, id=lesson_id)
        user_profile = request.user.profile
        
        # Check if lesson is unlocked
        if not UnlockedLesson.objects.filter(user=user_profile, lesson=lesson).exists():
            return Response({
                "success": False,
                "message": "Lesson not unlocked",
                "data": None
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get or create course progress
        progress, _ = CourseProgress.objects.get_or_create(
            user=user_profile,
            course=lesson.course
        )
        
        # Mark lesson as completed
        progress.completed_lessons.add(lesson)
        progress.last_activity = timezone.now()
        progress.save()
        
        # Award points for completion
        if lesson.points_reward > 0:
            user_profile.points += lesson.points_reward
            user_profile.save()
        
        return Response({
            "success": True,
            "message": "Lesson marked as completed",
            "data": {
                "course_progress": progress.completion_percentage,
                "points_earned": lesson.points_reward,
                "total_points": user_profile.points
            }
        })
    except Exception as e:
        return Response({
            "success": False,
            "message": str(e),
            "data": None
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def course_statistics(request, course_id):
    """Get detailed course statistics"""
    try:
        course = get_object_or_404(Course, id=course_id)
        user_profile = request.user.profile
        
        # Get user's progress
        progress = CourseProgress.objects.filter(
            user=user_profile,
            course=course
        ).first()
        
        # Calculate time spent
        time_spent = 0
        if progress:
            completed_lessons = progress.completed_lessons.count()
            completed_quizzes = progress.completed_quizzes.count()
            time_spent = (completed_lessons * 15) + sum(
                quiz.time_limit for quiz in progress.completed_quizzes.all()
            )
        
        # Get overall course statistics
        total_students = CourseProgress.objects.filter(course=course).count()
        completion_rate = (
            CourseProgress.objects.filter(
                course=course,
                is_completed=True
            ).count() / total_students * 100
        ) if total_students > 0 else 0
        
        # Get average quiz scores
        quiz_scores = []
        for quiz in course.quizzes.all():
            attempts = QuizAttempt.objects.filter(
                quiz=quiz,
                completed_at__isnull=False
            )
            avg_score = attempts.aggregate(Avg('score'))['score__avg'] or 0
            quiz_scores.append({
                'quiz_title': quiz.title,
                'average_score': avg_score
            })
        
        return Response({
            "success": True,
            "message": "Statistics retrieved successfully",
            "data": {
                "user_stats": {
                    "completion_percentage": progress.completion_percentage if progress else 0,
                    "time_spent_minutes": time_spent,
                    "completed_lessons": completed_lessons if progress else 0,
                    "completed_quizzes": completed_quizzes if progress else 0,
                    "points_earned": sum(
                        lesson.points_reward for lesson in progress.completed_lessons.all()
                    ) if progress else 0
                },
                "course_stats": {
                    "total_students": total_students,
                    "completion_rate": completion_rate,
                    "quiz_scores": quiz_scores
                }
            }
        })
    except Exception as e:
        return Response({
            "success": False,
            "message": str(e),
            "data": None
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

