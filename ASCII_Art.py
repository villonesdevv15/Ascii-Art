# Original Sources:
# https://www.youtube.com/watch?v=FtutLA63Cp8&ab_【東方】Bad Apple!! ＰＶ【影絵】
# Run using the run_apple.py for smooth quality preventing frame delay

import pygame
import pyautogui  
import os
import sys
import time
import cv2

# ASCII characters 
ascii_char = ' @%#*+=-:. ' # ascii_chars 
# Other ASCII char (alternative)
    # '  .,:;+*&%@#$' for Bad Apple!! feat.SEKAI (SEKAI version)
    # ' $8obdpq0L@n1+"`' for Bad Apple!! (Original version)
    # ' @%#*+=-:. ' for Honeypie MV

# Video path for capture
# Media paths (change these if needed)
video_path = "audio & video/Honeypie MV.mp4"
audio_path = "audio & video/Honeypie MV.mp3"

# Terminal output width (155 is good for full-screen terminals)
output_width = 155

# FPS override — using cap.get() was unreliable here
fps = 24    # 24 fps for sekai ver
frame_time = 1 / fps


def convert_frame_to_ascii(gray_frame, width=output_width):

    h, w = gray_frame.shape
    aspect_ratio = w / h
    new_height = int((width / aspect_ratio) * 0.5)

    resized = cv2.resize(gray_frame, (width, new_height))

    ascii_rows = []
    for row in resized:
        line = ""
        for pixel in row:
            idx = min(pixel // 25, len(ascii_char) - 1)
            line += ascii_char[idx]
        ascii_rows.append(line)

    return "\n".join(ascii_rows)


print("\033[?25l", end="")

pygame.mixer.init()
pygame.mixer.music.load(audio_path)
pygame.mixer.music.set_volume(0.1)

cap = cv2.VideoCapture(video_path)

pygame.mixer.music.play()
start_time = time.time()

frame_index = 0
first_frame = True

while cap.isOpened():
    ok, frame = cap.read()
    if not ok:
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    ascii_art = convert_frame_to_ascii(gray)

    if not first_frame:
        sys.stdout.write("\033[H")
    else:
        first_frame = False

    sys.stdout.write(ascii_art)
    sys.stdout.flush()

    frame_index += 1
    expected = start_time + (frame_index * frame_time)
    delay = expected - time.time()

    if delay > 0:
        time.sleep(delay)

cap.release()
pygame.mixer.music.stop()

print("\033[?25h", end="")

pyautogui.hotkey("f11")
