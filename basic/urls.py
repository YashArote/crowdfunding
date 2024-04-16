from django.urls import include,path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns=[
    
    path("account/",include("django.contrib.auth.urls")),
    path("register/",views.register,name="register"),
    path("",views.allCampaigns,name="allcampaign"),
    path("campaigns/",views.allCampaigns,name="allcampaigns"),
    path("campaigns/detail/<int:id>/",views.campaign_detail,name="detail"),
    path("campaigns/<address>/",views.userCampaigns,name="user"),

    path("create/",views.createCampaign,name="create"),
    path("approve/",views.approve,name="approve")
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)
