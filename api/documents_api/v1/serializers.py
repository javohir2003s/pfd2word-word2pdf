from rest_framework import serializers
from documents.models import FileConverter


class FileUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = FileConverter
        fields = ['id', 'user', 'uploaded_file', 'converted_file', 'uploaded_at']
        read_only_fields = ['id', 'user', 'converted_file', 'uploaded_at']

    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['user'] = user
        return FileConverter.objects.create(**validated_data)