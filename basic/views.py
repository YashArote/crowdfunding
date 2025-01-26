from django.shortcuts import render
from web3 import Web3
from .forms import ImageForm,CampaignForm,UserRegistrationForm,AddressForm,ProfileForm
from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_GET
from .models import Address,Approve,Image
from .contract_data import *;
from datetime import datetime
from django.contrib.auth.models import User
import pytz
import base64

def days_difference_from_unix_timestamp(unix_timestamp):
    timestamp_datetime_utc = datetime.utcfromtimestamp(unix_timestamp)
    ist_timezone = pytz.timezone('Asia/Kolkata')
    timestamp_datetime_ist = timestamp_datetime_utc.astimezone(ist_timezone)
    current_datetime_ist = datetime.now(ist_timezone)
    difference =  timestamp_datetime_ist - current_datetime_ist 
    difference_in_days = difference.days

    return difference_in_days

def register(request):
    if request.method=="POST":
        user_form=UserRegistrationForm(request.POST)
        profile_form=ProfileForm(data=request.POST,files=request.FILES)
        print("is valid",profile_form.is_valid())
        address_form=AddressForm(data=request.POST)
        if user_form.is_valid() and address_form.is_valid() and profile_form.is_valid():
            cd=user_form.cleaned_data
            new_user=user_form.save(commit=False)
            new_user.set_password(cd["password"])
            new_user.save()

            new_profile=profile_form.save(commit=False)
            new_profile.user=new_user
            new_profile.save()
            cd1=address_form.cleaned_data
            Address.objects.create(user=new_user,address=cd1["address"])
            return render(request=request,template_name="account/register_done.html",context={"user":new_user})
    else:
        user_form=UserRegistrationForm()
        address_form=AddressForm()
        profile_form=ProfileForm()
    return render(request,"account/register.html",{"user_form":user_form,"address_form":address_form,"profile_form":profile_form})
# Create your views here.
@login_required
def allCampaigns(request):
   
    approved=Approve.objects.filter(approved=True,rejected=False).values_list("camp_id",flat=True)
    images=Image.objects.filter(id__in=approved)
    urls= [image.image.url for image in images ]
    #print(urls)
    campaignData = SimpleStorage.functions.getAllCampaigns().call()
    print("up",campaignData)
    camp_approved=[]
    for camp in campaignData:
        for url in urls:

            if camp[7]==url:
                #print(camp[6])
                camp+=(urls.index(url),)
                camp_temp=list(camp)
                camp_temp[6]=w3.from_wei(camp_temp[6],"ether")
                days_left=days_difference_from_unix_timestamp(camp_temp[5])
                camp_temp[5]=days_left
                if(days_left>0):
                    camp_approved.append(tuple(camp_temp))
                
    
    campaignData=camp_approved
    print(campaignData)
    return render(
        request, "account/campaigns.html", context={"campaigns": campaignData}
    )
@login_required
def createCampaign(request):
    campaign=CampaignForm()
    image=ImageForm()
    submit=None
    imageUrl=None
    date=None
    data=None

    if request.method=="POST":
        campaign1=CampaignForm(request.POST)
        image1=ImageForm(data=request.POST,files=request.FILES)
        if campaign1.is_valid() and image1.is_valid():
            
            data=campaign1.cleaned_data
            data["owner"]=request.user.address.address
            savedImg=image1.save()
            imageUrl=savedImg.image.url
            date=campaign1.get_unix()
            Approve.objects.create(camp_id=savedImg.id)
            data["id"]=savedImg.id
            submit=True
            print("inside called")

        else:
            campaign=campaign1
            image=image1

# print(nonce)
    print("data: ",data)
    return render(request=request,template_name="account/create.html",context={"form1":campaign,"form2":image,"submit":submit,"data":data,"image":imageUrl,"date":date})

@login_required
def approve(request):
    for_approval=Approve.objects.filter(approved=False,rejected=False).values_list("camp_id",flat=True)
    images=Image.objects.filter(id__in=for_approval)
    #print(images)

    approved=False
    rejected=False
    if request.method=="POST":
        campaign_img=request.POST.get("camp_img")
        img=None
        for image in images:
            if image.image.url==campaign_img:
                img=image
        app_obj=Approve.objects.get(camp_id=img.id)
        if(request.POST.get("reject")):
             print("rejected")
             app_obj.rejected=True
             app_obj.save()
             rejected=True

        else:

           
            app_obj.approved=True
            app_obj.save()
            approved=True
        for_approval=Approve.objects.filter(approved=False,rejected=False).values_list("camp_id",flat=True)
        images=Image.objects.filter(id__in=for_approval)
    
    urls= [image.image.url for image in images ]
    #print(urls)
    campaignData = SimpleStorage.functions.getAllCampaigns().call()
    print(campaignData)
    camp_unapproved=[]
    for camp in campaignData:
        for url in urls:
            if camp[7]==url:
                #print(camp[6])

                camp_unapproved.append(camp)

    print(camp_unapproved)
    
    return render(request,"account/approve.html",{"campaigns":camp_unapproved,"approved":approved,"rejected":rejected})

@login_required
@require_GET
def userCampaigns(request,address):
  
    approved=Approve.objects.filter(approved=True,rejected=False).values_list("camp_id",flat=True)
    images=Image.objects.filter(id__in=approved)
    urls= [image.image.url for image in images ]
    #print(urls)
    campaignData = SimpleStorage.functions.getAllCampaigns().call()
    print(campaignData)
    print(str(address).upper)
    camp_approved=[]
    for camp in campaignData:
        for url in urls:
            if camp[7]==url and str(camp[0]).upper()== str(address).upper():
                #print(camp[6])
                camp+=(urls.index(url),)
                camp_temp=list(camp)
                camp_temp[6]=w3.from_wei(camp_temp[6],"ether")
                days_left=days_difference_from_unix_timestamp(camp_temp[5])
                camp_temp[5]=days_left
                camp_approved.append(tuple(camp_temp))
    campaignData=camp_approved
    return render(
        request, "account/campaigns.html", context={"campaigns": campaignData}
    )

@login_required
def campaign_detail(request,id):


    if request.method=="GET":
       
        camp_id_1=id
        smart_camp_id=0
    #  print(str(request.GET.get("image"))) 
        approved=Approve.objects.filter(approved=True,rejected=False).values_list("camp_id",flat=True)
        images=Image.objects.filter(id__in=approved)
        urls= [image.image.url for image in images ]
        #print(urls)
        campaignData = SimpleStorage.functions.getAllCampaigns().call()
        
        camp=None
        for camp1 in campaignData:
            for url in urls:
                if camp1[7]==url and camp1[7]==urls[id]:
                    
                    #print(camp[6])
                    camp=camp1
                    break
        print(camp)
        days_left=days_difference_from_unix_timestamp(camp[5])
        smart_camp_id=camp[0]
        image=camp[7]
        creator=camp[1]
        title=camp[2]
        description=camp[3]
        target=camp[4]
        print("COLLECT",camp[6])
        collected= w3.from_wei(camp[6],"ether")
        print("collected :- ",collected)
        donators=camp[8]
        donators_1=[ (Address.objects.filter(address=i)[0].user.username,i) for i in donators ]
        return render(
        request, "account/campaigns.html", context={"detail":"yes","left":days_left,"creator":creator,"title":title,"description":description,"target":target,
                                                    "collected":collected,"donators":donators_1,"image":image,"id":smart_camp_id}
    )


