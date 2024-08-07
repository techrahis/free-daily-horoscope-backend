# models.py
from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator

class HoroscopeType(models.Model):
    TYPE_CHOICES = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('yearly', 'Yearly'),
    ]
    name = models.CharField(max_length=20, choices=TYPE_CHOICES, unique=True)

    def __str__(self):
        return self.name

class HoroscopeCategory(models.Model):
    CATEGORY_CHOICES = [
        ('sunshine', 'Sunshine'),
        ('love', 'Love'),
        ('career', 'Career'),
        ('money', 'Money'),
        ('health', 'Health'),
    ]
    name = models.CharField(max_length=20, choices=CATEGORY_CHOICES, unique=True)

    def __str__(self):
        return self.name

class HoroscopeSign(models.Model):
    SIGN_CHOICES = [
        ('aries', 'Aries'),
        ('taurus', 'Taurus'),
        ('gemini', 'Gemini'),
        ('cancer', 'Cancer'),
        ('leo', 'Leo'),
        ('virgo', 'Virgo'),
        ('libra', 'Libra'),
        ('scorpio', 'Scorpio'),
        ('sagittarius', 'Sagittarius'),
        ('capricorn', 'Capricorn'),
        ('aquarius', 'Aquarius'),
        ('pisces', 'Pisces'),
    ]
    name = models.CharField(max_length=20, choices=SIGN_CHOICES, unique=True)

    def __str__(self):
        return self.name

class Horoscope(models.Model):
    type = models.ForeignKey(HoroscopeType, on_delete=models.CASCADE)
    category = models.ForeignKey(HoroscopeCategory, on_delete=models.CASCADE)
    sign = models.ForeignKey(HoroscopeSign, on_delete=models.CASCADE)
    start_date = models.DateField(default=timezone.now, editable=False)
    end_date = models.DateField(default=timezone.now, editable=False)
    content = models.TextField()
    sex_rating = models.PositiveSmallIntegerField(
        default=1,
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    hustle_rating = models.PositiveSmallIntegerField(
        default=1,
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    vibe_rating = models.PositiveSmallIntegerField(
        default=1,
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    success_rating = models.PositiveSmallIntegerField(
        default=1,
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    mood_emoji = models.CharField(max_length=5, blank=True)  # Emoji representing the general mood

    # Matches for love, friendship, and career
    love_match = models.ForeignKey(HoroscopeSign, related_name='love_matches', on_delete=models.CASCADE, blank=True, null=True)
    friendship_match = models.ForeignKey(HoroscopeSign, related_name='friendship_matches', on_delete=models.CASCADE, blank=True, null=True)
    career_match = models.ForeignKey(HoroscopeSign, related_name='career_matches', on_delete=models.CASCADE, blank=True, null=True)

    # created_at = models.DateTimeField(auto_now_add=True, default=timezone.now, editable=False)
    # updated_at = models.DateTimeField(auto_now=True, default=timezone.now, editable=False)

    def save(self, *args, **kwargs):
        if self.type.name == 'daily':
            self.end_date = self.start_date
        elif self.type.name == 'weekly':
            self.end_date = self.start_date + timezone.timedelta(days=6)
        elif self.type.name == 'monthly':
            self.end_date = (self.start_date.replace(day=28) + timezone.timedelta(days=4)).replace(day=1) - timezone.timedelta(days=1)
        elif self.type.name == 'yearly':
            self.end_date = self.start_date.replace(month=12, day=31)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.type.name} - {self.category.name} - {self.sign.name} - {self.start_date} to {self.end_date}"