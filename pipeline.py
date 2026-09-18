import re
import shutil
from pathlib import Path
from typing import List

from moviepy.editor import AudioFileClip

from config import CFG
from ocr import extract_text
from tts import synthesize
from video_builder import build_video


def _natural_key(path: Path) -> int:
    """Sort comment_2.png trước comment_10.png (thay vì sort theo chuỗi ký tự)."""
    m = re.search(r"(\d+)", path.stem)
    return int(m.group(1)) if m else 0


def _find_topic_and_comments() -> tuple[Path, List[Path]]:
    images_dir = Path(CFG.images_dir)

    topic_path = images_dir / CFG.topic_filename
    if not topic_path.exists():
        raise FileNotFoundError(f"Không tìm thấy ảnh topic: {topic_path}")

    comment_paths = [
        p for p in images_dir.iterdir()
        if p.stem.startswith(CFG.comment_prefix) and p.suffix.lower() in CFG.image_extensions
    ]
    comment_paths.sort(key=_natural_key)

    if not comment_paths:
        raise FileNotFoundError(
            f"Không tìm thấy ảnh comment nào (dạng '{CFG.comment_prefix}*.png') trong {images_dir}"
        )

    return topic_path, comment_paths


def run_pipeline() -> Path:
    output_dir = Path(CFG.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    tmp_audio_dir = output_dir / "_tmp_audio"
    tmp_audio_dir.mkdir(exist_ok=True)

    topic_path, comment_paths = _find_topic_and_comments()
    all_images = [topic_path] + comment_paths

    segments = []
    for idx, img_path in enumerate(all_images):
        text = extract_text(img_path)
        if not text:
            print(f"⚠️  Không đọc được chữ trong '{img_path.name}', bỏ qua ảnh này.")
            continue

        audio_path = tmp_audio_dir / f"seg_{idx}.mp3"
        synthesize(text, audio_path)
        duration = AudioFileClip(str(audio_path)).duration

        label = "TOPIC" if img_path == topic_path else f"COMMENT[{idx}]"
        print(f"✅ {label} — {img_path.name}: \"{text[:60]}{'...' if len(text) > 60 else ''}\" ({duration:.1f}s)")

        segments.append({"image": img_path, "audio_path": audio_path, "duration": duration})

    if not segments:
        raise RuntimeError("Không có đoạn nào đọc được chữ — kiểm tra lại chất lượng ảnh / cấu hình OCR.")

    print(f"\n>> Tổng {len(segments)} đoạn, đang ghép video...")
    final_video, bg_original, audio_clips = build_video(segments)

    out_path = output_dir / CFG.output_filename
    final_video.write_videofile(
        str(out_path),
        fps=CFG.fps,
        codec="libx264",
        audio_codec="aac",
        threads=4,
        preset="medium",
    )

    # Dọn dẹp tài nguyên
    final_video.close()
    bg_original.close()
    for a in audio_clips:
        a.close()
    shutil.rmtree(tmp_audio_dir, ignore_errors=True)

    print(f"\n🎬 Hoàn tất! Video lưu tại: {out_path}")
    return out_path
