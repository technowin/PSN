from rest_framework import serializers

from Masters.models import *

 
class CompanyMasterSerializer(serializers.ModelSerializer):
    class Meta:
        model = company_master
        fields = '__all__'  # Include all fields, or specify specific fields as needed



class ScRosterSerializer(serializers.ModelSerializer):
    company = CompanyMasterSerializer()  # Use the nested serializer

    class Meta:
        model = sc_roster
        fields = '__all__'  # Include all fields, or specify specific fields as needed
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        # Replace null shift_time with an empty string
        if instance.shift_time is None:
            representation['shift_time'] = ""
        return representation