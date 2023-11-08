from pyautogui import screenshot as pyautogui_screenshot
from pyautogui import press as pyautogui_press
from pyautogui import locateOnScreen as pyautogui_locateOnScreen
from pyautogui import pixel as pyautogui_pixel


import threading
import cv2
import numpy as np
import time
import win32gui
import win32api
import datetime
import configparser
import win32con
import os

"""
mode

0 : keep
1 : sell
"""
mode = 0

activate = False

# 960 x 540
# 화면 크기관련 세팅
right = 960
bot = 540

def checkBlueStack():
    try:
        return win32gui.FindWindow(None, 'BlueStacks App Player')
    except:
        return False
        
hwnd = checkBlueStack()

if hwnd: 
    win32gui.SetWindowPos(hwnd , win32con.HWND_TOP , 0 ,0 , right, bot , True)


# 현재 마우스값 받아낼 변수
mouse_x = 0
mouse_y = 0 

screen = None

active_mouse_x = 0
active_mouse_y = 0 

active_x_offset = 30
active_y_offset = 60

sensitive = 0.7

# 전에 세팅된 마우스 포지션값 불러오기 
configSection= 'config'
config = configparser.ConfigParser()
config.read('config.ini')

# window name
windowName = "Enjoy Fish Bot"

# Fish Grade Color
trash = (228 , 224 , 197)
green = (163 , 228 , 103)
blue  = (89  , 168 , 217)
purple = (231 , 147 ,232)

try:
    config.add_section(configSection)
    
except configparser.DuplicateSectionError: 
    pass


if config.has_option(configSection , 'active_mouse_x'):
    active_mouse_x = int(config.get(configSection , 'active_mouse_x'))
if config.has_option(configSection , 'active_mouse_y'):
    active_mouse_y = int(config.get(configSection , 'active_mouse_y'))

if config.has_option(configSection , 'mode'):
    mode = int(config.get(configSection , 'mode'))

if config.has_option(configSection , 'x_offset'):
    active_x_offset = int(config.get(configSection , 'x_offset'))

if config.has_option(configSection , 'y_offset'):
    active_y_offset = int(config.get(configSection , 'y_offset'))  

if config.has_option(configSection , 'sensitive'):
    sensitive = float(config.get(configSection , 'sensitive'))  


def mouse_event(event, x, y, flags, param):
    global mouse_x 
    global mouse_y
    global active_mouse_x 
    global active_mouse_y
    global ix, iy, drawing, screen

    mouse_x = x
    mouse_y = y

    if event == cv2.EVENT_LBUTTONUP:
        active_mouse_x = mouse_x
        active_mouse_y = mouse_y

        # pyautogui.screenshot("venv\img\catch_diff.png", region = (active_mouse_x - active_x_offset , active_mouse_y - active_y_offset , active_x_offset * 2 , active_y_offset * 2) )


def textBox(text , y ):
    font_scale = 1.8
    font = cv2.FONT_HERSHEY_PLAIN

    rectangle_bgr = (255, 255, 255)
    text = text
    (text_width, text_height) = cv2.getTextSize(text, font, fontScale=font_scale, thickness=1)[0]
    text_offset_x = 5
    text_offset_y = screen.shape[0] - y
    box_coords = ((text_offset_x, text_offset_y), (text_offset_x + text_width + 2, text_offset_y - text_height - 2))
    cv2.rectangle(screen, box_coords[0], box_coords[1], rectangle_bgr, cv2.FILLED)
    cv2.putText(screen, text, (text_offset_x, text_offset_y), font, fontScale=font_scale, color=(0, 0, 0), thickness=2)




