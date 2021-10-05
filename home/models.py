from django.db import models
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver


User = get_user_model()

class App(models.Model):
    TYPE_WEB = 'Web'
    TYPE_MOBILE = 'Mobile'
    TYPE_CHOICES = [
        (TYPE_WEB, 'Web'),
        (TYPE_MOBILE, 'Mobile')
    ]

    FRAMEWORK_DJANGO = 'Django'
    FRAMEWORK_REACT_NATIVE = 'React Native'
    FRAMEWORK_CHOICES = [
        (FRAMEWORK_DJANGO, 'Django'),
        (FRAMEWORK_REACT_NATIVE, 'React Native')
    ]

    name = models.CharField(max_length=50)
    description = models.TextField(blank=True)
    type = models.CharField(choices=TYPE_CHOICES, max_length=20)
    framework = models.CharField(choices=FRAMEWORK_CHOICES, max_length=20)
    domain_name = models.CharField(max_length=50, blank=True)
    screenshot = models.URLField(blank=True)
    subscription = models.ForeignKey('Subscription', models.SET_NULL, blank=True, null=True, related_name='apps') # cache
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Plan(models.Model):
    name = models.CharField(max_length=20)
    description = models.TextField()
    price = models.DecimalField(decimal_places=2, max_digits=10, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Subscription(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True) # cache
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE)
    app = models.ForeignKey(App, on_delete=models.CASCADE, related_name='subscriptions')
    active = models.BooleanField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


@receiver(post_save, sender=Subscription)
def post_save_subscription(sender, instance, created, **kwargs):
    if instance and instance.id and ((instance.user != instance.app.user) or (instance.app.subscription != instance)):
        # populating cache fields
        instance.user = instance.app.user
        post_save.disconnect(post_save_subscription, sender=Subscription)
        instance.save()
        post_save.connect(post_save_subscription, sender=Subscription)
        instance.app.subscription = instance
        instance.app.save()
