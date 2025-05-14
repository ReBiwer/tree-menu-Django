from django.db import models
from django.urls import reverse, NoReverseMatch

# Create your models here.

class Menu(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name='Название меню')

    def __str__(self):
        return self.name

class MenuItem(models.Model):
    menu = models.ForeignKey(Menu, related_name='items', on_delete=models.CASCADE, verbose_name='Меню')
    parent = models.ForeignKey('self', null=True, blank=True, related_name='children', on_delete=models.CASCADE, verbose_name='Родительский пункт')
    title = models.CharField(max_length=100, verbose_name='Название пункта')
    url = models.CharField(max_length=200, blank=True, verbose_name='URL (явный)')
    named_url = models.CharField(max_length=200, blank=True, verbose_name='Named URL (name из urls.py)')
    order = models.PositiveIntegerField(default=0, verbose_name='Порядок')

    class Meta:
        ordering = ['order', 'id']
        verbose_name = 'Пункт меню'
        verbose_name_plural = 'Пункты меню'

    def __str__(self):
        return self.title

    def get_url(self):
        if self.named_url:
            try:
                return reverse(self.named_url)
            except NoReverseMatch:
                return self.url or '#'
        return self.url or '#'
