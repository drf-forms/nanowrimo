from django.conf import settings
from django.db import models


class Book(models.Model):
    title = models.CharField(max_length=500, null=True, blank=True)
    summary = models.TextField(null=True, blank=True)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                               related_name='authors')
    cover = models.ImageField(blank=True, null=True)

    def __str__(self):
        if self.title is not None and self.title != '':
            return self.title
        return 'Untitled book #{}'.format(self.id)

    class Meta:
        ordering = ('title', )


class Chapter(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='chapters')
    number = models.PositiveSmallIntegerField(default=0)
    title = models.CharField(max_length=500, null=True, blank=True)
    summary = models.TextField(null=True, blank=True)

    def __str__(self):
        if self.title is not None and self.title != '':
            return self.title
        return 'Chapter {}'.format(self.number)

    class Meta:
        ordering = ('number', )


class Place(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='places')
    name = models.CharField(max_length=500)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('name', )


class Prop(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='props')
    name = models.CharField(max_length=500)
    descritpion = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('name', )


class Character(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='characters')
    name = models.CharField(max_length=500)
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('name', )


class Scene(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='scenes')
    ordernum = models.PositiveSmallIntegerField(default=0)
    timestamp = models.DateTimeField(null=True)
    short_description = models.CharField(max_length=500, null=True, blank=True)
    summary = models.TextField(null=True, blank=True)
    long_description = models.TextField(null=True, blank=True)
    chapter = models.ForeignKey(Chapter, on_delete=models.SET_NULL, null=True, blank=True,
                                related_name='scenes')
    place = models.ForeignKey(Place, on_delete=models.SET_NULL, null=True, blank=True,
                              related_name='scenes')
    characters = models.ManyToManyField(Character, related_name='scenes', blank=True)
    image = models.ImageField(blank=True, null=True)

    def __str__(self):
        if self.short_description is not None and self.short_description != '':
            return '{} ({})'.format(self.short_description, self.timestamp)
        return 'scene at {} with {} ({})'.format(
            self.place.name,
            ', '.join([c.name for c in self.characters.all()]),
            self.timestamp
        )

    class Meta:
        ordering = ('short_description', )


class InventoryExchange(models.Model):
    scene = models.ForeignKey(Scene, on_delete=models.CASCADE, related_name='exchanges')
    from_char = models.ForeignKey(Character, on_delete=models.SET_NULL, null=True, blank=True,
                                  related_name='given_props')
    to_char = models.ForeignKey(Character, on_delete=models.SET_NULL, null=True, blank=True,
                                related_name='received_props')
    prop = models.ForeignKey(Prop, on_delete=models.CASCADE, related_name='exchanges')
    note = models.CharField(max_length=500, null=True, blank=True)

    def __str__(self):
        if self.note is not None and self.note != '':
            return self.note
        elif self.from_char is not None:
            if self.to_char is None:
                return '{} loses {}'.format(self.from_char.name, self.prop.name)
            return '{} receives {} from {}'.format(self.to_char.name, self.prop.name,
                                                   self.from_char.name)
        elif self.to_char is not None:
            return '{} receives {}'.format(self.to_char.name, self.prop.name)
        return self.prop.name
