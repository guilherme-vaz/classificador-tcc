from django.db import models

# Create your models here.
class Search(models.Model):
    search = models.CharField(max_length=500)

    def __str__(self):
        return self.search

class Tweet(models.Model):
    user = models.CharField(max_length = 64)
    tweet_id = models.CharField(max_length = 24)
    tweet_date = models.DateTimeField()
    tweet_text = models.CharField(max_length = 280)
    classification = models.CharField(max_length = 1)
    change = models.BooleanField(default = False)
    search = models.ForeignKey(Search, on_delete = models.CASCADE)
