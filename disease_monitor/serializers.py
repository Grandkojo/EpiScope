from rest_framework import serializers
from .models import DiseaseTrends
from .models import HospitalLocalities
from .models import Hospital

class DiseaseTrendsSerializer(serializers.ModelSerializer):
    disease_name = serializers.CharField(source='disease.disease_name', read_only=True)

    class Meta:
        model = DiseaseTrends
        fields = ['id', 'disease', 'disease_name', 'year', 'month', 'trend_value']

class HospitalLocalitiesSerializer(serializers.ModelSerializer):
    """
    Serializer for HospitalLocalities model
    """
    class Meta:
        model = HospitalLocalities
        fields = ['id', 'locality', 'orgname', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

class HospitalLocalitiesListSerializer(serializers.ModelSerializer):
    """
    Simplified serializer for listing hospital localities
    """
    class Meta:
        model = HospitalLocalities
        fields = ['locality', 'orgname']

class HospitalLocalitiesFilterSerializer(serializers.Serializer):
    """
    Serializer for filtering hospital localities
    """
    locality = serializers.CharField(required=False, help_text="Filter by locality")
    orgname = serializers.CharField(required=False, help_text="Filter by hospital name")
    search = serializers.CharField(required=False, help_text="Search in both locality and orgname")

class HospitalSerializer(serializers.ModelSerializer):
    """
    Serializer for Hospital model
    """
    class Meta:
        model = Hospital
        fields = ['id', 'name', 'slug', 'created_at', 'updated_at']
        read_only_fields = ['id', 'slug', 'created_at', 'updated_at']

class HospitalListSerializer(serializers.ModelSerializer):
    """
    Simplified serializer for listing hospitals
    """
    class Meta:
        model = Hospital
        fields = ['id', 'name', 'slug']

class HospitalFilterSerializer(serializers.Serializer):
    """
    Serializer for filtering hospitals
    """
    name = serializers.CharField(required=False, help_text="Filter by hospital name")
    search = serializers.CharField(required=False, help_text="Search in hospital name") 