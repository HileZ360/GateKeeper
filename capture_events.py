import cv2
import numpy as np
import json
import argparse
from datetime import timedelta


def format_time(seconds: float) -> str:
    td = timedelta(seconds=int(seconds))
    total_seconds = int(td.total_seconds())
    minutes, sec = divmod(total_seconds, 60)
    return f"{minutes:02d}:{sec:02d}"


class EventTracker:
    def __init__(self):
        self.active = {}
        self.events = []

    def update(self, name: str, is_active: bool, timestamp: float):
        if is_active:
            if name not in self.active:
                self.active[name] = timestamp
        else:
            if name in self.active:
                start = self.active.pop(name)
                self.events.append(
                    {
                        "type": name,
                        "start": format_time(start),
                        "end": format_time(timestamp),
                    }
                )

    def finalize(self, final_time: float):
        for name, start in list(self.active.items()):
            self.events.append(
                {
                    "type": name,
                    "start": format_time(start),
                    "end": format_time(final_time),
                }
            )
        self.active.clear()


def main():
    parser = argparse.ArgumentParser(description="Capture video and log events")
    parser.add_argument("--source", default=0, help="Video source (default: webcam)")
    parser.add_argument("--output", default="events.json", help="Output JSON file")
    args = parser.parse_args()

    cap = cv2.VideoCapture(
        int(args.source) if str(args.source).isdigit() else args.source
    )
    if not cap.isOpened():
        raise SystemExit("Unable to open video source")

    # Initialize detectors
    hog = cv2.HOGDescriptor()
    hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())

    ret, prev = cap.read()
    if not ret:
        raise SystemExit("Unable to read from video source")
    prev_gray = cv2.cvtColor(prev, cv2.COLOR_BGR2GRAY)

    tracker = EventTracker()
    motion_threshold = 20
    quick_threshold = 40

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        timestamp = cap.get(cv2.CAP_PROP_POS_MSEC) / 1000.0
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        diff = cv2.absdiff(prev_gray, gray)
        diff_mean = diff.mean()
        motion = diff_mean > motion_threshold
        quick = diff_mean > quick_threshold

        rects, _ = hog.detectMultiScale(frame, winStride=(8, 8))
        person = len(rects) > 0

        tracker.update("motion", motion, timestamp)
        tracker.update("quick_motion", quick, timestamp)
        tracker.update("person", person, timestamp)

        prev_gray = gray

    final_time = cap.get(cv2.CAP_PROP_POS_MSEC) / 1000.0
    tracker.finalize(final_time)
    cap.release()

    with open(args.output, "w", encoding="utf-8") as fh:
        json.dump({"events": tracker.events}, fh, indent=2, ensure_ascii=False)
    print(f"Events saved to {args.output}")


if __name__ == "__main__":
    main()
