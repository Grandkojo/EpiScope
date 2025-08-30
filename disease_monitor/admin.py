from django.contrib import admin
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django import forms
from django.contrib.auth.hashers import identify_hasher
from .models import (
    DiabetesData, MeningitisData, CholeraData, NationalHotspots, 
    Disease, DiseaseYear, RegionPopulation, Hospital,
    PredictionHistory, ReinforcementLearningData, ModelTrainingSession, PredictionFeedback,
    GoogleTrendsCache, GoogleTrendsMetrics, GoogleTrendsRequestLog,
    ArticleTag, Article, ResearchPaper, ArticleComment, ArticleLike, ArticleBookmark, ArticleView
)
from api.models import User

# Register your models here.

@admin.register(RegionPopulation)
class RegionPopulationAdmin(admin.ModelAdmin):
    list_display = ('region', 'periodname', 'population', 'formatted_population')
    list_filter = ('periodname', 'region')
    search_fields = ('region', 'periodname')
    ordering = ('-periodname', 'region')
    
    def formatted_population(self, obj):
        return f"{obj.population:,}"
    formatted_population.short_description = 'Population (Formatted)'
    
    def has_add_permission(self, request):
        return request.user.is_superuser or request.user.is_admin
    
    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser or request.user.is_admin
    
    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

@admin.register(DiabetesData)
class DiabetesDataAdmin(admin.ModelAdmin):
    list_display = ('periodname', 'diabetes_mellitus', 'diabetes_mellitus_deaths')
    list_filter = ('periodname',)
    search_fields = ('periodname',)
    readonly_fields = ('periodname', 'diabetes_mellitus', 'diabetes_mellitus_female', 
                      'diabetes_mellitus_male', 'diabetes_mellitus_deaths', 
                      'diabetes_mellitus_lab_confirmed_cases')
    
    def has_add_permission(self, request):
        return request.user.is_superuser
    
    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser
    
    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

@admin.register(MeningitisData)
class MeningitisDataAdmin(admin.ModelAdmin):
    list_display = ('periodname', 'meningitis_cases', 'meningococcal_meningitis_deaths')
    list_filter = ('periodname',)
    search_fields = ('periodname',)
    readonly_fields = ('periodname', 'meningitis_cases', 'meningitis_cases_female',
                      'meningitis_cases_male', 'meningitis_case_fatality_rate',
                      'meningococcal_meningitis_cases_weekly', 'meningococcal_meningitis_deaths_weekly',
                      'meningococcal_meningitis_lab_confirmed_cases', 'meningococcal_meningitis_lab_confirmed_cases_weekly',
                      'meningococcal_meningitis_cases_cds', 'meningococcal_meningitis_deaths')
    
    def has_add_permission(self, request):
        return request.user.is_superuser
    
    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser
    
    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

@admin.register(CholeraData)
class CholeraDataAdmin(admin.ModelAdmin):
    list_display = ('periodname', 'cholera_cases_cds', 'cholera_deaths_cds')
    list_filter = ('periodname',)
    search_fields = ('periodname',)
    readonly_fields = ('periodname', 'cholera_female', 'cholera_male', 'cholera_deaths_cds',
                      'cholera_cases_cds', 'cholera_cases_weekly', 'cholera_deaths_weekly',
                      'cholera_lab_confirmed', 'cholera_lab_confirmed_weekly', 'cholera_waho_cases')
    
    def has_add_permission(self, request):
        return request.user.is_superuser
    
    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser
    
    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

