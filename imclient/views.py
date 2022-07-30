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
import pathlib
import humanfriendly
from . import carib

from .models import ImFile, CaribImage
from .serializers import ImFileSerializer, CaribSerializer

# ビデオの基本的なディレクトリ
BASE_DIR = "/mnt/qnap104/ptokai_demo/conv_mp4/2022-05-17/"
# このディレクトリ以下に ファイル群があることを前提
# /cameraXX/+++.mp4
#          /png/****_plane.png  # キャプチャされたファイル
#          /png/****.png        # キャリブレーションされたファイル


class FileListViewSet(viewsets.ModelViewSet):
    queryset = ImFile.objects.all()
    serializer_class = ImFileSerializer



class ImageListViewSet(viewsets.ModelViewSet):
    queryset = CaribImage.objects.all()
    serializer_class = CaribSerializer

    def get_queryset(self):
        print("Got GET", self.request.GET)
#        cam = self.request.GET['cam']

        if 'fname' in self.request.GET:
            fname = self.request.GET['fname']
            return CaribImage.objects.filter(fname=fname).order_by("time")
        else:
            return CaribImage.objects.order_by("time")



class SetFileList(viewsets.ModelViewSet):
    queryset = ImFile.objects.all()
    serializer_class = ImFileSerializer

    def get_queryset(self):
#        files = glob.glob("/mnt/qnap105/gstreamer/2022/2022-05-17/cameraG?/*.mkv")
        files = glob.glob(BASE_DIR+"/camera*/*.mp4")
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


class GenPlaneFileList(APIView):
    def get(self, request, format=None):
        print("Get PlaneFileList",request)

        files = glob.glob(BASE_DIR+"/camera*/png/*_plane.png")
        for f in files:
            pobj = pathlib.Path(f)
            bname = pobj.parts[-1]
            camera = pobj.parts[-3]
            cam = camera[6:]
            tb=bname.split("_")
            mtime = float(tb[1])
            fname = tb[0]+".mp4"
            sfile = camera+"/png/"+bname
            # 
            if CaribImage.objects.filter(cfile=sfile).exists():
                continue

            carObj= CaribImage.objects.create(
                cam = cam,
                fname=fname,
                time=mtime,
                json={},
                cfile = sfile
            )
            carObj.save()

        mod = CaribImage.objects.all()
        serializer = CaribSerializer(mod)
        return Response(serializer.data)





class CaptureVideo(APIView):
#    cb = carib.setCalibData()
    cb = carib.baseCarib
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
        sfname = BASE_DIR+camera+"/"+fname
#        print("Its working", sfname)
        ff = fname.split(".")
        fd = BASE_DIR+camera+"/png/"
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
        sfname = BASE_DIR+camera+"/"+fname
#        print("Its working", sfname)
        ff = fname.split(".")
        fd = BASE_DIR+camera+"/png/"
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



# 特定のキャリブレーションファイルで、イメージをキャプチャ
class ConvImage(APIView):

    def post(self, request, format=None):
        fname0 = request.data['fname']
        conv =request.data['conv']
        num = request.data['num']
        print("Got", fname0, conv, num)

    ## ここで変換！
    ##  fname = "/static/cameraXX/png/XXXXX_plane.png"
    ##  実際には /mnt/qnap104/ptokai_demo/conv_mp4/2022-05-17 に
    ##  変換した結果は？
        fbase = fname0[len("/static/"):]
        cfn = fbase[:-len("_plane.png")]
        cfs = cfn.split("/")
        cam = cfs[0][len("camera"):]
        fname = cfs[-1].split("_")[0]+".mp4"
        cfile = BASE_DIR+cfn+"_"+conv+".png"
        rfile = BASE_DIR+fbase
        sfile = cfn+"_"+conv+".png"
        print(sfile, cfile,fname0)

        # 同じオブジェクトがあれば、それを返す
        if CaribImage.objects.filter(cfile=sfile).exists():
            qobj = CaribImage.objects.get(cfile=sfile)

            serializer = CaribSerializer(qobj)
            return Response(serializer.data)

        carib.convDefaultCb(rfile, conv, cfile)

        carObj= CaribImage.objects.create(
            cam = cam,
            fname=fname,  #ビデオの fname が必要
            time=num,  #ここは、本当の時刻じゃないことに注意！
            json= carib.baseCarib[conv],
            cfile = sfile
        )
        carObj.save()

#        mod = CaribImage.objects.all()
        serializer = CaribSerializer(carObj)
        return Response(serializer.data)


