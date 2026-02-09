from django.contrib import admin
from .models import ContactSubmission


@admin.register(ContactSubmission)
class ContactSubmissionAdmin(admin.ModelAdmin):
    list_display = ("uid", "lastname", "firstname", "email", "phone", "city", "status", "created_at", "updated_at")
    list_filter = ("status", "region", "created_at")
    search_fields = ("uid", "firstname", "lastname", "email", "phone", "city")
    readonly_fields = ("uid", "created_at", "updated_at")
    list_editable = ("status",)
    fieldsets = (
        (None, {"fields": ("uid", "status", "admin_notes", "created_at", "updated_at")}),
        ("Клиент", {"fields": ("firstname", "lastname", "phone", "email", "telegram")}),
        ("Доставка", {"fields": ("region", "city", "address", "comment")}),
    )
