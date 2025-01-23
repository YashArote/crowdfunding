from django.urls import include,path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

urlpatterns=[
    
    path("account/",include("django.contrib.auth.urls")),
    path("register/",views.register,name="register"),
    path("",views.allCampaigns,name="allcampaign"),
    path("campaigns/",views.allCampaigns,name="allcampaigns"),
    path("campaigns/detail/<int:id>/",views.campaign_detail,name="detail"),
    path("campaigns/<address>/",views.userCampaigns,name="user"),

    path("create/",views.createCampaign,name="create"),
    path("approve/",views.approve,name="approve"),
    path('logout/', auth_views.LogoutView.as_view(next_page=settings.LOGOUT_REDIRECT_URL), name='logout'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)
