import cv2
from discordwebhook import Discord
import datetime
import copy

# Discord Webhook URL
discord = Discord(url="your Discord Webhook URL")

temp = cv2.imread("./pic/temp.jpg") #テンプレート画像
temp = cv2.cvtColor(temp, cv2.COLOR_BGR2GRAY) #グレイスケールに変換

capture = cv2.VideoCapture(0)
capture.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

# テンプレートマッチング
def template(img,img_color):
    h, w = temp.shape[0],temp.shape[1]
    match = cv2.matchTemplate(img, temp, cv2.TM_SQDIFF_NORMED)
    min_value, max_value, min_pt, max_pt = cv2.minMaxLoc(match)
    pt = min_pt
    temp_out = copy.deepcopy(img_color[pt[1]:pt[1]+h,pt[0]:pt[0]+w])
    # 決め打ち
    if 500<pt[0] and pt[0]<550 and 85<pt[1] and pt[1]<105 and min_value<0.1: 
        #　時空の歪みを検知
        cv2.rectangle(img_color, (pt[0], pt[1]), (pt[0] + w, pt[1] + h), (0, 200, 0), 3)
        print("detect",min_value)
        return True,img_color,temp_out
    else:
        # 時空の歪みを非検知
        cv2.rectangle(img_color, (pt[0], pt[1]), (pt[0] + w, pt[1] + h), (0, 0, 200), 3)
        return False,img_color,temp_out


if capture.isOpened() is False:
  raise IOError

while(True):
  try:
    ret, frame = capture.read()
    frame_color = copy.deepcopy(frame)
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY) # グレイスケールに変換
    if ret is False:
      raise IOError

    flag,frame_out,temp_out = template(frame,frame_color)
    
    if flag: # Discordに通知
        cv2.imwrite("./pic/frame_out.jpg", frame_out)
        cv2.imwrite("./pic/temp_out.jpg", temp_out)
        f1 = open("./pic/frame_out.jpg", 'rb')
        f2 = open("./pic/temp_out.jpg", 'rb')
        dt_now = datetime.datetime.now() # 現在時刻取得
        discord.post(content="@here 時空の歪み検知 " + dt_now.strftime('%Y年%m月%d日 %H:%M:%S'),file={"1": f1,"2": f2})

    cv2.imshow('frame',frame_out)
    cv2.waitKey(1)

  except KeyboardInterrupt:
    break

capture.release()
cv2.destroyAllWindows()
