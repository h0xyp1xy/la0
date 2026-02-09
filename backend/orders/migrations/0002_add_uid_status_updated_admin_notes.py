# Generated manually

import uuid

from django.db import migrations, models


def fill_uid(apps, schema_editor):
    ContactSubmission = apps.get_model("orders", "ContactSubmission")
    for row in ContactSubmission.objects.all():
        if row.uid is None:
            row.uid = uuid.uuid4()
            row.save(update_fields=["uid"])


class Migration(migrations.Migration):

    dependencies = [
        ("orders", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="contactsubmission",
            name="uid",
            field=models.UUIDField(
                db_index=True,
                default=uuid.uuid4,
                editable=False,
                null=True,
                unique=True,
                verbose_name="Уникальный ID",
            ),
        ),
        migrations.AddField(
            model_name="contactsubmission",
            name="status",
            field=models.CharField(
                choices=[
                    ("new", "Новая"),
                    ("in_progress", "В работе"),
                    ("done", "Обработана"),
                    ("cancelled", "Отменена"),
                ],
                db_index=True,
                default="new",
                max_length=20,
                verbose_name="Статус",
            ),
        ),
        migrations.AddField(
            model_name="contactsubmission",
            name="admin_notes",
            field=models.TextField(blank=True, verbose_name="Заметки (админ)"),
        ),
        migrations.AddField(
            model_name="contactsubmission",
            name="updated_at",
            field=models.DateTimeField(auto_now=True, verbose_name="Обновлено"),
        ),
        migrations.AlterField(
            model_name="contactsubmission",
            name="created_at",
            field=models.DateTimeField(
                auto_now_add=True,
                db_index=True,
                verbose_name="Создано",
            ),
        ),
        migrations.RunPython(fill_uid, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="contactsubmission",
            name="uid",
            field=models.UUIDField(
                db_index=True,
                default=uuid.uuid4,
                editable=False,
                unique=True,
                verbose_name="Уникальный ID",
            ),
        ),
    ]
