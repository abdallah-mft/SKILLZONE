from django.shortcuts import render
from rest_framework.decorators import api_view
from django.http import JsonResponse
from .models import Course

@api_view(['GET'])
def courses_list(request):
    courses = Course.objects.all().values('id', 'title', 'description')
    return JsonResponse({"courses": list(courses)})

@api_view(['GET'])
def course_detail(request, course_id):
    try:
        course = Course.objects.get(id=course_id)
        # Use related_name "lessons" to get all lessons for this course
        lessons = course.lessons.all().values('id', 'title', 'video_url', 'points_required')
        data = {
            "id": course.id,
            "title": course.title,
            "description": course.description,
            "lessons": list(lessons)
        }
        return JsonResponse(data)
    except Course.DoesNotExist:
        return JsonResponse({"error": "Course not found"}, status=404)

