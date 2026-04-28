import cv2
import numpy as np
from typing import Tuple, Optional
import time
from dataclasses import dataclass

#time is important!
timestamp = time.strftime("%Y%m%d_%H%M%S") + f"_{int(time.time()*1000)%1000}"

@dataclass
class ConverterConfig:
    cols: int = 120
    rows: int = 60
    char_set: str = 'custom'
    invert: bool = False
    contrast_enhance: bool = True
    edge_detect: bool = False
    color_mode: bool = False


class VideoRecorder:

    def __init__(self):
        self.writer = None
        self.is_recording = False
        self.filename = None
        self.frame_count = 0
        self.start_time = None

    def start(self, filename: str, fps: float, frame_size: Tuple[int, int], is_color: bool = False):
        self.filename = filename
        self.frame_count = 0
        self.start_time = time.time()

        codecs = [
            ('mp4v', '.mp4'),
            ('XVID', '.avi'),
            ('MJPG', '.avi'),
            ('X264', '.mp4')
        ]

        for codec, ext in codecs:
            fourcc = cv2.VideoWriter_fourcc(*codec)
            output = filename.replace('.mp4', ext).replace('.avi', ext)

            self.writer = cv2.VideoWriter(
                output,
                fourcc,
                fps,
                frame_size,
                isColor=is_color
            )

            if self.writer.isOpened():
                self.filename = output
                self.is_recording = True
                print(f"Recording started: {output} ({codec})")
                return True

        self.writer = None
        print("Video writer initialization failed")
        return False

    def write_frame(self, frame: np.ndarray):
        if self.is_recording and self.writer is not None:
            self.writer.write(frame)
            self.frame_count += 1

    def stop(self):
        if self.writer is not None:
            self.writer.release()
            duration = time.time() - self.start_time if self.start_time else 0
            print(f"Recording stopped: {self.filename}")
            print(f"Frames: {self.frame_count} | Duration: {duration:.1f}s")
            self.writer = None
            self.is_recording = False
            self.frame_count = 0
            self.start_time = None


class ASCIICameraConverter:
#unique things in between !
    CHAR_SETS = {
        'simple': " .:;+=xX$@",
        'detailed': " .'`^\",:;Il!i><~+_-?][}{1)(|\\/tfjrxnuvczXYUJCLQ0OZmwqpdbkhao*#MW&8%B@$",
        'blocks': " ░▒▓█",
        'custom': " .:/\\|!@#$%^&*",
        'binary': " █",
        'minimal': " .-+*#@"
    }

    def __init__(self, config: Optional[ConverterConfig] = None):

        self.config = config or ConverterConfig()
        self.chars = self.CHAR_SETS.get(self.config.char_set, self.CHAR_SETS['custom'])

        if self.config.invert:
            self.chars = self.chars[::-1]

        self.char_width = 8
        self.char_height = 12
        self.output_width = self.config.cols * self.char_width
        self.output_height = self.config.rows * self.char_height

        self._create_lut()

    def _create_lut(self):
        count = len(self.chars)
        self.lut = np.array([
            self.chars[min(int(i * (count - 1) / 255), count - 1)]
            for i in range(256)
        ])

    def edge(self, img):
        gx = cv2.Sobel(img, cv2.CV_64F, 1, 0, ksize=3)
        gy = cv2.Sobel(img, cv2.CV_64F, 0, 1, ksize=3)
        mag = np.sqrt(gx ** 2 + gy ** 2)
        mag = np.clip(mag, 0, 255).astype(np.uint8)
        return cv2.addWeighted(img, 0.5, mag, 0.5, 0)

    def process_frame(self, frame: np.ndarray) -> np.ndarray:

        frame = cv2.flip(frame, 1)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        if self.config.contrast_enhance:
            gray = cv2.equalizeHist(gray)

        if self.config.edge_detect:
            gray = self.edge(gray)

        small = cv2.resize(gray, (self.config.cols, self.config.rows), interpolation=cv2.INTER_AREA)

        if self.config.color_mode:
            output = np.zeros((self.output_height, self.output_width, 3), dtype=np.uint8)
            color_small = cv2.resize(frame, (self.config.cols, self.config.rows), interpolation=cv2.INTER_AREA)
        else:
            output = np.zeros((self.output_height, self.output_width), dtype=np.uint8)

        for y in range(self.config.rows):
            for x in range(self.config.cols):

                intensity = small[y, x]
                char = self.lut[intensity]
                pos = (x * self.char_width, y * self.char_height)

                if self.config.color_mode:
                    color = tuple(map(int, color_small[y, x]))
                    cv2.putText(output, char, pos, cv2.FONT_HERSHEY_SIMPLEX, 0.3, color, 1, cv2.LINE_AA)
                else:
                    cv2.putText(output, char, pos, cv2.FONT_HERSHEY_SIMPLEX, 0.3, 255, 1, cv2.LINE_AA)

        return output


