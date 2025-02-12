from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.CharField(default='Hola, Twitter', max_length=100)
    image = models.ImageField(default='default.png')

    def __str__(self):
        return f'Perfil de {self.user.username}'

    def following(self):
        return Profile.objects.filter(
            user__in=Relationship.objects.filter(
                from_user=self.user
            ).values_list('to_user', flat=True)
        ).order_by('user__username')  

    def followers(self):
        return Profile.objects.filter(
            user__in=Relationship.objects.filter(
                to_user=self.user
            ).values_list('from_user', flat=True)
        ).order_by('user__username') 

class Post(models.Model):
    timestamp = models.DateTimeField(default=timezone.now)
    content = models.CharField(max_length=280) 
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return self.content

class Relationship(models.Model):
    from_user = models.ForeignKey(User, related_name='relationships', on_delete=models.CASCADE)
    to_user = models.ForeignKey(User, related_name='related_to', on_delete=models.CASCADE)

    class Meta:
        unique_together = ('from_user', 'to_user')