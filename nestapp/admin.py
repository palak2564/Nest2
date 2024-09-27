from django.contrib import admin
from .models import NestUser, Note, Order, PrintPricing, PickupLocation, MyNotes
from django.utils.html import format_html
from .models import NestUser, Note  # Combined import
from django.urls import reverse
from django.utils.html import format_html
from .models import Badge

###
from .models import Comment


# Admin for NestUsers
@admin.register(NestUser)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'is_active','date_joined', 'is_superuser', 'is_staff')
    search_fields = ('username', 'email')
    list_filter = ('is_superuser', 'is_staff','is_active')

     # Adding actions to activate and deactivate users
    actions = ['activate_users', 'deactivate_users', 'delete_selected']

     # Custom action to activate selected users
    def activate_users(self, request, queryset):
        queryset.update(is_active=True)
        self.message_user(request, "Selected users have been activated.")
    activate_users.short_description = "Activate selected users"

    # Custom action to deactivate selected users
    def deactivate_users(self, request, queryset):
        queryset.update(is_active=False)
        self.message_user(request, "Selected users have been deactivated.")
    deactivate_users.short_description = "Deactivate selected users"

@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ('subject', 'branch', 'semester', 'uploaded_by', 'is_approved', 'upload_date', 'view_note')
    list_filter = ('is_approved', 'branch', 'semester')
    search_fields = ('subject', 'description')
    actions = ['approve_notes']

    def view_note(self, obj):
        if obj.file:
            return format_html('<a href="{}" target="_blank">View Note</a>', obj.file.url)
        return "No document uploaded"

    view_note.short_description = "View Note"

    def approve_notes(self, request, queryset):
        queryset.update(is_approved=True)
    approve_notes.short_description = "Approve selected notes"

@admin.register(MyNotes)
class MyNotesAdmin(admin.ModelAdmin):
    list_display = ('user', 'note', 'created_at')

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_id', 'user', 'status', 'price', 'created_at')
    list_filter = ('status', 'pickup_location')
    search_fields = ('user__username', 'order_id')

@admin.register(PrintPricing)
class PrintPricingAdmin(admin.ModelAdmin):
    list_display = ('black_and_white_price', 'color_price', 'fast_print_surcharge', 'delivery_surcharge', 'tax_rate')

@admin.register(PickupLocation)
class PickupLocationAdmin(admin.ModelAdmin):
    list_display = ('name', 'address', 'open_time', 'close_time')
#ADMIN CAN VIEW BADGE
@admin.register(Badge)
class BadgeAdmin(admin.ModelAdmin):
    list_display = ('user', 'badge_type', 'awarded_at')
    search_fields = ('user__username', 'badge_type')


###
@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('note', 'user', 'created_at', 'is_approved')
    search_fields = ('user__username', 'note__subject', 'content')
    list_filter = ('is_approved', 'created_at')
    actions = ['approve_comments', 'disapprove_comments']

    def approve_comments(self, request, queryset):
        queryset.update(is_approved=True)
        self.message_user(request, "Selected comments have been approved.")
    approve_comments.short_description = "Approve selected comments"

    def disapprove_comments(self, request, queryset):
        queryset.update(is_approved=False)
        self.message_user(request, "Selected comments have been disapproved.")
    disapprove_comments.short_description = "Disapprove selected comments"