class FPSCounter:

    def __init__(self, window=30):
        self.times = []
        self.last = time.time()
        self.window = window

    def update(self):
        now = time.time()
        self.times.append(now - self.last)
        self.last = now

        if len(self.times) > self.window:
            self.times.pop(0)

        avg = sum(self.times) / len(self.times)
        return 1 / avg if avg > 0 else 0


def main():

    config = ConverterConfig()
    converter = ASCIICameraConverter(config)

    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Camera error")
        return

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    fps_counter = FPSCounter()

    recorder = VideoRecorder()

    screenshots = 0
    recordings = 0

    print("ASCII Camera Started")
#so this is how you can change the unique things..!
    char_keys = {
        ord('1'): 'simple',
        ord('2'): 'detailed',
        ord('3'): 'blocks',
        ord('4'): 'custom',
        ord('5'): 'binary',
        ord('6'): 'minimal'
    }

    try:

        while True:

            ret, frame = cap.read()

            if not ret:
                break

            output = converter.process_frame(frame)

            fps = fps_counter.update()

            cv2.putText(output, f"FPS {fps:.1f}", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                        (0,255,0) if config.color_mode else 200, 1)

            if recorder.is_recording:
                rec_color = (0,0,255) if config.color_mode else 255
                cv2.circle(output,(10,60),5,rec_color,-1)

                elapsed = int(time.time()-recorder.start_time)
                cv2.putText(output,f"REC {elapsed//60:02d}:{elapsed%60:02d}",
                            (20,65),cv2.FONT_HERSHEY_SIMPLEX,
                            0.4,rec_color,1)

                recorder.write_frame(output)

            cv2.imshow("ASCII Camera", output)

            key = cv2.waitKey(1) & 0xFF

            if key == ord('q') or key == 27:
                break

            elif key == ord('s'):
               screenshots += 1
               timestamp = time.strftime("%Y%m%d_%H%M%S") + f"_{int(time.time()*1000)%1000}"
               name = f"ascii_screenshot_{timestamp}.png"
               cv2.imwrite(name, output)
               print("Saved", name)

            elif key == ord('r'):

                if recorder.is_recording:
                    recorder.stop()

                else:
                   recordings += 1
                   timestamp = time.strftime("%Y%m%d_%H%M%S") + f"_{int(time.time()*1000)%1000}"
                   name = f"ascii_recording_{timestamp}.mp4"
                   size = (converter.output_width, converter.output_height)
                   recorder.start(name, 20.0, size, config.color_mode)

            elif key == ord('c'):
                config.color_mode = not config.color_mode
                converter = ASCIICameraConverter(config)

            elif key == ord('e'):
                config.edge_detect = not config.edge_detect
                converter = ASCIICameraConverter(config)

            elif key == ord('i'):
                config.invert = not config.invert
                converter = ASCIICameraConverter(config)

            elif key in char_keys:
                config.char_set = char_keys[key]
                converter = ASCIICameraConverter(config)

            elif key == ord('+') or key == ord('='):
                config.cols = min(200, config.cols + 10)
                config.rows = min(100, config.rows + 5)
                converter = ASCIICameraConverter(config)

            elif key == ord('-') or key == ord('_'):
                config.cols = max(40, config.cols - 10)
                config.rows = max(20, config.rows - 5)
                converter = ASCIICameraConverter(config)

    finally:

        if recorder.is_recording:
            recorder.stop()

        cap.release()
        cv2.destroyAllWindows()

        print("Screenshots:", screenshots)
        print("Recordings:", recordings)


if __name__ == "__main__":
    main()