@admin.register(NationalHotspots)
class NationalHotspotsAdmin(admin.ModelAdmin):
    list_display = ('organisationunitname', 'cholera_lab_confirmed_cases_2024', 
                   'diabetes_mellitus_lab_confirmed_cases_2024', 
                   'meningococcal_meningitis_lab_confirmed_cases_2024')
    list_filter = ('organisationunitname',)
    search_fields = ('organisationunitname',)
    readonly_fields = ('organisationunitname', 'cholera_lab_confirmed_cases_2020',
                      'cholera_lab_confirmed_cases_2021', 'cholera_lab_confirmed_cases_2022',
                      'cholera_lab_confirmed_cases_2023', 'cholera_lab_confirmed_cases_2024',
                      'cholera_lab_confirmed_cases_2025', 'diabetes_mellitus_lab_confirmed_cases_2020',
                      'diabetes_mellitus_lab_confirmed_cases_2021', 'diabetes_mellitus_lab_confirmed_cases_2022',
                      'diabetes_mellitus_lab_confirmed_cases_2023', 'diabetes_mellitus_lab_confirmed_cases_2024',
                      'diabetes_mellitus_lab_confirmed_cases_2025', 'meningococcal_meningitis_lab_confirmed_cases_2020',
                      'meningococcal_meningitis_lab_confirmed_cases_2021', 'meningococcal_meningitis_lab_confirmed_cases_2022',
                      'meningococcal_meningitis_lab_confirmed_cases_2023', 'meningococcal_meningitis_lab_confirmed_cases_2024',
                      'meningococcal_meningitis_lab_confirmed_cases_2025')
    
    def has_add_permission(self, request):
        return request.user.is_superuser
    
    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser
    
    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

@admin.register(Disease)
class DiseaseAdmin(admin.ModelAdmin):
    list_display = ('disease_name', 'description')
    search_fields = ('disease_name', 'description')
    
    def has_add_permission(self, request):
        return request.user.is_superuser or request.user.is_admin
    
    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser or request.user.is_admin
    
    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

@admin.register(DiseaseYear)
class DiseaseYearAdmin(admin.ModelAdmin):
    list_display = ('periodname', 'disease_id', 'hot_spots', 'summary_data', 'case_count_summary')
    list_filter = ('periodname', 'disease_id', 'hot_spots', 'summary_data', 'case_count_summary')
    search_fields = ('periodname', 'disease_id__disease_name')
    
    def has_add_permission(self, request):
        return request.user.is_superuser or request.user.is_admin
    
    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser or request.user.is_admin
    
    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

class UserAdminForm(forms.ModelForm):
    # Use a password input and allow blank to keep existing
    password = forms.CharField(
        label='Password', required=False,
        widget=forms.PasswordInput(render_value=False)
    )

    class Meta:
        model = User
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Determine whether admin is checked from bound data or instance
        is_admin_checked = False
        if self.is_bound:
            is_admin_checked = bool(self.data.get('is_admin'))
        elif self.instance and getattr(self.instance, 'is_admin', False):
            is_admin_checked = True
        # Hospital required only when admin
        if 'hospital' in self.fields:
            self.fields['hospital'].required = is_admin_checked
        # Help text for password field on change
        if self.instance and self.instance.pk:
            self.fields['password'].help_text = "Leave blank to keep the current password."

    def clean(self):
        cleaned = super().clean()
        if cleaned.get('is_admin') and not cleaned.get('hospital'):
            self.add_error('hospital', "Hospital is required when 'Is admin' is checked.")
        return cleaned

    def clean_password(self):
        # Preserve existing hashed password if left blank on change
        pwd = self.cleaned_data.get('password')
        if self.instance and self.instance.pk and not pwd:
            return self.instance.password
        return pwd


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    form = UserAdminForm
    list_display = ('username', 'email', 'phone', 'hospital', 'is_admin', 'is_email_verified', 'is_phone_verified', 'is_staff', 'is_superuser')
    list_filter = ('is_admin', 'is_email_verified', 'is_phone_verified', 'is_staff', 'is_superuser', 'is_active')
    search_fields = ('username', 'email', 'phone')
    readonly_fields = ('date_joined', 'last_login')
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email', 'phone', 'address', 'hospital')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'is_admin',
                                   'is_email_verified', 'is_phone_verified', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    
    def has_add_permission(self, request):
        return request.user.is_superuser
    
    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser or (request.user.is_admin and obj and not obj.is_superuser)
    
    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

    def save_model(self, request, obj, form, change):
        # If user is marked as admin, ensure hospital is selected
        if obj.is_admin and not obj.hospital:
            from django.core.exceptions import ValidationError
            raise ValidationError("Hospital must be selected when 'Is admin' is checked.")
        # Hash password inputs and also hash previously stored raw passwords
        new_password = form.cleaned_data.get('password')
        if new_password:
            try:
                # If this doesn't raise, the value is already a valid encoded hash
                identify_hasher(new_password)
                obj.password = new_password
            except Exception:
                # Treat as raw password and hash it
                obj.set_password(new_password)
        else:
            # No new password provided; ensure existing value is a valid hash
            try:
                identify_hasher(obj.password)
            except Exception:
                # Stored value is raw; hash it in-place
                obj.set_password(obj.password)
        super().save_model(request, obj, form, change)

    class Media:
        js = ('disease_monitor/admin_user.js',)

