from rest_framework import serializers

from Masters.serializers import ScRosterSerializer
from Notification.models import notification_log



class NotificationSerializer(serializers.ModelSerializer):
    sc_roster = ScRosterSerializer()  # Use the nested serializer

    class Meta:
        model = notification_log
        fields = '__all__'  # Include all fields, or specify specific fields as needed