from pathlib import Path
import argparse
import re

from pydub import AudioSegment


def book_join(folder):
    parts = Path(folder).glob("*.mp3")
    groups = {}

    for part in parts:
        match = re.match(r"(?P<group>.+)_(.+)", part.name)
        if match:
            match = match.groupdict()
            groups.setdefault(match["group"], []).append(part)

    for group, files in groups.items():
        sound = AudioSegment.silent(duration=1000)
        for file in files:
            sound += AudioSegment.from_mp3(file)
            sound += AudioSegment.silent(duration=2000)
        print(f"part: {group} len: {int(sound.duration_seconds)} sec")
        sound.export(f"{folder}/{group}.mp3", format="mp3")


def main():
    ap = argparse.ArgumentParser(description="Join mp3 files according book parts")
    ap.add_argument("folder", help="Folder contains mp3 files", type=str, nargs="?")
    arg = ap.parse_args()

    if arg.folder:
        book_join(arg.folder)
    else:
        ap.print_help()


if __name__ == "__main__":
    main()
