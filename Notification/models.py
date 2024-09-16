from django.db import models

from Account.models import CustomUser
from Masters.models import parameter_master, sc_roster

# Create your models here.

class notification_log(models.Model):
    id = models.AutoField(primary_key=True)
    sc_roster_id = models.ForeignKey(sc_roster, on_delete=models.CASCADE,related_name='sc_roster_id',blank=True, null=True,db_column='sc_roster_id')
    notification_sent = models.DateTimeField(null=True,blank=True)
    notification_received = models.DateTimeField(null=True,blank=True)
    notification_opened = models.DateTimeField(null=True,blank=True)
    notification_message = models.TextField(null=True, blank=True)
    type = models.ForeignKey(parameter_master, on_delete=models.CASCADE,related_name='type_id_parameter',blank=True, null=True,db_column='type_id')
    created_at = models.DateTimeField(null=True,blank=True,auto_now_add=True)
    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE,related_name='noti_created_by',blank=True, null=True,db_column='created_by')
    updated_at = models.DateTimeField(null=True,blank=True,auto_now_add=True)
    updated_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE,related_name='noti_updated_by',blank=True, null=True,db_column='updated_by')
    class Meta:
        db_table = 'notification_log'
    def __str__(self):
        return self.employee_id

