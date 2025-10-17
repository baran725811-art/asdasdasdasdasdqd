from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('products', '0001_initial'),  # Son migration'a göre değiştir
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='focal_point_x',
            field=models.FloatField(default=50.0, help_text='Yatay odak noktası (0-100 arası yüzde)', verbose_name='Odak Noktası X'),
        ),
        migrations.AddField(
            model_name='product',
            name='focal_point_y',
            field=models.FloatField(default=50.0, help_text='Dikey odak noktası (0-100 arası yüzde)', verbose_name='Odak Noktası Y'),
        ),
    ]