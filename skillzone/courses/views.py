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
    """List all courses with search and pagination"""
    try:
        search = request.GET.get('search', '')
        course_type = request.GET.get('type', '')
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

        # Pagination
        start = (page - 1) * per_page
        end = start + per_page
        total = courses.count()

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
                'user_points': request.user.profile.points  # Add current user points
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
    """Get detailed course information"""
    try:
        course = get_object_or_404(Course, id=course_id)
        user_profile = request.user.profile
        
        # Check if course is unlocked (for HARD courses)
        is_unlocked = (
            course.course_type == 'SOFT' or
            UnlockedCourse.objects.filter(user=user_profile, course=course).exists()
        )
        
        serializer = CourseSerializer(course, context={'request': request})
        data = serializer.data
        data['user_points'] = user_profile.points
        data['can_access'] = is_unlocked
        data['needs_unlock'] = course.course_type == 'HARD' and not is_unlocked
        
        if not is_unlocked and course.course_type == 'HARD':
            data['lessons'] = []  # Hide lessons if course is not unlocked
        
        return Response({
            "success": True,
            "message": "Course details retrieved successfully",
            "data": data
        })
    except Course.DoesNotExist:
        return Response({
            "success": False,
            "message": "Course not found",
            "data": None
        }, status=status.HTTP_404_NOT_FOUND)

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