def fisher():

    global screen
    global activate
    global hwnd
    global sensitive
    global mode

    cv2.namedWindow(windowName)
    cv2.moveWindow(windowName, right, 0)
    cv2.setMouseCallback(windowName , mouse_event)


    while True:
        screen = pyautogui_screenshot(region=(0, 0, right, bot))
        screen = np.array(screen)
        screen = cv2.cvtColor(screen , cv2.COLOR_RGB2BGR)

        # 마우스 커서
        cv2.rectangle(screen, (mouse_x - active_x_offset , mouse_y - active_y_offset), ( mouse_x + active_x_offset , mouse_y + active_y_offset), (255, 255, 255), 1)

        if mode == 0 :
            textBox("Mode : keep" , 490 )
        elif mode == 1:
            textBox("Mode : sell" , 490 )

        if activate: 
            textBox("Active : on"  , 515 )
        else : 
            textBox("Active : off"  , 515 )

        textBox("sensitive : " + str(sensitive)  , 465 )

        if active_mouse_x > 0 :

            template_area = pyautogui_screenshot( region = (active_mouse_x - active_x_offset , active_mouse_y - active_y_offset , active_x_offset * 2 , active_y_offset * 2) )
            template_area = np.array(template_area)
            template_area = cv2.cvtColor(template_area , cv2.COLOR_BGR2GRAY)

            # 실시간 이미지 체크
            # cv2.imwrite("venv\img\catch_area.png" , template_area)

            # 선택된 영역 보여주기
            cv2.rectangle(screen, 
                        (active_mouse_x - active_x_offset , active_mouse_y - active_y_offset), 
                        ( active_mouse_x + active_x_offset , active_mouse_y + active_y_offset), 
                        (0, 0, 153), 
                        3 )
                    

            if activate : 
                day_image = cv2.imread(os.path.join(os.getcwd() , "img" , "day_gray.png"))
                night_image = cv2.imread(os.path.join(os.getcwd() , "img" , "knight_gray.png"))

                day_template = cv2.cvtColor(day_image , cv2.COLOR_BGR2GRAY)
                night_template = cv2.cvtColor(night_image , cv2.COLOR_BGR2GRAY)

                result_day = cv2.matchTemplate(
                    image=template_area,
                    templ=day_template,
                    method=cv2.TM_CCOEFF_NORMED)

                result_night = cv2.matchTemplate(
                    image=template_area,
                    templ=night_template,
                    method=cv2.TM_CCOEFF_NORMED)

                _ , max_day , _, maxloc = cv2.minMaxLoc(result_day)
                _ , max_night , _, maxloc = cv2.minMaxLoc(result_night)

                textBox("day match : " + str(max_day) , 10)
                textBox("night match : " + str(max_night) , 30 )

                if max_day >= sensitive : 
                    pyautogui_press('c') # Catch
                    
                    # name = "venv\img\log\catch_day_" + str(datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')) + ".png"
                    # pyautogui_screenshot( name , region = (active_mouse_x - active_x_offset , active_mouse_y - active_y_offset , active_x_offset * 2 , active_y_offset * 2))

                    print("day catch" , datetime.datetime.now() , "---" , max_day)
                    time.sleep(1)
                
                if max_night >= sensitive : 
                    pyautogui_press('c') # Catch

                    # name = "venv\img\log\catch_night_" + str(datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')) + ".png"
                    # pyautogui_screenshot( name , region = (active_mouse_x - active_x_offset , active_mouse_y - active_y_offset , active_x_offset * 2 , active_y_offset * 2))

                    print("night catch" , datetime.datetime.now() , "---" , max_night)
                    time.sleep(1)


        cv2.imshow(windowName ,screen)

        f1_key = win32api.GetAsyncKeyState(0x70)
        f2_key = win32api.GetAsyncKeyState(0x71)
        f3_key = win32api.GetAsyncKeyState(0x72)
        f4_key = win32api.GetAsyncKeyState(0x73)
        f5_key = win32api.GetAsyncKeyState(0x74)

        add_key = win32api.GetAsyncKeyState(0x6B)
        subtract_key = win32api.GetAsyncKeyState(0x6D)
        
        if add_key and add_key == -32768 :
            if sensitive > 0.9:
                pass
            else:
                sensitive += 0.05
                sensitive = round(sensitive , 2)

        if subtract_key and subtract_key == -32768 :
            if sensitive < 0.45:
                pass
            else:
                sensitive -= 0.05
                sensitive = round(sensitive , 2)

        if f1_key :
            activate = not activate
            time.sleep(0.5)

        if f2_key: 
            mode = 0 
        if f3_key:
            mode = 1
        if f5_key:
            mode = 2

        key = cv2.waitKey(1)

        if f4_key or cv2.getWindowProperty(windowName, cv2.WND_PROP_VISIBLE ) <1:  
            with open('config.ini', 'w') as configfile:

                # -----------------------------------------------------------
                config.set(configSection, "active_mouse_x" , str(active_mouse_x))
                config.set(configSection, "active_mouse_y" ,  str(active_mouse_y))
                # -----------------------------------------------------------
                config.set(configSection , "mode" , str(mode))
                # -----------------------------------------------------------
                config.set(configSection , "sensitive" , str(sensitive))

                config.write(configfile)
            break
    


def status_checker():
    global activate

    while True:
        if activate:

            hwnd = checkBlueStack()

            if hwnd: 
                win32gui.SetWindowPos(hwnd , win32con.HWND_TOP , 0 ,0 , right, bot , True)
                win32gui.SetForegroundWindow(hwnd)
            
            is_MainScreen = pyautogui_locateOnScreen(os.path.join(os.getcwd() , "img" , "main.png"), region=((0 , 0 , right , bot)) , confidence=0.7)
            is_CatchAfter = pyautogui_locateOnScreen(os.path.join(os.getcwd() , "img" , "catch_after.png"), region=((0 , 0 , right , bot)) , confidence=0.7)
            is_Recycle = pyautogui_locateOnScreen(os.path.join(os.getcwd() , "img" , "recycle.png"), region=((0 , 0 , right , bot)) , confidence=0.7 )

            print("Check main!")

            if is_MainScreen :
                print("is_MainScreen!")
                pyautogui_press('f')
                time.sleep(3)

                # refish and check repair
                is_Repiar = pyautogui_locateOnScreen(os.path.join(os.getcwd() , "img" , "repiar.png"), region=((0 , 0 , right , bot)) , confidence=0.7)
                if is_Repiar :
                    print("is_Repiar!")
                    pyautogui_press('r')
                    time.sleep(3)
                    pyautogui_press('r')

            if is_CatchAfter :
                print("is_CatchAfter!")
                
                # keep
                if mode == 0: 
                    pyautogui_press('k')
                    time.sleep(0.1)
                
                # sell
                if mode == 1:
                    pyautogui_press('p')
                    time.sleep(0.1)
                    pyautogui_press('p')
                    time.sleep(0.1)
                    pyautogui_press('p')
                    time.sleep(0.1)
                    pyautogui_press('r')
                    time.sleep(0.1)
                    pyautogui_press('r')

            if is_Recycle : 

                print("is_Recycle!")
                pyautogui_press('p')

        time.sleep(3)


def main():
    fishThread = threading.Thread(target=fisher)

    statusCheckerThread = threading.Thread(target=status_checker)
    statusCheckerThread.daemon = True

    fishThread.start()
    statusCheckerThread.start()


if __name__ == "__main__":
	main()