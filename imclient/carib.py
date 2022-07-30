import numpy as np
import cv2
import glob
import yaml
import json

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

# 特定の変換を行って保存
def convCb(fplane, cbinfo, cfile):
    im = cv2.imread(fplane)
    cimg, pimg, coi = convImg2(im, cbinfo, 1)
    cv2.imwrite(cfile, pimg)
    return cfile

baseCarib = setCalibData()

def convDefaultCb(fplane, cam, cfile):
    cbinfo = baseCarib[cam]
    convCb(fplane, cbinfo, cfile)
    return cfile


def convEditCb(fplane, calib, matrix, cfile):
    cbinfo = {
        'camera_matrix':{
            'data': matrix,
        },
        'distortion_coefficients':{
            'data': calib
        }
    }
    convCb(fplane, cbinfo, cfile)
    return cbinfo

CHECKERBOARD = (5,7)

def findCheckerImg(fplane, cfile, save=True):
    print("Find Checker", fplane, cfile)
    im = cv2.imread(fplane)
    grayColor = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)

    ret, corners = cv2.findChessboardCorners(
        grayColor, CHECKERBOARD,
        cv2.CALIB_CB_ADAPTIVE_THRESH +
        cv2.CALIB_CB_FAST_CHECK +
        cv2.CALIB_CB_NORMALIZE_IMAGE
    )
    if ret == True and save:
        im2 = cv2.drawChessboardCorners(
            im, CHECKERBOARD, corners, ret
        )
        cv2.imwrite(cfile, im2)
        print("Checker Done!", cfile)
    else:
        print("Can't find checker!!")

    return ret, corners


def saveCaribFile(basefile, caribs, destfile):
    im = cv2.imread(basefile)
    cimg, pimg, coi = convImg2(im, caribs, 1)
    cv2.imwrite(destfile, pimg)


# ファイル一覧で、一気にやる！

CRITERIA = (cv2.TERM_CRITERIA_EPS+
            cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

def doCaribFiles(files):

    objp = np.zeros((5*7,3),np.float32)
    objp[:,:2] = np.mgrid[0:7,0:5].T.reshape(-1,2)
    threedpts =[]
    twodpts = []
    print("doCarib with", len(files))
    for i,fn in enumerate(files):
        im = cv2.imread(fn)
        grayColor = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
        ret, corners = cv2.findChessboardCorners(
            grayColor, CHECKERBOARD,
            cv2.CALIB_CB_ADAPTIVE_THRESH +
            cv2.CALIB_CB_FAST_CHECK +
            cv2.CALIB_CB_NORMALIZE_IMAGE
        )
        if ret:
            threedpts.append(objp)
            corners2 = cv2.cornerSubPix(
                grayColor, 
                corners,
                (11,11),(-1,-1),CRITERIA
            )
            twodpts.append(corners2)
            print("Success:",i,fn)
        else:
            print("Failed:",i,fn)
    h,w = grayColor.shape[:2]
    print("W,H",w,h)
        
    ret, matrix, distortion, r_vecs, t_vecs = cv2.calibrateCamera(
            threedpts, twodpts, grayColor.shape[::-1], None, None )

    matrix = matrix.reshape(-1).tolist()
    distortion = distortion.reshape(-1).tolist()
    print(matrix)
    print(distortion)
    print("rvec",r_vecs)
    print("tvec",t_vecs)
    
    carib = {
        "image_width": w,
        "image_height":h, 
        "camera_name": "narrow_stereo",
        "camera_matrix": {"rows":3, "cols":3, "data":matrix},
        "camera_model" : "plumb_bob",
        "distortion_coefficients": {"rows":1, "cols":5, "data":list(distortion)},
        "rectification_matrix": {},
        "projection_matrix": {},
    }
    print("Make Carib")
    print(json.dumps(carib, indent=4))

    return carib
