from django.contrib import admin
from .models import Genre, Filmwork, GenreFilmwork, Person, PersonFilmwork


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')

    search_fields = ('name', 'description', 'id')


class GenreFilmworkInline(admin.TabularInline):
    model = GenreFilmwork


class PersonFilmworkInline(admin.TabularInline):
    model = PersonFilmwork
    autocomplete_fields = ('person',)
    extra = 0


@admin.register(Filmwork)
class FilmworkAdmin(admin.ModelAdmin):
    inlines = [GenreFilmworkInline, PersonFilmworkInline]
    list_display = ('title', 'type', 'creation_date', 'rating')

    list_filter = ('type', 'rating', 'creation_date')
    search_fields = ('title', 'description', 'id')


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    inlines = [PersonFilmworkInline,]
    list_display = ('full_name',)

    list_filter = ('full_name',)
    search_fields = ('full_name', 'id')
