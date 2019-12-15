from rest_framework import serializers
from api.models import url

class WordListSerializer(serializers.ModelSerializer):
    class Meta:
        model = url
        fields = '__all__'

#converts to JSON, validates the data