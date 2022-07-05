import numpy as np
import cv2
import glob
import yaml

#Loading Caribration files

def findImgDirs():
    files = glob.glob("./ptk1FAll_*")
    return files

def findImgFiles(fdr):
    files = glob.glob(fdr+"/ptk*")
#    for file in files:
#        print(file)
    return files

def getFirstFiles():
    fdir= findImgDirs()   
    print("Use",fdir[0])
    return findImgFiles(fdir[0])

def convImg(srcImg,calib_data):
    h,  w = srcImg.shape[:2]
    k = calib_data['camera_matrix']['data']
    d = calib_data['distortion_coefficients']['data']
    cm = np.mat(k).reshape(3,3)
    ds = np.mat(d)
    dstImg = np.ones((h, w, 3), np.uint8) * 255
    new_camera_matrix, roi = cv2.getOptimalNewCameraMatrix(cm,ds,(w, h), 1.0, (w,h))
    cv2.undistort(src=srcImg, dst=dstImg,cameraMatrix=cm,distCoeffs=ds)
    return dstImg

def convImgFile(fname,f2, calib_data):
    im = cv2.imread(fname)
    im2 = convImg(im,calib_data)
    cv2.imwrite(f2,im2)

# キャリブレーションファイルを読み込む
def parse_yaml(filename):
  with open(filename, 'r') as stream:
    calib_data = yaml.safe_load(stream)
    return calib_data

# キャリブレーションファイルとの対応づけを読み込む
def setCalibData():
    calibs={}
    cf = glob.glob("/home/kawaguti/work2022/ptokai_video_proc/calibration_files/*/ost.yaml")
#    print("Carib!",len(cf))
    for x in cf:
        cs = x.split("/")
        c = cs[-2][0]
        m = cs[-2][1:]
#        if len(m) == 1:
#            m = "0"+m
#        print(c,m,x)       
        calibs[""+c+m]=parse_yaml(x)
    return calibs

# 黒のところを透過に（周辺以外も透過になっちゃうので、要検討）
def convImgPng(img,roi):
#    h,  w = srcImg.shape[:2]
#    dstImg = np.ones((h, w, 4), np.uint8) 
    c_blue , c_green , c_red = cv2.split(img)
    gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    mg = np.ma.masked_where(gray > 0,gray )
    mg.set_fill_value(255)
    g2 = mg.filled()
    x0,y0,xd,yd=roi
    g3 = cv2.rectangle(g2, (x0,y0),(x0+xd,y0+yd),255,-1) #少なくとも　roi は、透過させない
    dstImg = cv2.merge([c_blue,c_green, c_red, g2])
    return dstImg    

# 透過付きの distortion

def convImg2(srcImg,calib_data,alpha):
    h,  w = srcImg.shape[:2]
    k = calib_data['camera_matrix']['data']
    d = calib_data['distortion_coefficients']['data']
    cm = np.mat(k).reshape(3,3)
    ds = np.mat(d)

#    dstImg = np.ones((h, w, 3), np.uint8) * 255
    new_camera_matrix, roi = cv2.getOptimalNewCameraMatrix(cm,ds,(w, h), alpha, newImgSize=(w,h))
    cimg = cv2.undistort(src=srcImg,cameraMatrix=cm,distCoeffs=ds,newCameraMatrix=new_camera_matrix )
    dimg = convImgPng(cimg,roi)
    return cimg,dimg,roi

def capAndCarib(fn, time, cbinfo, cfile):
    
    cap = cv2.VideoCapture(fn)
    fps = cap.get(cv2.CAP_PROP_FPS)
    cap.set(cv2.CAP_PROP_POS_FRAMES, int(time * fps))
    tf, im = cap.read()
    if not tf:
        print("Can't carib image on ", fn)
        return None
    cimg, pimg, roi =convImg2(im, cbinfo, 1)
    cv2.imwrite(cfile, pimg)
#    fimg = cv2.imencode(".png", pimg)[1]
#    print("OK. caribrated", len(fimg), type(fimg))
    cap.release()
    return cfile

# 特定の時間でキャプチャする
def planeCapture(fn, time, cfile):
    cap = cv2.VideoCapture(fn)
    fps = cap.get(cv2.CAP_PROP_FPS)
    cap.set(cv2.CAP_PROP_POS_FRAMES, int(time * fps))
    tf, im = cap.read()
    if not tf:
        print("Can't carib image on ", fn)
        return None
    cv2.imwrite(cfile, im)
    cap.release()
    return cfile