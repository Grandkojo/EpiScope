from django.contrib import admin
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from .models import DiabetesData, MeningitisData, CholeraData, NationalHotspots, Disease, DiseaseYear, RegionPopulation, Hospital
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

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'phone', 'is_admin', 'is_email_verified', 'is_phone_verified', 'is_staff', 'is_superuser')
    list_filter = ('is_admin', 'is_email_verified', 'is_phone_verified', 'is_staff', 'is_superuser', 'is_active')
    search_fields = ('username', 'email', 'phone')
    readonly_fields = ('date_joined', 'last_login')
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email', 'phone', 'address')}),
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

@admin.register(Hospital)
class HospitalAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('name', 'slug')
    readonly_fields = ('slug', 'created_at', 'updated_at')
    ordering = ('name',)
    
    def has_add_permission(self, request):
        return request.user.is_superuser or request.user.is_admin
    
    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser or request.user.is_admin
    
    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

# Custom admin site configuration
admin.site.site_header = "EpiScope Administration"
admin.site.site_title = "EpiScope Admin Portal"
admin.site.index_title = "Welcome to EpiScope Disease Monitoring System"
