import cv2
import mediapipe as mp
import numpy as np
import math
import tkinter as tk
import time

mp_hands = mp.solutions.hands

def distance(p1, p2):
    return math.sqrt((p1.x - p2.x)**2 + (p1.y - p2.y)**2)


class HandPaint:

    def __init__(self):

        self.cap = cv2.VideoCapture(0)

        if not self.cap.isOpened():
            print("Camera not detected")
            exit()

        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH,1280)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT,720)

        root = tk.Tk()
        self.screen_width = root.winfo_screenwidth()
        self.screen_height = root.winfo_screenheight()
        root.destroy()

        self.cam_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.cam_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        self.hands = mp_hands.Hands(
            max_num_hands=1,
            min_detection_confidence=0.6,
            min_tracking_confidence=0.6
        )

        self.canvas = np.zeros((self.screen_height,self.screen_width,3),dtype=np.uint8)

        self.history = []
        self.current_path = None

        self.smoothed_x = None
        self.smoothed_y = None
        self.smoothing_alpha = 0.35

        self.erase_mode = False
        self.brush_size = 5

        self.colors = [
            (0,255,255),
            (255,0,0),
            (0,255,0),
            (0,0,255),
            (255,255,0),
            (255,255,255),
            (255,0,255),
            (0,165,255),
            (255,192,203)
        ]

        self.current_color_idx = 0
        self.brush_color = self.colors[self.current_color_idx]

        self.prev_draw = False
        self.prev_clear = False
        self.prev_erase = False
        self.prev_color = False

        self.clear_start = None
        self.color_start = None

        self.save_message_start = None
        self.save_filename = None

        self.pinch_threshold_factor = 0.25

    def redraw_canvas(self):

        self.canvas = np.zeros((self.screen_height,self.screen_width,3),dtype=np.uint8)

        for path in self.history:

            color = path['color']
            size = path['size']
            pts = path['points']

            for i in range(1,len(pts)):
                cv2.line(self.canvas,pts[i-1],pts[i],color,size)

    def save_canvas(self):

        self.save_filename = time.strftime("drawing_%Y%m%d_%H%M%S.png")
        cv2.imwrite(self.save_filename,self.canvas)
        self.save_message_start = time.time()

        print("Saved:",self.save_filename)

    def draw_ui(self,frame):

        overlay = frame.copy()

        cv2.rectangle(overlay,(0,0),(500,240),(0,0,0),-1)

        frame = cv2.addWeighted(overlay,0.6,frame,0.4,0)

        lines = [
        "Thumb + Index  : Draw / Erase",
        "Thumb + Middle : Undo",
        "Hold >1s       : Clear Canvas",
        "Thumb + Ring   : Toggle Erase",
        "Thumb + Pinky  : Change Color",
        "Hold >1s       : Save Image",
        "Press Q        : Quit"
        ]

        y = 30

        for line in lines:
            cv2.putText(frame,line,(15,y),
            cv2.FONT_HERSHEY_SIMPLEX,0.65,(255,255,255),2)
            y+=30

        return frame

    def resize_with_ratio(self,frame):

        cam_ratio = self.cam_width/self.cam_height
        screen_ratio = self.screen_width/self.screen_height

        if cam_ratio > screen_ratio:
            new_width = self.screen_width
            new_height = int(self.screen_width/cam_ratio)
        else:
            new_height = self.screen_height
            new_width = int(self.screen_height*cam_ratio)

        resized = cv2.resize(frame,(new_width,new_height))

        display = np.zeros((self.screen_height,self.screen_width,3),dtype=np.uint8)

        x = (self.screen_width-new_width)//2
        y = (self.screen_height-new_height)//2

        display[y:y+new_height,x:x+new_width] = resized

        return display

    def run(self):

        print("\nGesture Paint Started\n")

        cv2.namedWindow("Hand Paint",cv2.WINDOW_NORMAL)
        cv2.setWindowProperty("Hand Paint",cv2.WND_PROP_FULLSCREEN,cv2.WINDOW_FULLSCREEN)

        while True:

            ret,frame = self.cap.read()
            if not ret:
                continue

            frame = cv2.flip(frame,1)

            rgb = cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)
            results = self.hands.process(rgb)

            frame_display = self.resize_with_ratio(frame)

            draw_pinch=False
            clear_pinch=False
            erase_pinch=False
            color_pinch=False

            if results.multi_hand_landmarks:

                hand = results.multi_hand_landmarks[0]

                index_tip = hand.landmark[8]
                thumb_tip = hand.landmark[4]
                middle_tip = hand.landmark[12]
                ring_tip = hand.landmark[16]
                pinky_tip = hand.landmark[20]

                wrist = hand.landmark[0]
                middle_base = hand.landmark[9]

                x_raw = index_tip.x*self.screen_width
                y_raw = index_tip.y*self.screen_height

                if self.smoothed_x is None:

                    self.smoothed_x = x_raw
                    self.smoothed_y = y_raw

                else:

                    self.smoothed_x = self.smoothing_alpha*x_raw+(1-self.smoothing_alpha)*self.smoothed_x
                    self.smoothed_y = self.smoothing_alpha*y_raw+(1-self.smoothing_alpha)*self.smoothed_y

                x = int(self.smoothed_x)
                y = int(self.smoothed_y)

                hand_size = distance(wrist,middle_base)
                threshold = hand_size*self.pinch_threshold_factor

                draw_pinch = distance(index_tip,thumb_tip)<threshold
                clear_pinch = distance(middle_tip,thumb_tip)<threshold
                erase_pinch = distance(ring_tip,thumb_tip)<threshold
                color_pinch = distance(pinky_tip,thumb_tip)<threshold

                if not self.prev_erase and erase_pinch:
                    self.erase_mode = not self.erase_mode

                if clear_pinch:

                    if not self.prev_clear:
                        self.clear_start=time.time()

                    elif self.clear_start is not None and time.time() - self.clear_start > 1:

                        self.canvas=np.zeros((self.screen_height,self.screen_width,3),dtype=np.uint8)
                        self.history=[]
                        self.clear_start=None

                else:

                    if self.prev_clear and self.clear_start:

                        if time.time()-self.clear_start<1:

                            if self.history:
                                self.history.pop()
                                self.redraw_canvas()

                    self.clear_start=None

                if color_pinch:

                    if not self.prev_color:
                        self.color_start=time.time()

                    elif self.color_start is not None and time.time() - self.color_start > 1:

                        self.save_canvas()
                        self.color_start=None

                else:

                    if self.prev_color and self.color_start:

                        if time.time()-self.color_start<1:

                            self.current_color_idx=(self.current_color_idx+1)%len(self.colors)
                            self.brush_color=self.colors[self.current_color_idx]

                    self.color_start=None

                if draw_pinch:

                    if self.current_path is None:

                        color=(0,0,0) if self.erase_mode else self.brush_color

                        self.current_path={'color':color,'size':self.brush_size,'points':[]}

                    point=(x,y)

                    self.current_path['points'].append(point)

                    pts=self.current_path['points']

                    if len(pts)>1:
                        cv2.line(self.canvas,pts[-2],pts[-1],self.current_path['color'],self.current_path['size'])

                else:

                    if self.current_path and self.current_path['points']:
                        self.history.append(self.current_path)

                    self.current_path=None

            frame_display=cv2.addWeighted(frame_display,0.25,self.canvas,0.75,0)

            frame_display=self.draw_ui(frame_display)

            cv2.rectangle(frame_display,(self.screen_width-140,20),(self.screen_width-20,80),(50,50,50),-1)

            cv2.circle(frame_display,(self.screen_width-80,50),18,self.brush_color,-1)

            cv2.putText(frame_display,"COLOR",(self.screen_width-135,100),
            cv2.FONT_HERSHEY_SIMPLEX,0.6,(255,255,255),1)

            if self.erase_mode:

                cv2.putText(frame_display,"ERASE MODE",
                (self.screen_width-200,140),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0,0,255),
                2)

            if self.save_message_start and time.time()-self.save_message_start<3:

                overlay=frame_display.copy()

                cv2.rectangle(overlay,
                (self.screen_width//2-250,self.screen_height-120),
                (self.screen_width//2+250,self.screen_height-60),
                (0,0,0),-1)

                frame_display=cv2.addWeighted(overlay,0.7,frame_display,0.3,0)

                cv2.putText(frame_display,
                f"Saved: {self.save_filename}",
                (self.screen_width//2-220,self.screen_height-80),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.9,
                (0,255,0),
                2)

            cv2.imshow("Hand Paint",frame_display)

            key=cv2.waitKey(1)&0xFF

            if key==ord('q'):
                break

            if key==ord('s'):
                self.save_canvas()

            self.prev_draw=draw_pinch
            self.prev_clear=clear_pinch
            self.prev_erase=erase_pinch
            self.prev_color=color_pinch

        self.cap.release()
        cv2.destroyAllWindows()


if __name__=="__main__":
    HandPaint().run()