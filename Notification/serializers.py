from rest_framework import serializers

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