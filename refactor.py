import argparse
import sys
import time
from pathlib import Path

import cv2
import pygame

# Characters ramp
CHARSETS = {
    "original": ' $8obdpq0L@n1+"`',   # Bad Apple!! (original)
    "sekai": '  .,:;+*&%@#$',         # Bad Apple!! feat. SEKAI
    "honeypie": ' @%#*+=-:. ',        # Honeypie MV
}

HIDE_CURSOR = "\033[?25l"
SHOW_CURSOR = "\033[?25h"
CURSOR_HOME = "\033[H"


class AsciiVideoPlayer:

    def __init__(self, video_path, audio_path, charset="original",
                 width=155, fps=30, volume=0.1):
        self.video_path = Path(video_path)
        self.audio_path = Path(audio_path)
        self.chars = CHARSETS.get(charset, charset)  # allow a custom string too
        self.width = width
        self.fps = fps
        self.frame_time = 1 / fps
        self.volume = volume
        self.cap = None

    def _validate_paths(self):
        if not self.video_path.exists():
            raise FileNotFoundError(f"Video file not found: {self.video_path}")
        if not self.audio_path.exists():
            raise FileNotFoundError(f"Audio file not found: {self.audio_path}")

    def _frame_to_ascii(self, gray_frame):
        h, w = gray_frame.shape
        aspect_ratio = w / h
        new_height = max(1, int((self.width / aspect_ratio) * 0.5))

        resized = cv2.resize(gray_frame, (self.width, new_height))

        bucket_count = len(self.chars)
        # Vectorized bucket lookup instead of a nested Python loop per pixel
        indices = (resized // 25).clip(0, bucket_count - 1)
        rows = ["".join(self.chars[i] for i in row) for row in indices]
        return "\n".join(rows)

    def _init_audio(self):
        pygame.mixer.init()
        pygame.mixer.music.load(str(self.audio_path))
        pygame.mixer.music.set_volume(self.volume)

    def run(self):
        self._validate_paths()
        self.cap = cv2.VideoCapture(str(self.video_path))
        if not self.cap.isOpened():
            raise IOError(f"Could not open video: {self.video_path}")

        self._init_audio()

        sys.stdout.write(HIDE_CURSOR)
        sys.stdout.flush()

        try:
            pygame.mixer.music.play()
            start_time = time.time()
            frame_index = 0
            first_frame = True

            while self.cap.isOpened():
                ok, frame = self.cap.read()
                if not ok:
                    break

                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                ascii_art = self._frame_to_ascii(gray)

                if not first_frame:
                    sys.stdout.write(CURSOR_HOME)
                first_frame = False

                sys.stdout.write(ascii_art)
                sys.stdout.flush()

                frame_index += 1
                expected = start_time + (frame_index * self.frame_time)
                delay = expected - time.time()
                if delay > 0:
                    time.sleep(delay)
        finally:
            self._cleanup()

    def _cleanup(self):
        if self.cap is not None:
            self.cap.release()
        pygame.mixer.music.stop()
        pygame.mixer.quit()
        sys.stdout.write(SHOW_CURSOR)
        sys.stdout.flush()


def parse_args():
    parser = argparse.ArgumentParser(description="Play a video as ASCII art in the terminal.")
    parser.add_argument("-v", "--video", required=True, help="Path to the video file")
    parser.add_argument("-a", "--audio", required=True, help="Path to the audio file")
    parser.add_argument(
        "-c", "--charset", default="original",
        help=f"Named charset ({', '.join(CHARSETS)}) or a custom ramp string, dark to light",
    )
    parser.add_argument("-w", "--width", type=int, default=155, help="Output width in columns")
    parser.add_argument("--fps", type=int, default=30, help="Target playback FPS")
    parser.add_argument("--volume", type=float, default=0.1, help="Audio volume (0.0-1.0)")
    return parser.parse_args()


def main():
    args = parse_args()
    player = AsciiVideoPlayer(
        video_path=args.video,
        audio_path=args.audio,
        charset=args.charset,
        width=args.width,
        fps=args.fps,
        volume=args.volume,
    )
    try:
        player.run()
    except (FileNotFoundError, IOError) as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nPlayback interrupted.", file=sys.stderr)
        sys.exit(0)


if __name__ == "__main__":
    main()