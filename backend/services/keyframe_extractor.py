import cv2
import numpy as np
import os
from typing import List, Dict

class KeyframeExtractor:
    def __init__(self, static_threshold: float = 10.0, dynamic_frames: int = 3):
        self.static_threshold = static_threshold
        self.dynamic_frames = dynamic_frames

    def calculate_frame_variance(self, frame1: np.ndarray, frame2: np.ndarray) -> float:
        gray1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
        gray2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)

        diff = cv2.absdiff(gray1, gray2)
        variance = np.mean(diff)

        return variance

    def extract_keyframes(self, video_path: str) -> List[Dict]:
        cap = cv2.VideoCapture(video_path)

        if not cap.isOpened():
            raise ValueError(f"Cannot open video file: {video_path}")

        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = cap.get(cv2.CAP_PROP_FPS)

        if total_frames == 0:
            cap.release()
            raise ValueError("Video has no frames")

        frames = []
        variances = []

        ret, prev_frame = cap.read()
        if not ret:
            cap.release()
            raise ValueError("Cannot read first frame")

        frames.append(prev_frame)

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            if len(frames) > 0:
                variance = self.calculate_frame_variance(prev_frame, frame)
                variances.append(variance)

            frames.append(frame)
            prev_frame = frame

        cap.release()

        avg_variance = np.mean(variances) if variances else 0

        keyframes = []
        base_filename = os.path.splitext(os.path.basename(video_path))[0]

        if avg_variance < self.static_threshold:
            median_idx = len(frames) // 2
            keyframe_path = f"keyframes/{base_filename}_frame_{median_idx}.jpg"
            cv2.imwrite(keyframe_path, frames[median_idx])

            keyframes.append({
                "path": keyframe_path,
                "frame_index": median_idx,
                "type": "static"
            })

        else:
            indices = [
                0,
                len(frames) // 2,
                len(frames) - 1
            ]

            for idx in indices:
                keyframe_path = f"keyframes/{base_filename}_frame_{idx}.jpg"
                cv2.imwrite(keyframe_path, frames[idx])

                keyframes.append({
                    "path": keyframe_path,
                    "frame_index": idx,
                    "type": "dynamic"
                })

        return keyframes
