from rest_framework import serializers
from yelp.models import business_id_test1, scraping_test1

class WordListSerializer(serializers.ModelSerializer):
    class Meta:
        model = business_id_test1
        fields = '__all__'

#converts to JSON, validates the data