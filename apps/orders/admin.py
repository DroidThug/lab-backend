from django.contrib import admin
from .models import LabOrder, LabTest, Privilege, TestStatus, LabComment

class TestStatusInline(admin.TabularInline):
    model = TestStatus
    extra = 0

class LabCommentInline(admin.TabularInline):
    model = LabComment
    extra = 0
    readonly_fields = ('created_at',)

@admin.register(LabOrder)
class LabOrderAdmin(admin.ModelAdmin):
    list_display = ('order_id', 'patient_name', 'ip_number', 'department', 'status', 'created_at')
    list_filter = ('status', 'department', 'created_at')
    search_fields = ('order_id', 'patient_name', 'ip_number')
    date_hierarchy = 'created_at'
    inlines = [TestStatusInline, LabCommentInline]

@admin.register(LabTest)
class LabTestAdmin(admin.ModelAdmin):
    list_display = ('name', 'privilege', 'section')
    list_filter = ('privilege', 'section')
    search_fields = ('name',)

@admin.register(TestStatus)
class TestStatusAdmin(admin.ModelAdmin):
    list_display = ('order', 'test', 'status', 'updated_at')
    list_filter = ('status', 'updated_at')
    search_fields = ('order__order_id', 'test__name')

@admin.register(LabComment)
class LabCommentAdmin(admin.ModelAdmin):
    list_display = ('order', 'username', 'role', 'comment', 'created_at')
    list_filter = ('role', 'created_at')
    search_fields = ('order__order_id', 'username', 'comment')
    readonly_fields = ('created_at',)

admin.site.register(Privilege)