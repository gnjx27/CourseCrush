from django.contrib import admin
from .models import *

# Register your models here.

# register CustomUser model
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'full_name', 'role', 'status', 'email', 'is_active')
    search_fields = ('username', 'email', 'full_name')
    list_filter = ('role', 'is_active')
    list_per_page = 25

admin.site.register(CustomUser, CustomUserAdmin)


# register Course model
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'teacher', 'created_at')
    search_fields = ('title', 'teacher__username')
    list_filter = ('teacher', 'created_at')
    list_per_page = 25

admin.site.register(Course, CourseAdmin)

# register Feedback model
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('course', 'student', 'created_at')
    search_fields = ('course__title', 'student__username')
    list_filter = ('created_at',)
    list_per_page = 25

admin.site.register(Feedback, FeedbackAdmin)

# register Enrolment model
class EnrolmentAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'created_at')
    search_fields = ('student__username', 'course__title')
    list_filter = ('created_at',)
    list_per_page = 25

admin.site.register(Enrolment, EnrolmentAdmin)

# register Blocked model
class BlockedAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'reason', 'created_at')
    search_fields = ('student__username', 'course__title', 'reason')
    list_filter = ('created_at',)
    list_per_page = 25

admin.site.register(Blocked, BlockedAdmin)

# register Notification model
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'message', 'created_at')
    search_fields = ('user__username', 'message')
    list_filter = ('created_at',)
    list_per_page = 25

admin.site.register(Notification, NotificationAdmin)

# register Material model
class MaterialAdmin(admin.ModelAdmin):
    list_display = ('file', 'description', 'course', 'teacher', 'created_at')
    search_fields = ('course__title', 'teacher__username', 'description')
    list_filter = ('created_at',)
    list_per_page = 25

admin.site.register(Material, MaterialAdmin)