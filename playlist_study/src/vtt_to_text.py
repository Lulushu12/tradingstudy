"""
Turn downloaded VTT subtitle files into plain transcripts.

Two flavours arrive from yt-dlp. `<id>.en.vtt` is the channel's own caption
track and is already clean prose. `<id>.en-orig.vtt` is YouTube's auto caption
track, which repeats each line several times as the rolling display updates, so
it needs dedup. The manual track is preferred whenever it exists.
"""

import os
import re
import sys

TAG = re.compile(r"<[^>]+>")
TS = re.compile(r"^\d{2}:\d{2}:\d{2}\.\d{3}\s+-->")
HEADER = re.compile(r"^(WEBVTT|Kind:|Language:|NOTE|STYLE|REGION)")


def parse(path):
    lines = []
    with open(path, encoding="utf-8", errors="replace") as f:
        for raw in f:
            s = raw.rstrip("\n")
            if not s.strip() or TS.match(s) or HEADER.match(s) or s.strip().isdigit():
                continue
            s = TAG.sub("", s).strip()
            if s:
                lines.append(s)

    # Auto captions repeat the previous line as the display scrolls. Drop a line
    # when it is identical to, or fully contained in, the one just kept.
    out = []
    for s in lines:
        if out and (s == out[-1] or s in out[-1]):
            continue
        if out and out[-1] in s:
            out[-1] = s
            continue
        out.append(s)

    text = " ".join(out)
    return re.sub(r"\s+", " ", text).strip()


def best_for(vid, subdir):
    manual = os.path.join(subdir, f"{vid}.en.vtt")
    auto = os.path.join(subdir, f"{vid}.en-orig.vtt")
    for p in (manual, auto):
        if os.path.exists(p):
            return p, ("manual" if p == manual else "auto")
    for p in sorted(f for f in os.listdir(subdir) if f.startswith(vid + ".")):
        return os.path.join(subdir, p), "other"
    return None, None


def main(playlist_file, subdir, outdir):
    os.makedirs(outdir, exist_ok=True)
    missing, written = [], 0
    for line in open(playlist_file, encoding="utf-8"):
        parts = line.rstrip("\n").split("|", 3)
        if len(parts) < 4:
            continue
        idxs, vid, dur, title = parts
        path, kind = best_for(vid, subdir)
        if not path:
            missing.append((idxs, vid, title))
            continue
        text = parse(path)
        if len(text) < 80:
            missing.append((idxs, vid, title + " [empty captions]"))
            continue
        safe = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")[:60]
        dest = os.path.join(outdir, f"{int(idxs):03d}-{safe}.txt")
        with open(dest, "w", encoding="utf-8") as f:
            f.write(f"# {title}\n")
            f.write(f"video_id: {vid}\nduration_s: {dur}\ncaptions: {kind}\n")
            f.write(f"url: https://www.youtube.com/watch?v={vid}\n\n")
            f.write(text + "\n")
        written += 1

    print(f"wrote {written} transcripts to {outdir}")
    if missing:
        print(f"{len(missing)} without usable captions:")
        for i, v, t in missing:
            print(f"  {i} {v} {t}")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3])
