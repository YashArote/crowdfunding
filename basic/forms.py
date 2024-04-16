from typing import Any, Mapping
from django import forms
from django.core.files.base import File
from django.db.models.base import Model
from django.forms.utils import ErrorList
from .models import Image,Profile
from bootstrap_datepicker_plus.widgets import DateTimePickerInput
from datetime import datetime,timezone
from django.contrib.auth.models import User
from .models import Address
from PIL import Image as im

class ProfileForm(forms.ModelForm):
    class Meta:
        model=Profile
        fields=["photo"]



class CampaignForm(forms.Form):
    owner=forms.CharField(widget=forms.HiddenInput(attrs={
        "id":"hidden1",
    }))
    title=forms.CharField(max_length=20)
    description=forms.CharField(widget=forms.Textarea)
    target=forms.IntegerField(max_value=100)
    deadline=forms.DateTimeField(widget=DateTimePickerInput,error_messages={'required':''})
    date1=None
    def clean_deadline(self):
        cd=self.cleaned_data
        print(cd)
        date=cd["deadline"]
        self.date1=date
        print(self.date1,"self")
        now=datetime.now(timezone.utc)
        difference=date-now
        print(difference.days)
        print(date)
        if(difference.days>30):
            raise forms.ValidationError("Campaign can only run for 30 days")
    def get_unix(self):
        
        unixtime=int(round(self.date1.timestamp()))
        return unixtime
class ImageForm(forms.ModelForm):
    x = forms.FloatField(widget=forms.HiddenInput())
    y = forms.FloatField(widget=forms.HiddenInput())
    width = forms.FloatField(widget=forms.HiddenInput())
    height = forms.FloatField(widget=forms.HiddenInput())
    class Meta:
        model=Image
        fields=["image","x","y","width","height"]
        error_messages={"required":"Please upload an Image"}
    
    def save(self):
        photo=super().save()

        x=self.cleaned_data.get("x")
        y=self.cleaned_data.get("y")
        w=self.cleaned_data.get("width")
        h=self.cleaned_data.get("height")

        image = im.open(photo.image)
        cropped_image = image.crop((x, y, w+x, h+y))
       # resized_image = cropped_image.resize((200, 200), Image.ANTIALIAS)
        cropped_image.save(photo.image.path)

        return photo

class UserRegistrationForm(forms.ModelForm):
    password=forms.CharField(label="Password",widget=forms.PasswordInput)
    password2=forms.CharField(label="Repeat Password",widget=forms.PasswordInput)

    class Meta:
        model= User
        fields=["username","first_name","email"]
    def clean_password2(self):
        cd=self.cleaned_data
        if cd["password"]!=cd["password2"]:
            raise forms.ValidationError("Passwords don't match")
        return cd["password2"]
    def clean_email(self):
        cd=self.cleaned_data
        if User.objects.filter(email=cd["email"]).exists():
            
            raise forms.ValidationError("Email already in use")
        return cd["email"]
    def __init__(self,*args,**kwargs):
       
        super().__init__(*args, **kwargs)
        self.fields['email'].required = True
        self.fields['first_name'].required = True
class AddressForm(forms.ModelForm):
    class Meta:
        model=Address
        fields=["address"]
    def __init__(self, *args, **kwargs):
        super(AddressForm, self).__init__(*args, **kwargs)
        self.fields["address"].widget = forms.TextInput(attrs={
            "id":"userAddress","disabled":"disabled"})
