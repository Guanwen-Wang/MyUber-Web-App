from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
import datetime  # for checking
from django.utils import timezone as datetime
from datetime import datetime, timedelta, tzinfo
from django.views.generic.edit import CreateView, UpdateView, DeleteView


class RenewBookForm(forms.Form):
    renewal_date = forms.DateField(help_text="Enter a date between now and 4 weeks (default 3).")

    def clean_renewal_date(self):
        data = self.cleaned_data['renewal_date']

        # Check date is not in past.
        if data < datetime.date.today():
            raise ValidationError(_('Invalid date - renewal in past'))

        # Check date is in range librarian allowed to change (+4 weeks).
        if data > datetime.date.today() + datetime.timedelta(weeks=4):
            raise ValidationError(_('Invalid date - renewal more than 4 weeks ahead'))

        # Remember to always return the cleaned data.
        return data


class MakeRequest(forms.Form):
    destination = forms.CharField(help_text="Enter a destination")
    arrival_time = forms.DateTimeField(help_text="arrival time")
    passenger_number = forms.IntegerField(max_value=6, min_value=1)
    is_shared = forms.RadioSelect()
    special_request = forms.CharField(help_text="special request", required=False)
    special_vehicle_type = forms.CharField(help_text="special request", required=False)

    def cleaned_arrival_time(self):
        arrival_time = self.cleaned_data['arrival_time']
        now = datetime.now()
        # now = now.replace(tzinfo=)
        if arrival_time < now:  # datetime.datetime.now():
            raise ValidationError(_('Invalid date'))
        return arrival_time


class MakeShareRequest(forms.Form):
    destination = forms.CharField(help_text="Enter a destination")
    earliest_arrival = forms.DateTimeField(help_text="earliest arrival time")
    latest_arrival = forms.DateTimeField(help_text="latest arrival time")
    share_pass_num = forms.IntegerField(min_value=1, max_value=6)


from .models import User, Order
from django.contrib.auth.forms import UserCreationForm, UserChangeForm


class EditInfoForm(forms.Form):
    username = forms.CharField(help_text="Enter a username")
    email = forms.EmailField()
    vehicle_type = forms.CharField()
    license_num = forms.CharField()
    max_passenger = forms.IntegerField()
    full_name = forms.CharField(max_length=50, help_text="full name")
    special_vehicle_info = forms.CharField(help_text="extra vehicle information")


class UpgradeAsDriverForm(forms.Form):
    full_name = forms.CharField(max_length=50, help_text="full name")
    vehicle_type = forms.CharField()
    license_num = forms.CharField()
    max_passenger = forms.IntegerField()
    special_vehicle_info = forms.CharField(help_text="extra vehicle information")


class RegisterAsUserForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        model.is_driver = False
        fields = ("username", "email")


class RegisterAsDriverForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        model.is_driver = True
        fields = ("username", "email", "full_name", "vehicle_type", "license_num", "max_passenger", "plate_num",
                  "special_vehicle_info")


from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy


class MyOwnRequestUpdateForm(forms.Form):
    destination = forms.CharField(help_text="Enter a destination")
    arrival_time = forms.DateTimeField(help_text="arrival time")
    own_pass_num = forms.IntegerField(max_value=6, min_value=1)
    is_shared = forms.RadioSelect()
    special_request = forms.CharField(help_text="special request", required=False)
    special_vehicle_type = forms.CharField(help_text="special vehicle type", required=False)

    def cleaned_arrival_time(self):
        arrival_time = self.cleaned_data['arrival_time']
        if arrival_time < datetime.date.today():
            raise ValidationError(_('Invalid date'))
        return arrival_time


"""   
class AuthorDelete(DeleteView):
    model = Author
   success_url = reverse_lazy('authors')
"""


class MyShareRequestUpdateForm(forms.Form):
    # destination = forms.CharField(help_text="Enter a destination")
    # arrival_time = forms.DateTimeField(help_text="arrival time")
    share_pass_num = forms.IntegerField(max_value=6, min_value=1)

    def cleaned_number(self):
        number = self.cleaned_data['share_pass_num']
        if number > 6 or number < 1:
            raise ValidationError(_('Invalid date'))
        return number

    # def cleaned_arrival_time(self):
    #     arrival_time = self.cleaned_data['arrivalTime']
    #     if arrival_time < datetime.date.today():
    #         raise ValidationError(_('Invalid date'))
    #     return arrival_time
