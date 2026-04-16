from django.contrib import admin
from django.urls import path
from django.utils.html import format_html
from .models import Lecturer, Exam, Room, Allocation, Absence
from .views import auto_allocate


# ✅ Lecturer
admin.site.register(Lecturer)


# ✅ Room (already sorted via model Meta)
admin.site.register(Room)


# ✅ Absence
admin.site.register(Absence)


# 🔥 FIXED Allocation Admin (NO sorted(), ONLY ordering)
@admin.register(Allocation)
class AllocationAdmin(admin.ModelAdmin):
    list_display = ['room', 'exam', 'lecturer']
    ordering = ['exam__date', 'exam__session', 'room__room_number']


# 🔥 FIXED Exam Admin (DATE + SESSION ORDER + BUTTON)
@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ['date', 'session', 'allocate_button']
    ordering = ['date', 'session']  # ✅ THIS FIXES YOUR ORDER ISSUE

    def allocate_button(self, obj):
        return format_html(
            '<a class="button" href="{}">Allocate</a>',
            f"/admin/core/exam/{obj.id}/allocate/"
        )

    allocate_button.short_description = "Auto Allocate"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                '<int:exam_id>/allocate/',
                self.admin_site.admin_view(self.allocate_view),
                name='admin-allocate'
            ),
        ]
        return custom_urls + urls

    def allocate_view(self, request, exam_id):
        return auto_allocate(request, exam_id)