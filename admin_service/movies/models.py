import uuid
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _


class TimeStampedMixin(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class UUIDMixin(models.Model):
    id = models.UUIDField(primary_key=True,
                          default=uuid.uuid4,
                          editable=False)

    class Meta:
        abstract = True


class Genre(UUIDMixin, TimeStampedMixin):
    name = models.CharField(_('name'),
                            max_length=255)
    description = models.TextField(_('description'),
                                   blank=True,
                                   null=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "content\".\"genre"
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'


class Filmwork(UUIDMixin, TimeStampedMixin):
    class Genres(models.TextChoices):
        MOVIE = "movie"
        TV_SHOW = "tv_show"

    title = models.CharField(_('title'),
                             max_length=255)
    description = models.TextField(_('description'),
                                   blank=True,
                                   null=True)
    creation_date = models.DateField(blank=True,
                                     null=True)
    rating = models.FloatField(_('rating'),
                               blank=True,
                               null=True,
                               validators=[MinValueValidator(0),
                                           MaxValueValidator(100)])
    type = models.CharField(
        max_length=7,
        choices=Genres.choices,
        default=Genres.MOVIE,
    )

    genres = models.ManyToManyField(Genre,
                                    through='GenreFilmwork')
    persons = models.ManyToManyField('Person',
                                     through='PersonFilmwork')
    file_path = models.FileField(_('file'),
                                 blank=True,
                                 null=True,
                                 upload_to='movies/')

    def __str__(self):
        return self.title

    class Meta:
        db_table = "content\".\"film_work"
        verbose_name = 'Кинопроизведение'
        verbose_name_plural = 'Кинопроизведения'


class GenreFilmwork(UUIDMixin):
    film_work = models.ForeignKey(Filmwork,
                                  on_delete=models.CASCADE)
    genre = models.ForeignKey(Genre,
                              on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "content\".\"genre_film_work"
        unique_together = ('film_work', 'genre')


class Person(UUIDMixin, TimeStampedMixin):
    full_name = models.CharField(_('full_name'),
                                 max_length=255)

    def __str__(self):
        return self.full_name

    class Meta:
        db_table = "content\".\"person"
        verbose_name = 'Персона'
        verbose_name_plural = 'Персоны'


class PersonFilmwork(UUIDMixin):
    film_work = models.ForeignKey(Filmwork,
                                  on_delete=models.CASCADE)
    person = models.ForeignKey(Person,
                               on_delete=models.CASCADE)
    role = models.CharField(_('role'),
                            max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "content\".\"person_film_work"
        unique_together = ('film_work', 'person', 'role')
