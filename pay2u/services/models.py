from django.db import models


class Category(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=20)

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"

    def __str__(self):
        return self.name


class Service(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=32, null=False, verbose_name="Название")
    image = models.ImageField(
        upload_to="services/images",
        null=False,
    )
    login = models.BooleanField(
        default=False, null=False, verbose_name="Логин"
    )
    availability = models.BooleanField(
        default=True, null=False, verbose_name="Доступен"
    )
    description = models.TextField(
        max_length=1000, null=False, verbose_name="Описание"
    )
    conditions = models.TextField(
        max_length=1000, null=False, verbose_name="Условия"
    )
    website = models.URLField(null=False, verbose_name="Сайт")
    instruction = models.TextField(
        max_length=1000, null=False, verbose_name="Инструкция"
    )
    rules = models.TextField(
        max_length=1000, null=False, verbose_name="Правила"
    )
    popularity = models.IntegerField(
        default=0, verbose_name="Популярность"
    )
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, verbose_name="Категория"
    )

    class Meta:
        verbose_name = "Сервис"
        verbose_name_plural = "Сервисы"

    def __str__(self):
        return self.name
