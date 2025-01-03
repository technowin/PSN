from rest_framework import serializers

from Masters.models import parameter_master, sc_roster
from Masters.serializers import ScRosterSerializer
from Notification.models import notification_log, test_table



class NotificationSerializer(serializers.ModelSerializer):
    sc_roster = ScRosterSerializer()  # Use the nested serializer

    class Meta:
        model = notification_log
        fields = '__all__'  # Include all fields, or specify specific fields as needed

class TestTableSerializer(serializers.ModelSerializer):
    class Meta:
        model = test_table
        fields = ['id', 'test_time']
        read_only_fields = ['test_time']

class ParameterMasterSerializer(serializers.ModelSerializer):  # Corrected serializer class name
    class Meta:
        model = parameter_master  # Assuming the model name is in PascalCase, adjust if necessary
        fields = '__all__' 

class ScRosterSerializerNoti(serializers.ModelSerializer):

    class Meta:
        model = sc_roster
        fields = '__all__'  


class NotificationLogSerializer(serializers.ModelSerializer):
    sc_roster_id = ScRosterSerializerNoti()
    type = ParameterMasterSerializer()
    class Meta:
        model = notification_log
        fields = '__all__' 