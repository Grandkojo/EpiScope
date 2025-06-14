from rest_framework import serializers
from disease_monitor.models import Disease, DiseaseYear

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

