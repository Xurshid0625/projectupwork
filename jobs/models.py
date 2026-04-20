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
    
class Contract(models.Model):
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('completed', 'Completed'),
    )

    job = models.ForeignKey('Job', on_delete=models.CASCADE)
    freelancer = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='freelancer_contracts')
    client = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='client_contracts')

    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField(null=True, blank=True)

    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')

    def __str__(self):
        return f"{self.job} - {self.freelancer}"
    
class Conversation(models.Model):
    contract = models.OneToOneField('Contract', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Chat for {self.contract}"
    
class Message(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey('users.User', on_delete=models.CASCADE)
    text = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender}: {self.text[:20]}"
    
class Review(models.Model):
    contract = models.ForeignKey('Contract', on_delete=models.CASCADE)
    reviewer = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='given_reviews')
    reviewee = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='received_reviews')

    rating = models.IntegerField()  # 1-5
    comment = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.reviewer} -> {self.reviewee}"