import re
from django.shortcuts import render
# Create your views here.
from django.contrib.auth.models import User, Group
#from yaml import serialize
#from imclient.serializers import ImFileSerializer
from rest_framework import viewsets
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.views import APIView

# for file listing
import glob
import os
import logging
import datetime
import humanfriendly
from . import carib

from .models import ImFile, CaribImage
from .serializers import ImFileSerializer, CaribSerializer

class FileListViewSet(viewsets.ModelViewSet):
    queryset = ImFile.objects.all()
    serializer_class = ImFileSerializer

class ImageListViewSet(viewsets.ModelViewSet):
    queryset = CaribImage.objects.all()
    serializer_class = CaribSerializer

    def get_queryset(self):
#        print("Got GET", self.request.GET)
#        cam = self.request.GET['cam']
        fname = self.request.GET['fname']
        return CaribImage.objects.filter(fname=fname).order_by("time")


class SetFileList(viewsets.ModelViewSet):
    queryset = ImFile.objects.all()
    serializer_class = ImFileSerializer

    def get_queryset(self):
#        files = glob.glob("/mnt/qnap105/gstreamer/2022/2022-05-17/cameraG?/*.mkv")
        files = glob.glob("/mnt/qnap104/ptokai_demo/conv_mp4/2022-05-17/camera*/*.mp4")
    ## ここでモデルとして、ファイル一覧を登録する？
    ## 特定のフォルダで、ファイル一覧を登録するよう感じがいいかも。
    ## ImFile オブジェクトを追加する
##        logging.debug("Coming here!! len:",len(files))
        for f in files:
            ff = os.stat(f).st_ctime
            #ファイル名、ディレクトリ名でわけたほうが良さそうだね。（どっち側でやるか、って話はあるか）
            fsize = os.path.getsize(f)
            human = humanfriendly.format_size(fsize)
            ImFile.objects.create(fname=f,fsize=fsize, fhuman = human ,fdate=datetime.datetime.fromtimestamp(ff,datetime.timezone(datetime.timedelta(hours=0),'JST')))
        
        return ImFile.objects.all()



class CaptureVideo(APIView):
    cb = carib.setCalibData()
    print("Set Caribdata!",len(cb))

    # 特定の状況でキャプチャする
    def get(self, request, format=None):
        print("Get CaptureVideo!!",request)
        mod = CaribImage.objects.all()
        serializer = CaribSerializer(mod)
        return Response(serializer.data)

    def post(self, request, format=None):
        print("Oh! get data message", request.data)
        fname = request.data['fname']
        camera =request.data['camera']
        cam = camera[6:]
        time = request.data['time']
        # read Default Caribdata
#        print("Got", fname, cam, time)
        sfname = "/mnt/qnap104/ptokai_demo/conv_mp4/2022-05-17/"+camera+"/"+fname
#        print("Its working", sfname)
        ff = fname.split(".")
        fd = "/mnt/qnap104/ptokai_demo/conv_mp4/2022-05-17/"+camera+"/png/"
        os.makedirs(fd, exist_ok=True)
        fn = ff[0]+"_"+str(time)+".png"
        cfile = fd+fn
        sfile = camera+"/png/"+fn
        if CaribImage.objects.filter(cfile=sfile).exists():
            qobj = CaribImage.objects.get(cfile=sfile)
            serializer = CaribSerializer(qobj)
            return Response(serializer.data)
        
        cfile = carib.capAndCarib(sfname, time, self.cb[cam],cfile)
#        print("Its working2", sfname)


        carObj= CaribImage.objects.create(
            cam = cam,
            fname=fname,
            time=time,
            json=self.cb[cam],
            cfile =camera+"/png/"+fn
        )
        carObj.save()

#        mod = CaribImage.objects.all()
        serializer = CaribSerializer(carObj)
        return Response(serializer.data)



class CaptureVideoPlane(APIView):
    # 特定の状況でキャプチャする

    def post(self, request, format=None):
        fname = request.data['fname']
        camera =request.data['camera']
        cam = camera[6:]
        time = request.data['time']
        # read Default Caribdata
#        print("Got", fname, cam, time)
        sfname = "/mnt/qnap104/ptokai_demo/conv_mp4/2022-05-17/"+camera+"/"+fname
#        print("Its working", sfname)
        ff = fname.split(".")
        fd = "/mnt/qnap104/ptokai_demo/conv_mp4/2022-05-17/"+camera+"/png/"
        os.makedirs(fd, exist_ok=True)
        fn = ff[0]+"_"+str(time)+"_plane.png"

        # 同じオブジェクトがあれば、それを返す
        cfile = fd+fn
        sfile = camera+"/png/"+fn
        if CaribImage.objects.filter(cfile=sfile).exists():
            qobj = CaribImage.objects.get(cfile=sfile)
            serializer = CaribSerializer(qobj)
            return Response(serializer.data)

        cfile = carib.planeCapture(sfname, time,cfile)

        carObj= CaribImage.objects.create(
            cam = cam,
            fname=fname,
            time=time,
            json= {},
            cfile =camera+"/png/"+fn
        )
        carObj.save()

#        mod = CaribImage.objects.all()
        serializer = CaribSerializer(carObj)
        return Response(serializer.data)



    
# ここで react / nodeでbuild したクライアントを返せばいい   
#class indexPage(request):
#    html_template = loader
