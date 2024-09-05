from django.contrib import admin
from .models import NestUser, Note  # Combined import
from django.utils.html import format_html


# Admin for all NestUsers with filtering for superusers
@admin.register(NestUser)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'date_joined', 'is_superuser', 'is_staff')
    search_fields = ('username', 'email')
    list_filter = ('is_superuser', 'is_staff')

@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ('subject', 'branch', 'semester', 'uploaded_by', 'is_approved', 'upload_date', 'view_note')
    list_filter = ('is_approved', 'branch', 'semester')
    search_fields = ('subject', 'description')
    actions = ['approve_notes']

    def view_note(self, obj):
        if obj.file:  # Assuming the file field in the model is named 'document'
            return format_html('<a href="{}" target="_blank">View Note</a>', obj.file.url)
        return "No document uploaded"

    view_note.short_description = "View Note"

    def approve_notes(self, request, queryset):
        queryset.update(is_approved=True)
    approve_notes.short_description = "Approve selected notes"
