from rest_framework import serializers
from .models import DiseaseTrends

class DiseaseTrendsSerializer(serializers.ModelSerializer):
    disease_name = serializers.CharField(source='disease.disease_name', read_only=True)

    class Meta:
        model = DiseaseTrends
        fields = ['id', 'disease', 'disease_name', 'year', 'month', 'trend_value'] 