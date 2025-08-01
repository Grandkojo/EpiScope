from django.contrib import admin
from .models import ChatSession, ChatMessage, ChatAnalytics, DiseaseQuery, FineTuningDataset

@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    list_display = ['session_id', 'start_time', 'end_time', 'status', 'total_messages']
    list_filter = ['status', 'start_time']
    search_fields = ['session_id', 'user_id']
    readonly_fields = ['id', 'created_at', 'updated_at']

@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ['role', 'content_preview', 'session', 'timestamp', 'message_type']
    list_filter = ['role', 'message_type', 'timestamp']
    search_fields = ['content', 'user_id']
    readonly_fields = ['id', 'created_at']

    def content_preview(self, obj):
        return obj.content[:50] + "..." if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Content'

@admin.register(ChatAnalytics)
class ChatAnalyticsAdmin(admin.ModelAdmin):
    list_display = ['session', 'total_questions', 'disease_related_questions', 'average_response_time']
    list_filter = ['created_at']
    readonly_fields = ['id', 'created_at', 'updated_at']

@admin.register(DiseaseQuery)
class DiseaseQueryAdmin(admin.ModelAdmin):
    list_display = ['disease_name', 'query_type', 'confidence_score', 'user_feedback', 'created_at']
    list_filter = ['disease_name', 'query_type', 'user_feedback', 'created_at']
    search_fields = ['query_text', 'response_text']
    readonly_fields = ['id', 'created_at']

@admin.register(FineTuningDataset)
class FineTuningDatasetAdmin(admin.ModelAdmin):
    list_display = ['disease_name', 'instruction_preview', 'source', 'quality_score', 'is_approved']
    list_filter = ['disease_name', 'source', 'is_approved', 'created_at']
    search_fields = ['instruction', 'input_text', 'output_text']
    readonly_fields = ['id', 'created_at', 'updated_at']
    actions = ['approve_selected', 'reject_selected', 'export_selected']

    def instruction_preview(self, obj):
        return obj.instruction[:50] + "..." if len(obj.instruction) > 50 else obj.instruction
    instruction_preview.short_description = 'Instruction'

    def approve_selected(self, request, queryset):
        updated = queryset.update(is_approved=True)
        self.message_user(request, f'{updated} training examples approved.')
    approve_selected.short_description = "Approve selected examples"

    def reject_selected(self, request, queryset):
        updated = queryset.update(is_approved=False)
        self.message_user(request, f'{updated} training examples rejected.')
    reject_selected.short_description = "Reject selected examples"

    def export_selected(self, request, queryset):
        # Export selected examples to JSON
        import json
        from django.http import HttpResponse
        
        data = []
        for item in queryset:
            data.append(item.to_training_format())
        
        response = HttpResponse(
            json.dumps(data, indent=2),
            content_type='application/json'
        )
        response['Content-Disposition'] = 'attachment; filename="fine_tuning_data.json"'
        return response
    export_selected.short_description = "Export selected examples" 