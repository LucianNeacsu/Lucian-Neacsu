# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project overview

This is a small, beginner-oriented Python project that watches a video feed (a
webcam or an IP/NVR camera over RTSP) and alerts on motion by saving a
snapshot. It is explicitly framed (in `README.md`) as a first hands-on
exercise for someone new to programming, with "next steps" ideas (email
alerts, running as a background service, cleanup of old snapshots, AI-based
person/animal detection) left for future sessions.

All user-facing documentation and in-code comments are written in Romanian —
match that language when editing `README.md` or comments in the existing
scripts, and keep explanations beginner-friendly (the README even calls out
which programming concepts — variables, functions, `while` loops, `if`
conditions — each part of the code demonstrates).

## Commands

```bash
# Install the only dependency (opencv-python)
pip install -r requirements.txt

# One-shot connectivity check: connects once, saves test_poza.jpg, then exits
python test_camera.py

# Continuous motion-detection loop (Ctrl+C to stop)
python motion_alert.py
```

There is no build step, linter, or test suite configured in this repo.

Both scripts read the video source from the `CAMERA_SOURCE` environment
variable (an RTSP URL such as `rtsp://user:pass@192.168.1.50:554/stream1`);
if unset, they default to `0`, the local webcam. Never hardcode camera
credentials in source — always pass them via `CAMERA_SOURCE`.

## Architecture

- `test_camera.py` — minimal sanity check. Opens `VIDEO_SOURCE` once, reads a
  single frame, writes it to `test_poza.jpg`, and exits with a clear
  OK/EROARE message. Meant to be run before `motion_alert.py` to confirm the
  RTSP address/credentials are correct.
- `motion_alert.py` — the actual detector, structured as:
  1. `VIDEO_SOURCE` / `MOTION_THRESHOLD` / `MIN_MOTION_AREA` /
     `ALERT_COOLDOWN_SECONDS` module-level constants — the intended place to
     tune behavior without touching the loop logic.
  2. `send_alert(frame, timestamp)` — writes a snapshot into `snapshots/`
     (created on demand, gitignored) and prints an alert message; this is the
     designated extension point for future notification channels (e.g.
     email/SMS) mentioned in the README's "next steps".
  3. `main()` — opens the capture, then loops: read a frame, convert to
     grayscale + blur, diff against the previous frame, threshold + dilate,
     find contours, and treat any contour above `MIN_MOTION_AREA` as motion.
     `ALERT_COOLDOWN_SECONDS` throttles repeated alerts for sustained motion.

There are no other modules — both files are self-contained scripts sharing
the same `CAMERA_SOURCE` env var convention.