# イメージからチェッカボードを探す！
class FindChecker(APIView):

    def post(self, request, format=None):
        fname0 = request.data['fname']
        conv =request.data['conv']
        num = request.data['num']
        print("FCGot", fname0, conv, num)
        fbase = fname0[len("/static/"):]
        cfn = fbase[:-len("_plane.png")]
        cfs = cfn.split("/")
        cam = cfs[0][len("camera"):]
        fname = cfs[-1].split("_")[0]+".mp4"
        cfile = BASE_DIR+cfn+"_chkbd.png"
        rfile = BASE_DIR+fbase
        sfile = cfn+"_chkbd.png"

        if CaribImage.objects.filter(cfile=sfile).exists():
            qobj = CaribImage.objects.get(cfile=sfile)
            serializer = CaribSerializer(qobj)
            return Response(serializer.data)

        carib.findCheckerImg(rfile,cfile)

        carObj= CaribImage.objects.create(
            cam = cam,
            fname=fname,  #ビデオの fname が必要
            time=num,  #ここは、本当の時刻じゃないことに注意！
            json= {},
            cfile = sfile
        )
        carObj.save()   
        serializer = CaribSerializer(carObj)
        return Response(serializer.data)


class GenCarib(APIView):
    def post(self, request):
        videoName = request.data['fname']
        print("Got gen", videoName)
        
        # videoName(fname)が一致して、 すべての plane がある
        objs = CaribImage.objects.filter(fname=videoName,cfile__endswith='_plane.png').order_by("time")

        # 各オブジェクトに対しキャリブレーション作成
        # イメージファイルのリストを作成

        fileList = []

        for imobj in objs:
            rfile = BASE_DIR+imobj.cfile
            fileList.append(rfile)
        
        caribs = carib.doCaribFiles(fileList)

        # キャリブレーションができるか、確認してみよう！
        cfn = objs[0].cfile[:-len("_plane.png")]
        cfile = BASE_DIR+cfn+"_carib.png"        
        carib.saveCaribFile(BASE_DIR+objs[0].cfile, caribs, cfile)

        carObj= CaribImage.objects.create(
            cam = objs[0].cam,
            fname=objs[0].fname,  #ビデオの fname が必要
            time=objs[0].time, 
            json= caribs,
            cfile = cfn+"_carib.png"
        )

        carObj.save()   
        serializer = CaribSerializer(carObj)
        return Response(serializer.data)



class DoCalibImage(APIView):
    def post(self, request):
        videoName = request.data['fname']
        print("Got DoCarib", request.data)
        calib = request.data['calib']
        matrix = request.data['matrix']
        fname0 = request.data['fname']

    ## ここで変換！
    ##  fname = "/static/cameraXX/png/XXXXX_plane.png"
    ##  実際には /mnt/qnap104/ptokai_demo/conv_mp4/2022-05-17 に
    ##  変換した結果は？
        fbase = fname0[len("/static/"):]
        cfn = fbase[:-len("_plane.png")]
        cfs = cfn.split("/")
        cam = cfs[0][len("camera"):]
        fname = cfs[-1].split("_")[0]+".mp4"
        cnum = str(sum(calib))
        cfile = BASE_DIR+cfn+"_"+cnum+"_editConv.png"
        rfile = BASE_DIR+fbase

        cbinfo = carib.convEditCb(rfile, calib, matrix, cfile)

        carObj= CaribImage.objects.create(
            cam = cam,
            fname=fname,  #ビデオの fname が必要
            time=0,  #ここは、本当の時刻じゃないことに注意！
            json= cbinfo,
            cfile = cfn+"_"+cnum+"_editConv.png"
        )
        carObj.save()

        serializer = CaribSerializer(carObj)
        return Response(serializer.data)



# キャリブレーションの情報を保存する！
class SaveCalibInfo(APIView):
    def post(self, request):
        videoName = request.data['fname']
        print("Got SaveCaribInfo", request.data)
        calib = request.data['calib']
        matrix = request.data['matrix']
        fname0 = request.data['fname']

    ##  fname = "/static/cameraXX/png/XXXXX_plane.png"
    ##  実際には /mnt/qnap104/ptokai_demo/conv_mp4/2022-05-17 に
        fbase = fname0[len("/static/"):]
        cfn = fbase[:-len("_plane.png")]
        cfs = cfn.split("/")
        cam = cfs[0][len("camera"):]
        fname = cfs[-1].split("_")[0]+".mp4"
        cnum = str(sum(calib))
        cfile = BASE_DIR+cfn+"_"+cnum+"_editConv.png"
        rfile = BASE_DIR+fbase

#        cbinfo = carib.convEditCb(rfile, calib, matrix, cfile)
        cbinfo = {
            'camera_matrix':{
                'data': matrix,
            },
            'distortion_coefficients':{
                'data': calib
            }
        }

        carObj= CaribImage.objects.create(
            cam = cam,
            fname=fname,  #ビデオの fname が必要
            time=0,  #ここは、本当の時刻じゃないことに注意！
            json= cbinfo,
            cfile = cfn+"_"+cnum+"_editConv.png"
        )
        carObj.save()

        serializer = CaribSerializer(carObj)
        return Response(serializer.data)