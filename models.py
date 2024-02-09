from django.db import models

class News(models.Model):
    id = models.IntegerField
    text = models.TextField()
    date = models.DateField
    coord_x = models.FloatField
    coord_y = models.FloatField
    url = models.TextField
    img = models.TextField
