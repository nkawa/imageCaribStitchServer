from django.db import models
import json
import glob
# Create your models here.


# 画像1枚ごとのモデル。キャリブレーションデータも含む
class CaribImage(models.Model):
    caribName = models.CharField(max_length=10)    #カメラ名
    caribFile = models.CharField(max_length=256)  #キャリブレーションファイル名
    caribJson = models.JSONField()  #キャリブレーションファイル


# 画面上への画像の配置
class ImagePos(models.Model):
    locx = models.SmallIntegerField()
    locy = models.SmallIntegerField()
    angle = models.FloatField()
    scale = models.FloatField()
    

# 1枚のシーン（複数の画像）
class ImScene(models.Model):
    scene = models.IntegerField()

class ImFile(models.Model):
    fname = models.CharField(max_length=255)
    fsize = models.IntegerField()
    fhuman = models.CharField(max_length=20, default="0")
    fdate = models.DateTimeField()
    def __str__(self):
        return self.fname


# ディレクトリを保存する
class FileDir(models.Model):
    dirName = models.CharField(max_length=255)
    fileList = models.JSONField()
    count = models.IntegerField()
    def __str__(self):
        return self.dirName+":{:d}".format(self.count)

def createFileDir(dirName):
    fn = glob.glob(dirName)
    js = json.dumps(fn)
    FileDir(dirName = dirName, fileList = js, count = len(fn))
