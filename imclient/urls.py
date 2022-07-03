from django.urls import path, include
from rest_framework import routers
from . import views

router = routers.DefaultRouter()

router.register(r'fileList', views.FileListViewSet)
router.register(r'setFileList', views.SetFileList)

urlpatterns = [
    path('',include(router.urls)),
    path('api-auth/', include('rest_framework.urls',namespace='rest_framework'))
]
