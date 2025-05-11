from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Avg, Q
from django.db import transaction
from django.conf import settings
import logging
# Update imports to use only what's available
from .models import Course, Lesson, UnlockedCourse, UnlockedLesson, UserCourseProgress
from .serializers import CourseSerializer, LessonSerializer, UserCourseProgressSerializer
from quizzes.models import QuizAttempt
from users.models import Profile
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.core.validators import ValidationError

logger = logging.getLogger(__name__)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def courses_list(request):
    """Get all courses with filters"""
    try:
        # Get query parameters
        category = request.GET.get('category')
        difficulty = request.GET.get('difficulty')
        search = request.GET.get('search')
        course_type = request.GET.get('type')
        
        # Safely convert page and per_page to integers with defaults
        try:
            page = int(request.GET.get('page', 1))
        except (ValueError, TypeError):
            page = 1
            
        try:
            per_page = int(request.GET.get('per_page', 10))
        except (ValueError, TypeError):
            per_page = 10

        # Base queryset
        courses = Course.objects.all()

        # Apply filters
        if category:
            courses = courses.filter(category=category)
        if difficulty:
            courses = courses.filter(difficulty_level=difficulty)
        if course_type:
            courses = courses.filter(course_type=course_type)
        if search:
            courses = courses.filter(
                Q(title__icontains=search) |
                Q(description__icontains=search)
            )
            
        # Make sure all_categories and all_tags are defined
        all_categories = Course.objects.values_list('category', flat=True).distinct()
        all_tags = set()
        for tags_str in Course.objects.values_list('tags', flat=True).distinct():
            if tags_str:
                all_tags.update([tag.strip() for tag in tags_str.split(',')])

        # Calculate pagination
        total = courses.count()
        start = (page - 1) * per_page
        end = start + per_page
        courses = courses[start:end]

        serializer = CourseSerializer(courses, many=True, context={'request': request})
        
        # Safely get user points
        user_points = 0
        try:
            if hasattr(request.user, 'profile'):
                user_points = request.user.profile.points
        except Exception:
            pass

        return Response({
            "success": True,
            "message": "Courses retrieved successfully",
            "data": {
                'courses': serializer.data,
                'pagination': {
                    'total': total,
                    'page': page,
                    'per_page': per_page,
                    'total_pages': (total + per_page - 1) // per_page
                },
                'user_points': user_points,
                'filters': {
                    'categories': list(all_categories),
                    'tags': list(all_tags),
                    'difficulties': ['BEGINNER', 'INTERMEDIATE', 'ADVANCED'],
                    'types': ['SOFT', 'HARD']
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
    """Unlock a premium course"""
    try:
        course = get_object_or_404(Course, id=course_id)
        user_profile = request.user.profile
        
        # Check if course is already unlocked
        already_unlocked = UnlockedCourse.objects.filter(
            user=user_profile,
            course=course
        ).exists()
        
        if already_unlocked:
            return Response({
                "success": False,
                "message": "Course already unlocked",
                "data": None
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get points required (default to 0 if not set)
        points_required = getattr(course, 'points_required', 0)
        if points_required == 0 and course.course_type == 'HARD':
            # Default value for HARD courses if not set
            points_required = 1000
        
        # Check if user has enough points
        if user_profile.points < points_required:
            return Response({
                "success": False,
                "message": f"Not enough points. Required: {points_required}, Available: {user_profile.points}",
                "data": None
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Deduct points and unlock course
        with transaction.atomic():
            # Deduct points
            user_profile.points -= points_required
            user_profile.save()
            
            # Create unlock record
            UnlockedCourse.objects.create(
                user=user_profile,
                course=course,
                unlocked_at=timezone.now()
            )
            
            # Create progress record
            UserCourseProgress.objects.create(
                user=user_profile,
                course=course
            )
        
        return Response({
            "success": True,
            "message": "Course unlocked successfully",
            "data": {
                "course_id": course.id,
                "points_remaining": user_profile.points
            }
        })
        
    except Exception as e:
        import traceback
        logger.error(f"Error unlocking course {course_id}: {str(e)}")
        logger.error(traceback.format_exc())
        return Response({
            "success": False,
            "message": str(e),
            "data": None,
            "error_details": traceback.format_exc() if settings.DEBUG else None
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mark_lesson_complete(request, lesson_id):
    """Mark a lesson as completed"""
    try:
        lesson = get_object_or_404(Lesson, id=lesson_id)
        user_profile = request.user.profile
        
        # First check if the course is unlocked (for HARD courses)
        course = lesson.course
        if course.course_type == 'HARD':
            course_unlocked = UnlockedCourse.objects.filter(
                user=user_profile,
                course=course
            ).exists()
            
            if not course_unlocked:
                return Response({
                    "success": False,
                    "message": "Course not unlocked",
                    "data": None
                }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get or create the unlocked lesson record
        unlocked_lesson, created = UnlockedLesson.objects.get_or_create(
            user=user_profile,
            lesson=lesson
        )
        
        # Mark as completed
        if not unlocked_lesson.completed_at:
            unlocked_lesson.completed_at = timezone.now()
            unlocked_lesson.save()
        
        return Response({
            "success": True,
            "message": "Lesson marked as completed",
            "data": {
                "lesson_id": lesson.id,
                "course_id": lesson.course.id,
                "completed_at": unlocked_lesson.completed_at
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

from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from rest_framework import viewsets, permissions
from rest_framework.decorators import api_view, permission_classes
from .models import Course, Lesson, UserCourseProgress
from .serializers import CourseSerializer, LessonSerializer, UserCourseProgressSerializer

# API ViewSets
class CourseViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = Course.objects.all()
        course_type = self.request.query_params.get('type')
        if course_type:
            queryset = queryset.filter(course_type=course_type.upper())
        return queryset

class LessonViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = Lesson.objects.all()
        course_id = self.request.query_params.get('course_id')
        if course_id:
            queryset = queryset.filter(course_id=course_id)
        return queryset

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_user_progress(request):
    progress = UserCourseProgress.objects.filter(user=request.user)
    serializer = UserCourseProgressSerializer(progress, many=True)
    return JsonResponse(serializer.data, safe=False)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def mark_lesson_complete(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)
    course = lesson.course
    
    # Get or create progress record
    progress, created = UserCourseProgress.objects.get_or_create(
        user=request.user,
        course=course
    )
    
    # Add lesson to completed lessons
    progress.completed_lessons.add(lesson)
    
    # Check if all lessons are completed
    total_lessons = course.lessons.count()
    completed_lessons = progress.completed_lessons.count()
    
    if total_lessons == completed_lessons:
        progress.is_completed = True
        progress.save()
    
    return JsonResponse({
        'success': True,
        'progress': progress.progress_percentage
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_course_inventory(request):
    """Get all courses (SOFT and HARD) unlocked by the current user"""
    try:
        user_profile = request.user.profile
        
        # Get all unlocked courses for this user
        unlocked_courses = UnlockedCourse.objects.filter(
            user=user_profile
        ).select_related('course')
        
        # Get the course objects
        courses = [uc.course for uc in unlocked_courses]
        
        # Serialize the courses
        serializer = CourseSerializer(courses, many=True, context={'request': request})
        
        # Add unlocked_at date to each course
        courses_data = serializer.data
        unlocked_dates = {uc.course.id: uc.unlocked_at for uc in unlocked_courses}
        
        for course_data in courses_data:
            course_id = course_data['id']
            if course_id in unlocked_dates:
                course_data['unlocked_at'] = unlocked_dates[course_id]
        
        # Group courses by type
        soft_courses = [c for c in courses_data if c.get('course_type') == 'SOFT']
        hard_courses = [c for c in courses_data if c.get('course_type') == 'HARD']
        
        return Response({
            "success": True,
            "message": "Course inventory retrieved successfully",
            "data": {
                "courses": courses_data,
                "soft_courses": soft_courses,
                "hard_courses": hard_courses,
                "total_count": len(courses_data),
                "soft_count": len(soft_courses),
                "hard_count": len(hard_courses),
                "user_points": user_profile.points
            }
        })
        
    except Exception as e:
        import traceback
        logger.error(f"Error retrieving course inventory: {str(e)}")
        logger.error(traceback.format_exc())
        return Response({
            "success": False,
            "message": str(e),
            "data": None,
            "error_details": traceback.format_exc() if settings.DEBUG else None
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser, JSONParser])
def upload_course(request):
    """Upload a new course to the system"""
    try:
        # Debug information
        import logging
        logger = logging.getLogger(__name__)
        
        logger.info(f"User: {request.user.username}")
        logger.info(f"Is staff: {request.user.is_staff}")
        logger.info(f"Is superuser: {request.user.is_superuser}")
        logger.info(f"Has profile: {hasattr(request.user, 'profile')}")
        
        if hasattr(request.user, 'profile'):
            logger.info(f"Profile: {request.user.profile}")
            logger.info(f"Profile fields: {vars(request.user.profile)}")
            logger.info(f"Is teacher: {getattr(request.user.profile, 'is_teacher', False)}")
        
        # Check if user has admin privileges or is a teacher
        is_admin = request.user.is_staff or request.user.is_superuser
        is_teacher = hasattr(request.user, 'profile') and getattr(request.user.profile, 'is_teacher', False)
        
        logger.info(f"Is admin: {is_admin}")
        logger.info(f"Is teacher: {is_teacher}")
        
        if not (is_admin or is_teacher):
            logger.info("Permission denied: User is neither admin nor teacher")
            return Response({
                "success": False,
                "message": "You don't have permission to upload courses",
                "data": None
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Get data from request
        data = request.data
        
        # Validate required fields
        required_fields = ['title', 'description', 'course_type', 'difficulty_level']
        for field in required_fields:
            if field not in data:
                return Response({
                    "success": False,
                    "message": f"Missing required field: {field}",
                    "data": None
                }, status=status.HTTP_400_BAD_REQUEST)
        
        # Validate course type
        course_type = data.get('course_type').upper()
        if course_type not in [choice[0] for choice in Course.COURSE_TYPES]:
            return Response({
                "success": False,
                "message": f"Invalid course type. Must be one of: {', '.join([choice[0] for choice in Course.COURSE_TYPES])}",
                "data": None
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Validate difficulty level
        difficulty_level = data.get('difficulty_level').upper()
        if difficulty_level not in [choice[0] for choice in Course.DIFFICULTY_LEVELS]:
            return Response({
                "success": False,
                "message": f"Invalid difficulty level. Must be one of: {', '.join([choice[0] for choice in Course.DIFFICULTY_LEVELS])}",
                "data": None
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # For HARD courses, points_required is mandatory
        if course_type == 'HARD' and (not data.get('points_required') or int(data.get('points_required', 0)) <= 0):
            return Response({
                "success": False,
                "message": "HARD courses must have points_required greater than 0",
                "data": None
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Create the course
        course = Course(
            title=data.get('title'),
            description=data.get('description'),
            course_type=course_type,
            difficulty_level=difficulty_level,
            points_required=int(data.get('points_required', 0)),
            points_reward=int(data.get('points_reward', 0)),
            duration=int(data.get('duration', 0)),
            price=float(data.get('price', 0.0)) if course_type == 'HARD' else 0.0,
            category=data.get('category', 'General'),
            tags=data.get('tags', '')
        )
        
        # Handle image upload if provided
        if 'image' in request.FILES:
            course.image = request.FILES['image']
        
        # Save the course
        course.save()
        
        # Handle lessons if provided
        lessons_data = data.get('lessons', [])
        if isinstance(lessons_data, str):
            try:
                import json
                lessons_data = json.loads(lessons_data)
            except json.JSONDecodeError:
                lessons_data = []
        
        for i, lesson_data in enumerate(lessons_data):
            lesson = Lesson(
                course=course,
                title=lesson_data.get('title', f'Lesson {i+1}'),
                number=i+1,
                duration=int(lesson_data.get('duration', 0)),
                video_url=lesson_data.get('video_url', '')
            )
            lesson.save()
        
        # Return the created course
        serializer = CourseSerializer(course, context={'request': request})
        return Response({
            "success": True,
            "message": "Course uploaded successfully",
            "data": serializer.data
        }, status=status.HTTP_201_CREATED)
        
    except ValidationError as e:
        return Response({
            "success": False,
            "message": str(e),
            "data": None
        }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        import traceback
        logger.error(f"Error uploading course: {str(e)}")
        logger.error(traceback.format_exc())
        return Response({
            "success": False,
            "message": "An error occurred while uploading the course",
            "data": None,
            "error_details": str(e) if settings.DEBUG else None
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def course_lessons(request, course_id):
    """Get all lessons for a specific course"""
    try:
        course = get_object_or_404(Course, id=course_id)
        lessons = Lesson.objects.filter(course=course).order_by('number')
        
        # Serialize the lessons
        serializer = LessonSerializer(lessons, many=True)
        
        # Get user profile to check unlocked lessons
        user_profile = request.user.profile
        
        # Add unlocked status to each lesson
        lessons_data = serializer.data
        for lesson_data in lessons_data:
            lesson_id = lesson_data['id']
            is_unlocked = UnlockedLesson.objects.filter(
                user=user_profile,
                lesson_id=lesson_id
            ).exists()
            lesson_data['is_unlocked'] = is_unlocked
        
        return Response({
            "success": True,
            "message": "Course lessons retrieved successfully",
            "data": {
                "course_id": course.id,
                "course_title": course.title,
                "lessons_count": lessons.count(),
                "lessons": lessons_data
            }
        })
    except Exception as e:
        return Response({
            "success": False,
            "message": str(e),
            "data": None
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

