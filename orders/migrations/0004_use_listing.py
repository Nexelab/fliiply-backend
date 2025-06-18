from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):

    dependencies = [
        ('products', '0001_initial'),
        ('orders', '0003_add_cartitem'),
    ]

    operations = [
        migrations.AddField(
            model_name='cartitem',
            name='listing',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='cart_items', to='products.listing'),
        ),
        migrations.AddField(
            model_name='order',
            name='listing',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='orders', to='products.listing'),
        ),
        migrations.RemoveField(
            model_name='cartitem',
            name='offer',
        ),
        migrations.RemoveField(
            model_name='order',
            name='offer',
        ),
        migrations.DeleteModel(
            name='Offer',
        ),
        migrations.AlterField(
            model_name='cartitem',
            name='listing',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='cart_items', to='products.listing'),
        ),
        migrations.AlterField(
            model_name='order',
            name='listing',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='orders', to='products.listing'),
        ),
    ]
