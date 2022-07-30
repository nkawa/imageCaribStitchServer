from django.urls import path, include
from rest_framework import routers
from . import views

router = routers.DefaultRouter()

router.register(r'fileList', views.FileListViewSet, 'fileList')
router.register(r'setFileListWhy', views.SetFileList,'setFileList')
router.register(r'imageList', views.ImageListViewSet, 'imageList')


urlpatterns = [
    path('saveCalibInfo', views.SaveCalibInfo.as_view(), name='saveCalibInfo'),
    path('doCalibImage', views.DoCalibImage.as_view(), name='doCalibImage'),
    path('captureVideo', views.CaptureVideo.as_view(), name='captureVideo'),
    path('convImage', views.ConvImage.as_view(), name='convImage'),
    path('findChecker', views.FindChecker.as_view(), name='findChecker'),
    path('genPlaneFileList', views.GenPlaneFileList.as_view(), name='genPlaneFile'),
    path('genCarib', views.GenCarib.as_view(), name='genCarib'),
    path('captureVideoPlane', views.CaptureVideoPlane.as_view(), name='captureVideoPlane'),
    path('',include(router.urls)),
    path('api-auth/', include('rest_framework.urls',namespace='rest_framework'))
]
