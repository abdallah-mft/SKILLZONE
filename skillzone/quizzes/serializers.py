from rest_framework import serializers
from .models import Quiz, Question, Answer, QuizAttempt

class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = ['id', 'text']  # Excluding is_correct to not reveal correct answer

class QuestionSerializer(serializers.ModelSerializer):
    answers = AnswerSerializer(many=True, read_only=True)
    
    class Meta:
        model = Question
        fields = ['id', 'text', 'points', 'answers']

class QuizListSerializer(serializers.ModelSerializer):
    question_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Quiz
        fields = ['id', 'title', 'description', 'time_limit', 'points_reward', 'question_count']
    
    def get_question_count(self, obj):
        return obj.questions.count()

class QuizDetailSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True)
    
    class Meta:
        model = Quiz
        fields = ['id', 'title', 'description', 'time_limit', 'points_reward', 'questions']

class QuizAttemptSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuizAttempt
        fields = ['id', 'score', 'started_at', 'completed_at', 'is_passed']