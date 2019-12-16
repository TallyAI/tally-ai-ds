from rest_framework import serializers
from api.models import Url

class WordListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Url
        fields = '__all__'

#converts to JSON, validates the data