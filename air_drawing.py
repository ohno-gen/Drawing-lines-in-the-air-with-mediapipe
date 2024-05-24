from xml.sax import SAXNotRecognizedException
import cv2
import mediapipe as mp
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

# landmarkの繋がり表示用
landmark_line_ids = [ 
    (0, 1), (1, 5), (5, 9), (9, 13), (13, 17), (17, 0),  # 掌
    (1, 2), (2, 3), (3, 4),         # 親指
    (5, 6), (6, 7), (7, 8),         # 人差し指
    (9, 10), (10, 11), (11, 12),    # 中指
    (13, 14), (14, 15), (15, 16),   # 薬指
    (17, 18), (18, 19), (19, 20),   # 小指
]

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    max_num_hands=2,                # 最大検出数
    min_detection_confidence=0.7,   # 検出信頼度
    min_tracking_confidence=0.7     # 追跡信頼度
)


cap = cv2.VideoCapture(0)   # カメラのID指定
#ウィンドウの名前を設定
#cv2.namedWindow("img", cv2.WINDOW_NORMAL)

#データの初期化
pt = {}
remenberpt={}
remenberpt[0]=1
m = 0
n = 0
count=1
ishand=True
isstart=False
iscolor=True
colorN=0
x=0
y=0
z=0
SizeX=640
SizeY=500
if cap.isOpened():
    while True:
        # カメラから画像取得
        success, img = cap.read()
        #サイズ変更
        #img = cv2.resize(img, (SizeX, SizeY))  
        h,w=img.shape[:2]
        if not success:
            continue
        img = cv2.flip(img, 1)          # 画像を左右反転
        img_h, img_w, _ = img.shape     # サイズ取得


        # 検出処理の実行
        results = hands.process(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        if results.multi_hand_landmarks:
            # 検出した手の数分繰り返し
            for h_id, hand_landmarks in enumerate(results.multi_hand_landmarks):


                # 検出情報をテキスト出力
                # - テキスト情報を作成
                hand_texts = []
                for c_id, hand_class in enumerate(results.multi_handedness[h_id].classification):
                    hand_texts.append("#%d-%d" % (h_id, c_id)) 
                    hand_texts.append("- Index:%d" % (hand_class.index))
                    hand_texts.append("- Label:%s" % (hand_class.label))
                    hand_texts.append("- Score:%3.2f" % (hand_class.score * 100))
                #手をパーにしたときに線をクリア
                if hand_landmarks.landmark[8].y<hand_landmarks.landmark[5].y and hand_landmarks.landmark[12].y<hand_landmarks.landmark[9].y and hand_landmarks.landmark[16].y<hand_landmarks.landmark[13].y and hand_landmarks.landmark[20].y<hand_landmarks.landmark[17].y:
                    pt.clear()
                    remenberpt.clear()
                    remenberpt[0]=1
                    m = 0
                    n = 0
                    count=1
                    ishand=True
                    isstart=False
                
                if hand_landmarks.landmark[4].x<hand_landmarks.landmark[3].x:
                    if isstart==True:
                        if ishand==True:
                            #手の形が変わる前の人差し指の座標を記録しているpt配列の番号を記録
                            remenberpt[count]=m+1
                            #手の形が変わったらカウントup
                            count=count+1
                            
                        ishand=False
                #人差し指を立てて線を書く
                elif hand_landmarks.landmark[8].y<hand_landmarks.landmark[5].y and hand_landmarks.landmark[12].y>hand_landmarks.landmark[9].y and hand_landmarks.landmark[16].y>hand_landmarks.landmark[13].y and hand_landmarks.landmark[20].y>hand_landmarks.landmark[17].y: #and hand_landmarks.landmark[4].y>hand_landmarks.landmark[8].y:
                    #人差し指の座標にを取得
                    landmarksX =hand_landmarks.landmark[8].x
                    landmarksY =hand_landmarks.landmark[8].y
                    #正規化された座標をもとに戻す
                    lx=int(landmarksX*img_w)
                    ly=int(landmarksY*img_h)
                    m=n
                    pt[n]=(lx,ly)
                    n=n+1
                    ishand=True
                    isstart=True
                    
                #カラーチェンジ、手を人差し指と親指を立てて、左に人差し指を向けて親指を上に立てるとできる
                if hand_landmarks.landmark[4].y<hand_landmarks.landmark[8].y and hand_landmarks.landmark[4].x>hand_landmarks.landmark[8].x:
                    if iscolor==True:
                        #赤
                        if colorN==0:
                            x=255
                            y=0
                            z=0
                            colorN=colorN+1
                        #黄色
                        elif colorN==1:
                            x=255
                            y=255
                            z=0
                            colorN=colorN+1
                        #緑
                        elif colorN==2:
                            x=0
                            y=255
                            z=0
                            colorN=colorN+1
                        #水色
                        elif colorN==3:
                            x=0
                            y=255
                            z=255
                            colorN=colorN+1
                        #青
                        elif colorN==4:
                            x=0
                            y=0
                            z=255
                            colorN=colorN+1
                        #ピンク
                        elif colorN==5:
                            x=255
                            y=0
                            z=255
                            colorN=colorN+1
                        #クロ
                        elif colorN==6:
                            x=0
                            y=0
                            z=0
                            colorN=0
                        
                        iscolor=False
                elif hand_landmarks.landmark[4].y>hand_landmarks.landmark[8].y and hand_landmarks.landmark[4].x<hand_landmarks.landmark[8].x:
                    iscolor=True
                
                
                
        #現在指定されている線の色を左上に表示
        cv2.circle(img,(20,20),10,(x,y,z),-1)

        #線を書く
        if n >= 1:
            if ishand==True:
                cv2.circle(img,pt[m],10,(x,y,z),-1)
        if n >= 2:
            if count==1:
                for i in range(1, n):
                    cv2.line(img, pt[i - 1], pt[i], (x, y, z), 10)
            if count>1:
            #線が手の形を書き終えてから別の場所にまた新たに書けるように手の形を変えた分でけ表示
                for roop in range(1,count+1):      
                    if roop==count:
                        for i in range(remenberpt[roop-1]+1, n):
                            cv2.line(img, pt[i-1], pt[i], (x, y, z), 10)
                    else:
                        for i in range(remenberpt[roop-1]+1, remenberpt[roop]):  
                            cv2.line(img, pt[i-1], pt[i], (x, y, z), 10)
        # 画像の表示
        cv2.imshow("MediaPipe Hands", img)
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q') or key == ord('Q') or key == 0x1b:
            break
        k = cv2.waitKey(1)
        #画像を保存
        if k == ord("s"):
            print(">>> Save Image and Coordinates.")
            path = "photo.jpg"
            cv2.imwrite(path,img)

            

cap.release()