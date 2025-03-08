from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q
from .models import Course
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
        serializer = CourseSerializer(courses, many=True)

        return Response({
            "success": True,
            "message": "Courses retrieved successfully",
            "data": {
                'courses': serializer.data,
                'total': total,
                'page': page,
                'total_pages': (total + per_page - 1) // per_page
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
        course = Course.objects.get(id=course_id)
        serializer = CourseSerializer(course)
        
        # Get user's points for validation
        user_points = request.user.profile.points
        
        # Add lesson availability based on user points
        data = serializer.data
        for lesson in data['lessons']:
            lesson['is_available'] = user_points >= lesson['points_required']
        
        return Response(data)
    except Course.DoesNotExist:
        return Response({
            "error": "Course not found"
        }, status=status.HTTP_404_NOT_FOUND)

