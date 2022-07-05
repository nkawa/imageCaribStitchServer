from django.urls import path, include
from rest_framework import routers
from . import views

router = routers.DefaultRouter()

router.register(r'fileList', views.FileListViewSet, 'fileList')
router.register(r'setFileListWhy', views.SetFileList,'setFileList')
router.register(r'imageList', views.ImageListViewSet, 'imageList')


urlpatterns = [
    path('captureVideo', views.CaptureVideo.as_view(), name='captureVideo'),
    path('captureVideoPlane', views.CaptureVideoPlane.as_view(), name='captureVideoPlane'),
    path('',include(router.urls)),
    path('api-auth/', include('rest_framework.urls',namespace='rest_framework'))
]