@admin.register(Hospital)
class HospitalAdmin(admin.ModelAdmin):
    list_display = ('name', 'hospital_id', 'slug', 'created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('name', 'slug', 'hospital_id')
    readonly_fields = ('hospital_id', 'slug', 'created_at', 'updated_at')
    ordering = ('name',)
    
    def has_add_permission(self, request):
        return request.user.is_superuser or request.user.is_admin
    
    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser or request.user.is_admin
    
    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

@admin.register(PredictionHistory)
class PredictionHistoryAdmin(admin.ModelAdmin):
    list_display = ('prediction_id', 'user', 'predicted_disease', 'confidence_score', 'status', 'timestamp', 'locality')
    list_filter = ('status', 'disease_type', 'vertex_ai_enabled', 'timestamp', 'locality')
    search_fields = ('prediction_id', 'user__username', 'predicted_disease', 'actual_disease', 'locality')
    readonly_fields = ('prediction_id', 'timestamp', 'feedback_timestamp', 'model_learning_score', 'prediction_accuracy', 'is_learning_ready')
    ordering = ('-timestamp',)
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('prediction_id', 'user', 'timestamp', 'status')
        }),
        ('Patient Data', {
            'fields': ('age', 'gender', 'locality', 'schedule_date', 'pregnant_patient', 'nhia_patient')
        }),
        ('Prediction Details', {
            'fields': ('disease_type', 'symptoms_description', 'predicted_disease', 'confidence_score', 'vertex_ai_enabled')
        }),
        ('Reinforcement Learning', {
            'fields': ('actual_disease', 'medicine_prescribed', 'cost_of_treatment', 'feedback_timestamp', 'model_learning_score')
        }),
        ('Additional Info', {
            'fields': ('hospital_name', 'doctor_notes', 'prediction_accuracy', 'is_learning_ready')
        }),
    )
    
    def has_add_permission(self, request):
        return request.user.is_superuser or request.user.is_admin
    
    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser or request.user.is_admin
    
    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

@admin.register(ReinforcementLearningData)
class ReinforcementLearningDataAdmin(admin.ModelAdmin):
    list_display = ('period_start', 'period_end', 'disease_type', 'total_predictions', 'confirmed_predictions', 'avg_confidence_score')
    list_filter = ('disease_type', 'period_start', 'period_end')
    search_fields = ('disease_type',)
    readonly_fields = ('period_start', 'period_end', 'total_predictions', 'confirmed_predictions', 'corrected_predictions', 'discarded_predictions')
    ordering = ('-period_start',)
    
    def has_add_permission(self, request):
        return request.user.is_superuser
    
    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser
    
    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

@admin.register(ModelTrainingSession)
class ModelTrainingSessionAdmin(admin.ModelAdmin):
    list_display = ('session_id', 'disease_type', 'start_time', 'end_time', 'status', 'test_accuracy')
    list_filter = ('disease_type', 'status', 'start_time')
    search_fields = ('session_id', 'disease_type')
    readonly_fields = ('session_id', 'start_time', 'end_time', 'test_accuracy', 'model_file_path')
    ordering = ('-start_time',)
    
    def has_add_permission(self, request):
        return request.user.is_superuser
    
    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser
    
    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

