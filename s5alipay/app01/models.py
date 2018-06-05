from django.db import models

# Create your models here.
class Order(models.Model):
    num = models.CharField(max_length=32)
    price = models.FloatField()
    static_choices = (
        (1, '未支付'),
        (2, '支付成功')
    )
    status = models.IntegerField(choices=static_choices,default=1)