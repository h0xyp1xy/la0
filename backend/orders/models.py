import uuid

from django.db import models


class ContactSubmission(models.Model):
    """Contact/order form submission stored in the database."""

    class Status(models.TextChoices):
        NEW = "new", "Новая"
        IN_PROGRESS = "in_progress", "В работе"
        DONE = "done", "Обработана"
        CANCELLED = "cancelled", "Отменена"

    uid = models.UUIDField(
        "Уникальный ID",
        unique=True,
        default=uuid.uuid4,
        editable=False,
        db_index=True,
    )
    firstname = models.CharField("Имя", max_length=100)
    lastname = models.CharField("Фамилия", max_length=100)
    phone = models.CharField("Телефон", max_length=20)
    email = models.EmailField("Email")
    telegram = models.CharField("Telegram", max_length=100, blank=True)
    region = models.CharField("Регион", max_length=200)
    city = models.CharField("Город", max_length=100)
    address = models.CharField("Адрес доставки", max_length=300)
    comment = models.TextField("Комментарий", blank=True)
    status = models.CharField(
        "Статус",
        max_length=20,
        choices=Status.choices,
        default=Status.NEW,
        db_index=True,
    )
    admin_notes = models.TextField("Заметки (админ)", blank=True)
    created_at = models.DateTimeField("Создано", auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField("Обновлено", auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "заявка"
        verbose_name_plural = "заявки"

    def __str__(self):
        return f"{self.lastname} {self.firstname} — {self.created_at:%d.%m.%Y %H:%M}"
