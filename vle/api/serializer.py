from rest_framework import serializers
from university import models as university_models



class FacultySerializer(serializers.ModelSerializer):
    class Meta:
        model = university_models.Faculty
        fields = '__all__'



class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = university_models.Department
        fields = '__all__'


class BatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = university_models.Batch
        fields = '__all__'

