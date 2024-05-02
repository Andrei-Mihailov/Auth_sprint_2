# Generated by Django 4.1.7 on 2024-02-12 10:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('movies', '0004_rename_created_genrefilmwork_created_at_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='filmwork',
            name='persons',
            field=models.ManyToManyField(through='movies.PersonFilmwork', to='movies.person'),
        ),
        migrations.AlterUniqueTogether(
            name='genrefilmwork',
            unique_together={('film_work', 'genre')},
        ),
        migrations.AlterUniqueTogether(
            name='personfilmwork',
            unique_together={('film_work', 'person', 'role')},
        ),
    ]
