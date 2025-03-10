# Generated by Django 5.1.6 on 2025-03-06 17:56

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('first_version', '0006_alter_comments_name_alter_comments_post_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comments',
            name='name',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='first_version.user_profile'),
        ),
        migrations.AlterField(
            model_name='comments',
            name='post_name',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='first_version.posts'),
        ),
    ]