@admin.register(PredictionFeedback)
class PredictionFeedbackAdmin(admin.ModelAdmin):
    list_display = ('prediction', 'provided_by', 'feedback_type', 'rating', 'timestamp')
    list_filter = ('feedback_type', 'rating', 'timestamp')
    search_fields = ('prediction__prediction_id', 'provided_by__username', 'feedback_text')
    readonly_fields = ('timestamp',)
    ordering = ('-timestamp',)
    
    def has_add_permission(self, request):
        return request.user.is_superuser or request.user.is_admin
    
    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser or request.user.is_admin
    
    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

@admin.register(GoogleTrendsCache)
class GoogleTrendsCacheAdmin(admin.ModelAdmin):
    list_display = ('disease_name', 'data_type', 'timeframe', 'geo', 'status', 'last_fetched', 'cache_expiry')
    list_filter = ('disease_name', 'data_type', 'status', 'geo')
    search_fields = ('disease_name', 'data_type', 'cache_key')
    readonly_fields = ('cache_key', 'last_fetched', 'last_accessed', 'fetch_count', 'retry_count')
    ordering = ('-last_fetched',)
    
    fieldsets = (
        ('Cache Information', {
            'fields': ('cache_key', 'disease_name', 'data_type', 'timeframe', 'geo')
        }),
        ('Data', {
            'fields': ('cached_data',)
        }),
        ('Status', {
            'fields': ('status', 'cache_expiry', 'last_fetched', 'last_accessed')
        }),
        ('Metrics', {
            'fields': ('fetch_count', 'retry_count', 'last_error')
        }),
    )
    
    def has_add_permission(self, request):
        return request.user.is_superuser
    
    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser
    
    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

@admin.register(GoogleTrendsMetrics)
class GoogleTrendsMetricsAdmin(admin.ModelAdmin):
    list_display = ('disease_name', 'date', 'search_interest', 'trend_direction', 'total_searches', 'last_updated')
    list_filter = ('disease_name', 'trend_direction', 'date')
    search_fields = ('disease_name',)
    readonly_fields = ('last_updated',)
    ordering = ('-date', 'disease_name')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('disease_name', 'date')
        }),
        ('Search Metrics', {
            'fields': ('search_interest', 'peak_interest', 'total_searches')
        }),
        ('Trend Analysis', {
            'fields': ('trend_direction', 'trend_strength')
        }),
        ('Related Data', {
            'fields': ('top_related_queries', 'top_related_topics', 'top_regions', 'regional_distribution')
        }),
        ('Metadata', {
            'fields': ('data_source', 'last_updated')
        }),
    )
    
    def has_add_permission(self, request):
        return request.user.is_superuser or request.user.is_admin
    
    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser or request.user.is_admin
    
    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

@admin.register(GoogleTrendsRequestLog)
class GoogleTrendsRequestLogAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'disease_name', 'data_type', 'status', 'response_time', 'cache_hit')
    list_filter = ('status', 'disease_name', 'data_type', 'cache_hit', 'timestamp')
    search_fields = ('disease_name', 'data_type', 'error_message')
    readonly_fields = ('timestamp', 'response_time', 'cache_hit', 'retry_count')
    ordering = ('-timestamp',)
    
    fieldsets = (
        ('Request Details', {
            'fields': ('timestamp', 'disease_name', 'data_type', 'timeframe', 'geo')
        }),
        ('Response', {
            'fields': ('status', 'response_time', 'cache_hit')
        }),
        ('Error Information', {
            'fields': ('error_message', 'retry_count')
        }),
        ('Rate Limiting', {
            'fields': ('rate_limit_remaining', 'rate_limit_reset')
        }),
    )
    
    def has_add_permission(self, request):
        return request.user.is_superuser
    
    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser
    
    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

# Custom admin site configuration
admin.site.site_header = "EpiScope Administration"
admin.site.site_title = "EpiScope Admin Portal"
admin.site.index_title = "Welcome to EpiScope Disease Monitoring System"

class ArticleTagAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'color', 'icon', 'get_article_count', 'created_at')
    list_filter = ('name', 'created_at')
    search_fields = ('name', 'description')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('name',)
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description')
        }),
        ('Display Settings', {
            'fields': ('color', 'icon')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def has_add_permission(self, request):
        return request.user.is_superuser or request.user.is_admin
    
    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser or request.user.is_admin
    
    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser


class ArticleCommentInline(admin.TabularInline):
    model = ArticleComment
    extra = 0
    readonly_fields = ('user', 'created_at', 'updated_at')
    fields = ('user', 'content', 'is_approved', 'is_flagged', 'likes_count', 'created_at')
    
    def has_add_permission(self, request, obj=None):
        return False


class ArticleLikeInline(admin.TabularInline):
    model = ArticleLike
    extra = 0
    readonly_fields = ('user', 'created_at')
    fields = ('user', 'created_at')
    
    def has_add_permission(self, request, obj=None):
        return False


class ArticleBookmarkInline(admin.TabularInline):
    model = ArticleBookmark
    extra = 0
    readonly_fields = ('user', 'created_at')
    fields = ('user', 'created_at')
    
    def has_add_permission(self, request, obj=None):
        return False


class ArticleViewInline(admin.TabularInline):
    model = ArticleView
    extra = 0
    readonly_fields = ('user', 'ip_address', 'user_agent', 'session_id', 'created_at')
    fields = ('user', 'ip_address', 'user_agent', 'session_id', 'created_at')
    
    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'author_name', 'article_type', 'status', 'is_featured', 'publication_date', 'estimated_read_time', 'get_tag_names', 'views_count', 'likes_count')
    list_filter = ('status', 'article_type', 'is_featured', 'publication_date', 'tags', 'created_at')
    search_fields = ('title', 'summary', 'content', 'author_name', 'author_affiliation')
    readonly_fields = ('slug', 'views_count', 'likes_count', 'comments_count', 'bookmarks_count', 'created_at', 'updated_at', 'published_at')
    ordering = ('-publication_date', '-created_at')
    prepopulated_fields = {'slug': ('title',)}
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'summary', 'content', 'article_type', 'status')
        }),
        ('Author Information', {
            'fields': ('author_name', 'author_credentials', 'author_affiliation')
        }),
        ('Publication Details', {
            'fields': ('publication_date', 'estimated_read_time', 'is_featured')
        }),
        ('Reference and Source', {
            'fields': ('reference_link', 'doi')
        }),
        ('Tags and Categories', {
            'fields': ('tags',)
        }),
        ('SEO and Display', {
            'fields': ('meta_description', 'featured_image')
        }),
        ('Engagement Metrics', {
            'fields': ('views_count', 'likes_count', 'comments_count', 'bookmarks_count'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'published_at'),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [ArticleCommentInline, ArticleLikeInline, ArticleBookmarkInline, ArticleViewInline]
    
    def get_tag_names(self, obj):
        """Display tag names in the list view"""
        return ', '.join([tag.name for tag in obj.tags.all()])
    get_tag_names.short_description = 'Tags'
    
    def has_add_permission(self, request):
        return request.user.is_superuser or request.user.is_admin
    
    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser or request.user.is_admin
    
    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser


@admin.register(ResearchPaper)
class ResearchPaperAdmin(admin.ModelAdmin):
    list_display = ('get_title', 'get_author', 'paper_type', 'journal_name', 'citation_count', 'research_quality_score', 'get_publication_date')
    list_filter = ('paper_type', 'journal_name', 'citation_count', 'research_quality_score', 'created_at')
    search_fields = ('article__title', 'abstract', 'key_findings', 'conclusions', 'journal_name')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-article__publication_date',)
    
    fieldsets = (
        ('Article Link', {
            'fields': ('article',)
        }),
        ('Research Details', {
            'fields': ('paper_type', 'abstract', 'keywords')
        }),
        ('Methodology', {
            'fields': ('methodology', 'sample_size', 'study_duration')
        }),
        ('Results and Findings', {
            'fields': ('key_findings', 'conclusions', 'limitations')
        }),
        ('Academic Metadata', {
            'fields': ('journal_name', 'volume_issue', 'page_numbers', 'impact_factor')
        }),
        ('Citations and References', {
            'fields': ('citation_count', 'references')
        }),
        ('Research Metrics', {
            'fields': ('h_index', 'research_quality_score')
        }),
        ('Funding and Ethics', {
            'fields': ('funding_source', 'ethical_approval')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_title(self, obj):
        """Get title from linked article"""
        return obj.article.title
    get_title.short_description = 'Title'
    get_title.admin_order_field = 'article__title'
    
    def get_author(self, obj):
        """Get author from linked article"""
        return obj.article.author_name
    get_author.short_description = 'Author'
    get_author.admin_order_field = 'article__author_name'
    
    def get_publication_date(self, obj):
        """Get publication date from linked article"""
        return obj.article.publication_date
    get_publication_date.short_description = 'Publication Date'
    get_publication_date.admin_order_field = 'article__publication_date'
    
    def has_add_permission(self, request):
        return request.user.is_superuser or request.user.is_admin
    
    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser or request.user.is_admin
    
    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser


@admin.register(ArticleComment)
class ArticleCommentAdmin(admin.ModelAdmin):
    list_display = ('get_article_title', 'user', 'content_preview', 'is_approved', 'is_flagged', 'likes_count', 'is_reply', 'created_at')
    list_filter = ('is_approved', 'is_flagged', 'created_at', 'article__tags')
    search_fields = ('content', 'user__username', 'article__title')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Comment Information', {
            'fields': ('article', 'user', 'content', 'parent_comment')
        }),
        ('Moderation', {
            'fields': ('is_approved', 'is_flagged')
        }),
        ('Engagement', {
            'fields': ('likes_count',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_article_title(self, obj):
        """Get article title"""
        return obj.article.title
    get_article_title.short_description = 'Article'
    get_article_title.admin_order_field = 'article__title'
    
    def content_preview(self, obj):
        """Show content preview"""
        return obj.content[:100] + '...' if len(obj.content) > 100 else obj.content
    content_preview.short_description = 'Content Preview'
    
    def is_reply(self, obj):
        """Check if this is a reply"""
        return obj.parent_comment is not None
    is_reply.boolean = True
    is_reply.short_description = 'Is Reply'
    
    def has_add_permission(self, request):
        return request.user.is_superuser or request.user.is_admin
    
    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser or request.user.is_admin
    
    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser


@admin.register(ArticleLike)
class ArticleLikeAdmin(admin.ModelAdmin):
    list_display = ('get_article_title', 'user', 'created_at')
    list_filter = ('created_at', 'article__tags')
    search_fields = ('user__username', 'article__title')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)
    
    def get_article_title(self, obj):
        """Get article title"""
        return obj.article.title
    get_article_title.short_description = 'Article'
    get_article_title.admin_order_field = 'article__title'
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser or request.user.is_admin
    
    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser


@admin.register(ArticleBookmark)
class ArticleBookmarkAdmin(admin.ModelAdmin):
    list_display = ('get_article_title', 'user', 'created_at')
    list_filter = ('created_at', 'article__tags')
    search_fields = ('user__username', 'article__title')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)
    
    def get_article_title(self, obj):
        """Get article title"""
        return obj.article.title
    get_article_title.short_description = 'Article'
    get_article_title.admin_order_field = 'article__title'
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser or request.user.is_admin
    
    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser


@admin.register(ArticleView)
class ArticleViewAdmin(admin.ModelAdmin):
    list_display = ('get_article_title', 'get_viewer', 'ip_address', 'session_id', 'created_at')
    list_filter = ('created_at', 'article__tags')
    search_fields = ('article__title', 'ip_address', 'session_id')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)
    
    def get_article_title(self, obj):
        """Get article title"""
        return obj.article.title
    get_article_title.short_description = 'Article'
    get_article_title.admin_order_field = 'article__title'
    
    def get_viewer(self, obj):
        """Get viewer information"""
        if obj.user:
            return obj.user.username
        return f"Anonymous ({obj.ip_address})"
    get_viewer.short_description = 'Viewer'
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser or request.user.is_admin
    
    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser


# Register the new models
admin.site.register(ArticleTag, ArticleTagAdmin)
