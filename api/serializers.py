from rest_framework import serializers
from .models import User
from disease_monitor.models import Disease, DiseaseYear, NationalHotspots

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
    class Meta:
        model = NationalHotspots
        fields = '__all__'