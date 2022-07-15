from django.db import models

class Stock(models.Model):
    Stock_code = models.CharField(max_length=100)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('Stock_code',)

class Trading_info(models.Model):
    open_price = models.CharField(max_length=100)
    volumn = models.ManyToManyField(volumn)
    year = models.IntegerField()

    def __str__(self):
        return self.title

    class Meta:
        ordering = ('title',)