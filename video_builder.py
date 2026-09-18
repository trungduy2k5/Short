"""
Ghép video cuối cùng bằng moviepy:
- Chọn ngẫu nhiên 1 video nền (parkour) trong backgrounds_dir, cắt đoạn ngẫu nhiên
  đúng bằng tổng thời lượng giọng đọc (nếu không có clip nào đủ dài, sẽ lặp lại).
- Resize/crop video nền cho vừa khung dọc (1080x1920).
- Overlay lần lượt từng ảnh (topic -> comment 1 -> comment 2 -> ...) đúng lúc
  giọng đọc tương ứng phát.
"""
import random
from pathlib import Path
from typing import List, Dict, Tuple

from moviepy.editor import (
    VideoFileClip,
    ImageClip,
    AudioFileClip,
    CompositeVideoClip,
    CompositeAudioClip,
    concatenate_videoclips,
)

from config import CFG


def _list_background_files() -> List[Path]:
    files = [p for p in Path(CFG.backgrounds_dir).glob("*") if p.suffix.lower() in (".mp4", ".mov", ".mkv")]
    if not files:
        raise FileNotFoundError(
            f"Không tìm thấy video nền nào trong '{CFG.backgrounds_dir}'. "
            "Hãy bỏ vài file .mp4 parkour vào thư mục đó."
        )
    return files


def get_background_subclip(duration: float) -> Tuple[VideoFileClip, VideoFileClip]:
    """Trả về (subclip đúng độ dài cần, clip gốc để close() sau).
    Nếu không có video nào đủ dài, sẽ lặp video dài nhất cho đủ."""
    bg_files = _list_background_files()
    random.shuffle(bg_files)

    # Thử từng file, ưu tiên file nào đủ dài để cắt ngẫu nhiên 1 đoạn tự nhiên
    for bg_path in bg_files:
        clip = VideoFileClip(str(bg_path))
        if clip.duration >= duration:
            max_start = max(0.0, clip.duration - duration)
            start = random.uniform(0, max_start)
            sub = clip.subclip(start, start + duration).without_audio()
            return sub, clip
        clip.close()

    # Không file nào đủ dài -> lấy file dài nhất và lặp lại cho đủ thời lượng
    longest_path = max(bg_files, key=lambda p: VideoFileClip(str(p)).duration)
    base = VideoFileClip(str(longest_path)).without_audio()
    loops_needed = int(duration // base.duration) + 1
    looped = concatenate_videoclips([base] * loops_needed)
    sub = looped.subclip(0, duration)
    return sub, base


def fit_to_resolution(clip: VideoFileClip, resolution: Tuple[int, int]) -> VideoFileClip:
    """Resize + crop-center video nền để lấp đầy khung hình dọc mà không méo hình."""
    target_w, target_h = resolution
    clip_ratio = clip.w / clip.h
    target_ratio = target_w / target_h

    if clip_ratio > target_ratio:
        # Video gốc "rộng" hơn khung đích -> resize theo chiều cao, crop 2 bên
        clip = clip.resize(height=target_h)
        clip = clip.crop(x_center=clip.w / 2, width=target_w)
    else:
        # Video gốc "hẹp" hơn khung đích -> resize theo chiều rộng, crop trên dưới
        clip = clip.resize(width=target_w)
        clip = clip.crop(y_center=clip.h / 2, height=target_h)

    return clip


def build_image_overlay(image_path: Path, duration: float, start: float) -> ImageClip:
    target_w, _ = CFG.resolution
    max_w = int(target_w * CFG.image_max_width_ratio)

    clip = ImageClip(str(image_path))
    if clip.w > max_w:
        clip = clip.resize(width=max_w)

    clip = clip.set_duration(duration).set_start(start).set_position("center")
    return clip


def build_video(segments: List[Dict]):
    """
    segments: [{ "image": Path, "audio_path": Path, "duration": float }, ...]
    theo đúng thứ tự topic -> comment 1 -> comment 2 -> ...
    """
    gap = CFG.gap_between_segments
    total_duration = sum(s["duration"] for s in segments) + gap * max(0, len(segments) - 1)

    bg_sub, bg_original = get_background_subclip(total_duration)
    bg_sub = fit_to_resolution(bg_sub, CFG.resolution)

    image_clips = []
    audio_clips = []
    t_cursor = 0.0

    for seg in segments:
        img_clip = build_image_overlay(seg["image"], seg["duration"], t_cursor)
        image_clips.append(img_clip)

        audio_clip = AudioFileClip(str(seg["audio_path"])).set_start(t_cursor)
        audio_clips.append(audio_clip)

        t_cursor += seg["duration"] + gap

    final_audio = CompositeAudioClip(audio_clips)
    final_video = CompositeVideoClip([bg_sub, *image_clips], size=CFG.resolution)
    final_video = final_video.set_audio(final_audio).set_duration(total_duration)

    # Trả thêm bg_original + audio_clips để pipeline.py close() giải phóng tài nguyên
    return final_video, bg_original, audio_clips
