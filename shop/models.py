from django.db import models
from django.db.models.expressions import F
from django.db.models.fields.files import ImageField
from uuid import uuid4
from django.utils import timezone
from django.conf import settings
from django.db.models import Sum, Max, Min, Avg
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
# Create your models here.

# settings.AUTH_USER_MODEL is just a string, which can be used when you define a model, (e.g. ForeignKey accepts a string) but not when you need the actual class.

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
        '主要圖片', null=True, default=None, upload_to=path_and_rename, blank=True)
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

    class StatisChoices(models.TextChoices):
        ORDER_SENT = 'order_sent', '已下單'
        PAID = 'paid', '已付款'
        INVOICE_MADE = 'invoice_made', '以開立發票'
        PRODUCT_SENT = 'product_sent', '產品寄出'
        ORDER_CLOSED = 'order_closed', '訂單結束'
        ORDER_FAILED = 'order_failed', '訂單失敗'

    customer = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name='客戶')
    created_at = models.DateTimeField('建立於', auto_now_add=True)
    updated_at = models.DateTimeField('更新於', auto_now=True)
    total = models.DecimalField(
        '總金額', max_digits=6, decimal_places=2, default=0.00)
    status = models.CharField(
        '訂單狀態', max_length=63, choices=StatisChoices.choices, default=StatisChoices.ORDER_SENT)
    products = models.ManyToManyField(
        Product, verbose_name='訂單內容', related_name='orders', through='Mapping')

    def __str__(self):
        return f"{self.id}"

    class Meta:
        verbose_name = '訂單'
        verbose_name_plural = '訂單'


class Mapping(models.Model):
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, verbose_name='訂單')
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, verbose_name='產品')
    quantity = models.IntegerField(default=1)
    # subtotal = models.DecimalField(
    #    '小計', max_digits=6, decimal_places=2, default=0.00)

    @property
    def subtotal(self):
        return self.product.discounted_price * self.quantity

    def __str__(self):
        return f"訂單編號:{self.order.id}-{self.product.title}"

    class Meta:
        verbose_name = '訂單產品'
        verbose_name_plural = '訂單產品'


@receiver(post_save, sender=Mapping)
@receiver(post_delete, sender=Mapping)
def update_order_total(sender, *arg, **kwargs):
    instance = kwargs['instance']
    print(instance.order)
    order = instance.oreder
    output = Mapping.objects.filter(order=order).aggregate(
        sum=Sum(F('product__discounted_price')*F('quantity')))  # 計算Order 總價
    order.total = output['sum'] if output['sum'] is not None else 0.00
    order.save()
