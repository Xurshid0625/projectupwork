from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Job(models.Model):
    JOB_TYPE = (
        ('fixed', 'Fixed'),
        ('hourly', 'Hourly'),
    )

    STATUS = (
        ('open', 'Open'),
        ('closed', 'Closed'),
    )

    EXPERIENCE = (
        ('junior', 'Junior'),
        ('mid', 'Mid'),
        ('senior', 'Senior'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField()
    budget = models.DecimalField(max_digits=10, decimal_places=2)
    job_type = models.CharField(max_length=10, choices=JOB_TYPE)
    experience_level = models.CharField(max_length=10, choices=EXPERIENCE)
    status = models.CharField(max_length=10, choices=STATUS, default='open')

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Proposal(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    )

    job = models.ForeignKey('Job', on_delete=models.CASCADE, related_name='proposals')
    freelancer = models.ForeignKey('users.User', on_delete=models.CASCADE)
    cover_letter = models.TextField()
    bid_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.freelancer} -> {self.job}"