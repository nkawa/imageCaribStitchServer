from django.shortcuts import render
# Create your views here.
from django.contrib.auth.models import User, Group
#from yaml import serialize
from imclient.serializers import ImFileSerializer
from rest_framework import viewsets
from rest_framework import permissions
from rest_framework.authentication import TokenAuthentication

# for file listing
import glob
import os
import logging
import datetime
import humanfriendly


from .models import ImFile
from .serializers import ImFileSerializer

class FileListViewSet(viewsets.ModelViewSet):
    queryset = ImFile.objects.all()
    serializer_class = ImFileSerializer

class SetFileList(viewsets.ModelViewSet):
    queryset = ImFile.objects.all()
    serializer_class = ImFileSerializer

    def get_queryset(self):
        files = glob.glob("/mnt/qnap105/gstreamer/2022/2022-05-17/cameraG?/*.mkv")
    ## ここでモデルとして、ファイル一覧を登録する？
    ## 特定のフォルダで、ファイル一覧を登録するよう感じがいいかも。
    ## ImFile オブジェクトを追加する
#        logging.debug("Coming here!! len:",len(files))
        for f in files:
            ff = os.stat(f).st_ctime
            #ファイル名、ディレクトリ名でわけたほうが良さそうだね。（どっち側でやるか、って話はあるか）
            fsize = os.path.getsize(f)
            human = humanfriendly.format_size(fsize)
            ImFile.objects.create(fname=f,fsize=fsize, fhuman = human ,fdate=datetime.datetime.fromtimestamp(ff,datetime.timezone(datetime.timedelta(hours=0),'JST')))
        
        return ImFile.objects.all()


    
# ここで react / nodeでbuild したクライアントを返せばいい   
#class indexPage(request):
#    html_template = loader
