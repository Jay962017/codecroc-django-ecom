from django.db import models
from django.db.models.fields.files import ImageField
from uuid import uuid4
from django.utils import timezone
from django.conf import settings
# Create your models here.

User = settings.AUTH_USER_MODEL


def path_and_rename(instance, filename):
    ext = filename.split('.')[:-1]
    now = timezone.now()
    return f"{now.year}/{now.month}/{now.day}/{uuid4().hex}.{ext}"


class Category(models.Model):
    title = models.CharField('標題', max_length=63)
    image = ImageField('圖片', null=True, default=None,
                       upload_to=path_and_rename)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = '產品類別'
        verbose_name_plural = '產品類別'


class Product(models.Model):
    title = models.CharField('標題', max_length=127)
    description = models.TextField(blank=True, null=True)
    primary_image = models.ImageField(
        '主要圖片', null=True, default=None, upload_to=path_and_rename)
    original_price = models.DecimalField('原價',
                                         max_digits=6, decimal_places=2, default=0.00)
    discounted_price = models.DecimalField('特價',
                                           max_digits=6, decimal_places=2, default=0.00)
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = '商品'
        verbose_name_plural = '商品'


class Order(models.Model):
    customer = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name='客戶')
    created_at = models.DateTimeField('建立於', auto_now_add=True)
    updated_at = models.DateTimeField('更新於', auto_now=True)
    total = models.DecimalField(
        '總金額', max_digits=6, decimal_places=2, default=0.00)
    status = models.CharField('訂單狀態', max_length=63, null=True, blank=True)

    def __str__(self):
        return self.customer

    class Meta:
        verbose_name = '客戶'
        verbose_name_plural = '客戶'
