from django.db import models
#from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractUser
from django.urls import reverse  # Used to generate URLs by reversing the URL patterns
from datetime import date
import uuid
class User(AbstractUser):

    is_driver = models.BooleanField(default=False)
    full_name = models.CharField(max_length=200,null=True,blank=True,help_text="full name")
    vehicle_type = models.CharField(max_length=200,null=True,blank=True,help_text="vehicle type")
    license_num = models.CharField(max_length=200, null=True, blank=True, help_text="Licence Number")
    plate_num = models.CharField(max_length=200, null=True, blank=True, help_text="Plate Number")
    max_passenger = models.IntegerField(null=True,blank=True,help_text="max passenger number")
    special_vehicle_info = models.CharField(max_length=1000,null=True,blank=True,help_text="special vehicle information")
    class Meta(AbstractUser.Meta):
        pass

class Order(models.Model):
    id = models.UUIDField(primary_key=True, auto_created=True, default=uuid.uuid4,
                          help_text="Unique ID for the request")
    destination = models.CharField(max_length=200,help_text="Destination",null=True)
    arrival_time = models.DateTimeField(help_text="form:year-month-day HH:YY",null=True)
    passenger_number = models.IntegerField(help_text="1-6 people",null=True)
    own_pass_num = models.IntegerField(null=True,blank=True,help_text="1-6 people")
    is_shared = models.BooleanField(default=False)
    driver = models.ForeignKey(User,on_delete=models.SET_NULL, null=True,blank=True,related_name='driver')
    #sharer = models.ManyToManyField(User,null=True,blank=True,default=None,related_name='sharer')
    owner = models.ForeignKey(User, on_delete=models.SET_NULL,null=True,related_name='owner')
    special_request = models.TextField(max_length=1000,null=True,blank=True,help_text="Other requests",default=None)#match info
    special_vehicle_type = models.CharField(max_length=200,help_text="Destination",null=True,blank=True,default=None)#match vehicle type

    STATUS = (
        ('open', 'open'),
        ('confirmed', 'confirmed'),
        ('completed', 'completed'),
    )
    status = models.CharField(max_length=10, choices=STATUS,default='open', help_text='request status')
    def __str__(self):
        return self.destination

    def get_absolute_url(self):
        return reverse('order-detail', args=[str(self.id)])

class Party(models.Model):
    party_id = models.UUIDField(primary_key=True, auto_created=True, default=uuid.uuid4,help_text="Unique ID for the party")
    sharer_person = models.ForeignKey(User,on_delete=models.CASCADE,related_name='sharer_person',null=True)
    share_pass_num = models.IntegerField(null=True,help_text="sharing people")
    request = models.ForeignKey(Order,on_delete=models.CASCADE,null=True)#models.SET_NULL,blank=True,null=True)
    sharer_name = models.CharField(max_length=200, help_text="share_name",null=True)
    def __str__(self):
        return self. sharer_name

    def get_absolute_url(self):
        return reverse('order-detail', args=[str(self.id)])
