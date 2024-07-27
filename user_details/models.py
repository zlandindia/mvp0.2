from django.db import models

class UserDetails(models.Model):
    name = models.CharField(max_length=100)
    age = models.IntegerField()
    gender = models.CharField(max_length=10)
    occupation = models.CharField(max_length=100)
    email_id = models.EmailField(blank=True, null=True)
    email_subject = models.CharField(max_length=255, blank=True, null=True)
    email_body = models.TextField(blank=True, null=True)
    feedback = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name
