import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('clientapp', '0005_articles_contact_articles_is_payant_articles_prix'),
    ]

    operations = [
        migrations.AddField(
            model_name='personnel',
            name='user',
            field=models.OneToOneField(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='personnel',
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AlterField(
            model_name='personnel',
            name='fonction',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='personnel',
            name='photo',
            field=models.ImageField(blank=True, null=True, upload_to='personnel'),
        ),
    ]
