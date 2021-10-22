# Generated by Django 3.2.8 on 2021-10-17 12:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[('order_sent', '已下單'), ('paid', '已付款'), ('invoice_made', '以開立發票'), ('product_sent', '產品寄出'), ('order_closed', '訂單結束'), ('order_failed', '訂單失敗')], default='order_sent', max_length=63, verbose_name='訂單狀態'),
        ),
    ]
