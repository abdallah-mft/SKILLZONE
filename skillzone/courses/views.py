from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Course
from .serializers import CourseSerializer

@api_view(['GET'])
def courses_list(request):
    courses = Course.objects.all()
    serializer = CourseSerializer(courses, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def course_detail(request, course_id):
    try:
        course = Course.objects.get(id=course_id)
        serializer = CourseSerializer(course)
        return Response(serializer.data)
    except Course.DoesNotExist:
        return Response({"error": "Course not found"}, status=status.HTTP_404_NOT_FOUND)

