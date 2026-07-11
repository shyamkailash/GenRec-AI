from django.contrib import admin

from .models import Experiment


@admin.register(Experiment)
class ExperimentAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "subject",
        "title",
        "status",
        "created_at",
    ]

    list_filter = [
        "status",
        "subject",
    ]

    search_fields = [
        "subject",
        "title",
    ]
