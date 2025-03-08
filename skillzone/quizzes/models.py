from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from courses.models import Course, Lesson
from users.models import Profile

class Quiz(models.Model):
    DIFFICULTY_LEVELS = (
        ('EASY', 'Easy'),
        ('MEDIUM', 'Medium'),
        ('HARD', 'Hard'),
    )
    
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='quizzes')
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='quizzes', null=True, blank=True)
    title = models.CharField(max_length=255)
    description = models.TextField()
    difficulty = models.CharField(max_length=6, choices=DIFFICULTY_LEVELS, default='MEDIUM')
    category = models.CharField(max_length=50, blank=True)
    time_limit = models.IntegerField(help_text="Time limit in seconds")
    points_reward = models.IntegerField(default=10)
    passing_score = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Minimum percentage to pass"
    )
    is_randomized = models.BooleanField(default=False, help_text="Randomize question order")
    max_attempts = models.IntegerField(default=0, help_text="0 for unlimited attempts")

    def get_statistics(self):
        attempts = self.quizattempt_set.all()
        total_attempts = attempts.count()
        if total_attempts == 0:
            return {
                'total_attempts': 0,
                'pass_rate': 0,
                'average_score': 0,
                'average_time': 0
            }

        passed_attempts = attempts.filter(is_passed=True).count()
        total_score = sum(attempt.score for attempt in attempts)
        
        completed_attempts = attempts.exclude(completed_at=None)
        if completed_attempts:
            total_time = sum(
                (attempt.completed_at - attempt.started_at).total_seconds()
                for attempt in completed_attempts
            )
            avg_time = total_time / completed_attempts.count()
        else:
            avg_time = 0

        return {
            'total_attempts': total_attempts,
            'pass_rate': (passed_attempts / total_attempts) * 100,
            'average_score': total_score / total_attempts,
            'average_time': avg_time
        }

class Question(models.Model):
    QUESTION_TYPES = (
        ('MCQ', 'Multiple Choice'),
        ('TF', 'True/False'),
        ('SHORT', 'Short Answer'),
        ('MATCH', 'Matching'),
    )
    
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField()
    points = models.IntegerField(default=1)
    question_type = models.CharField(max_length=5, choices=QUESTION_TYPES, default='MCQ')
    explanation = models.TextField(blank=True, help_text="Explanation shown after answering")

class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)

class QuizAttempt(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    user = models.ForeignKey(Profile, on_delete=models.CASCADE)
    score = models.IntegerField(default=0)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    is_passed = models.BooleanField(default=False)

class QuizProgress(models.Model):
    user = models.ForeignKey('users.Profile', on_delete=models.CASCADE)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    best_score = models.IntegerField(default=0)
    attempts_count = models.IntegerField(default=0)
    total_time_spent = models.IntegerField(default=0, help_text="Total time spent in seconds")
    last_attempt_date = models.DateTimeField(null=True)
    completed = models.BooleanField(default=False)
    
    class Meta:
        unique_together = ['user', 'quiz']

class QuizAchievement(models.Model):
    ACHIEVEMENT_TYPES = (
        ('PERFECT', 'Perfect Score'),
        ('FAST', 'Speed Demon'),
        ('STREAK', 'Winning Streak'),
        ('MASTER', 'Quiz Master'),
    )
    
    user = models.ForeignKey('users.Profile', on_delete=models.CASCADE)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    achievement_type = models.CharField(max_length=10, choices=ACHIEVEMENT_TYPES)
    earned_at = models.DateTimeField(auto_now_add=True)
    bonus_points = models.IntegerField(default=0)
