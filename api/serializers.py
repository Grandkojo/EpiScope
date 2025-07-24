from rest_framework import serializers
from .models import User
from disease_monitor.models import Disease, DiseaseYear, NationalHotspots
from .services.national_hotspots import get_available_years

class DiseaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Disease
        fields = '__all__'

class DiseaseYearSerializer(serializers.ModelSerializer):
    class Meta:
        model = DiseaseYear
        fields = '__all__'

# class DiseaseYearOnlySerializer(serializers.Serializer):
#     periodname = serializers.CharField()
    
#     class Meta:
#         model = DiseaseYear
#         fields = ['id', 'periodname']

# class DiseaseAllSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Disease
#         fields = '__all__'



class UserRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'phone', 'address']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user
    
class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'phone', 'address']

    def update(self, instance, validated_data):
        instance.username = validated_data.get('username', instance.username)
        instance.email = validated_data.get('email', instance.email)
        instance.phone = validated_data.get('phone', instance.phone)
        instance.address = validated_data.get('address', instance.address)
        instance.save()
        return instance

class NationalHotspotsSerializer(serializers.ModelSerializer):
    severity = serializers.SerializerMethodField()
    code = serializers.SerializerMethodField()
    
    class Meta:
        model = NationalHotspots
        fields = '__all__'
    
    def get_code(self, obj):
        """
        Get the region code based on the organisation unit name
        """
        region_codes = {
            "Upper West": "UW",
            "Upper East": "UE", 
            "North East": "NE",
            "Savannah": "SA",
            "Northern": "NO",
            "Bono": "BO",
            "Bono East": "BE",
            "Oti": "OT",
            "Western North": "WN",
            "Ahafo": "AH",
            "Ashanti": "AS",
            "Eastern": "ET",
            "Volta": "VO",
            "Western": "WE",
            "Central": "CE",
            "Greater Accra": "GA",
        }
        return region_codes.get(obj.organisationunitname, "")
    
    def get_severity(self, obj):
        """
        Calculate severity based on individual disease cases
        High Severity (500+ cases)
        Medium Severity (100-499 cases)
        Low Severity (<100 cases)
        Returns the highest severity among all diseases
        """
        available_years = get_available_years()
        
        # Get filters from context if available
        year_filter = self.context.get('year_filter') if hasattr(self, 'context') else None
        disease_filter = self.context.get('disease_filter') if hasattr(self, 'context') else None
        
        # Calculate total cases for each disease separately
        cholera_total = 0
        diabetes_total = 0
        meningitis_total = 0
        
        for year in available_years:
            # If year filter is specified, only include that year
            if year_filter and year_filter.lower() != 'all' and year != year_filter:
                continue
                
            cholera_cases = getattr(obj, f'cholera_lab_confirmed_cases_{year}', 0) or 0
            diabetes_cases = getattr(obj, f'diabetes_mellitus_lab_confirmed_cases_{year}', 0) or 0
            meningitis_cases = getattr(obj, f'meningococcal_meningitis_lab_confirmed_cases_{year}', 0) or 0
            
            cholera_total += cholera_cases
            diabetes_total += diabetes_cases
            meningitis_total += meningitis_cases
        
        # If disease filter is specified, only calculate severity for that disease
        if disease_filter and disease_filter.lower() != 'all':
            if disease_filter == 'cholera':
                total_cases = cholera_total
            elif disease_filter == 'diabetes':
                total_cases = diabetes_total
            elif disease_filter == 'meningitis':
                total_cases = meningitis_total
            else:
                total_cases = 0 
        else:
            # Use the highest among all diseases
            total_cases = max(cholera_total, diabetes_total, meningitis_total)
        
        # Determine severity based on total cases
        if total_cases >= 500:
            return "high"
        elif total_cases >= 100:
            return "medium"
        elif total_cases > 1 and total_cases < 100:
            return "low"
        else:
            return "none"
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Get the disease filter and year filter from context if available
        disease_filter = self.context.get('disease_filter') if hasattr(self, 'context') else None
        year_filter = self.context.get('year_filter') if hasattr(self, 'context') else None
        
        exclude_fields = []
        
        # Only exclude fields if a specific year is selected (not 'all' or None)
        if year_filter and year_filter.lower() != 'all':
            available_years = get_available_years()
            for year in available_years:
                if year != year_filter:
                    # Exclude all disease fields for non-matching years
                    exclude_fields.extend([
                        f'cholera_lab_confirmed_cases_{year}',
                        f'diabetes_mellitus_lab_confirmed_cases_{year}',
                        f'meningococcal_meningitis_lab_confirmed_cases_{year}'
                    ])
        
        # Only exclude fields if a specific disease is selected (not 'all' or None)
        if disease_filter and disease_filter.lower() != 'all':
            # Get available years dynamically
            available_years = get_available_years()
            
            if disease_filter == 'diabetes':
                # Exclude cholera and meningitis fields for all available years
                for year in available_years:
                    exclude_fields.extend([
                        f'cholera_lab_confirmed_cases_{year}',
                        f'meningococcal_meningitis_lab_confirmed_cases_{year}'
                    ])
            elif disease_filter == 'cholera':
                # Exclude diabetes and meningitis fields for all available years
                for year in available_years:
                    exclude_fields.extend([
                        f'diabetes_mellitus_lab_confirmed_cases_{year}',
                        f'meningococcal_meningitis_lab_confirmed_cases_{year}'
                    ])
            elif disease_filter == 'meningitis':
                # Exclude diabetes and cholera fields for all available years
                for year in available_years:
                    exclude_fields.extend([
                        f'diabetes_mellitus_lab_confirmed_cases_{year}',
                        f'cholera_lab_confirmed_cases_{year}'
                    ])
        
        # Remove excluded fields from the serializer
        for field in exclude_fields:
            if field in self.fields:
                del self.fields[field]