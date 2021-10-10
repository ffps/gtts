from pathlib import Path
import argparse
import asyncio
import time
import base64
import requests

GET_TOKEN = """
Manual for get Google API tocket.

1. Open:
 http://gstatic.com/cloud-site-ux/text_to_speech/text_to_speech.min.html

2. Paste to URL field:
 javascript void window.addEventListener("cloud-demo-captcha-solved", function(e){document.write(e.detail.token)})

3. Type symbol ":" after "javascript" then press Enter
(for security reason you cannot be paste "javascript:" to URL field)

4. Press "SPEAK IT" and resolve captcha
"""


def tts_book(options):
    parts = list(Path(options.folder).glob("*.txt"))
    options.text_files = parts
    if parts:
        sem = asyncio.Semaphore(options.threads)
        q = []
        for part_file in parts:
            q.append(tts_file_async(part_file, sem, options))
        print(f"Start encoding {len(q)} parts")
        asyncio.run(asyncio.wait(q))
        print("END")
    else:
        print(f"No .txt files in folder '{options.folder}'")


async def tts_file_async(part_file, semaphore, options):
    async with semaphore:
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, tts_file, part_file, options)


def tts_file(text_file, options):

    audio_folder = Path(text_file.parent.with_suffix(".mp3"))
    audio_folder.mkdir(parents=True, exist_ok=True)
    audio_file = Path(audio_folder / text_file.stem).with_suffix(".mp3")

    if Path(audio_file).exists():
        return

    text = text_file.read_text(encoding="utf-8")
    print(f" {text_file.name} START {len(text)} chars")
    query = {
        "input": {"ssml": set_accents(text, line_pause=options.line_pause)},
        "voice": {"languageCode": "ru-RU", "name": "ru-RU-Wavenet-B"},
        "audioConfig": {"audioEncoding": "mp3", "pitch": options.pitch, "speakingRate": options.rate / 100},
    }
    headers = {"content-type": "text/plain;charset=UTF-8"}
    params = ("url", "https://texttospeech.googleapis.com/v1beta1/text:synthesize"), ("token", options.token)

    time.sleep(options.file_pause)
    ret = requests.post("http://cxl-services.appspot.com/proxy", json=query, headers=headers, params=params)

    if ret.reason == "OK":
        audio = ret.json()["audioContent"]
        audio = base64.b64decode(audio)
        audio_file.write_bytes(audio)
        ret = f"{len(audio)} bytes"
    else:
        ret = ret.reason

    audio_files = list(Path(audio_folder).glob("*.mp3"))
    print(f" {audio_file.name} END   {ret:<20} [{len(audio_files)}/{len(options.text_files)}]")
    return ret


def set_accents(text, line_pause=200):

    from accents_ru import accents

    for key, val in accents.items():
        text = text.replace(key, val)
        text = text.replace("\n", f'<break time="{line_pause}ms"/>')

    return f"<speak>{text}</speak>"


def main():
    ap = argparse.ArgumentParser(description="Encode book to MP3 with using Google TTS engine")
    ap.add_argument("folder", help="Folder contains book text files", type=str, nargs="?")
    ap.add_argument("-t", "--token", help="Google API token. Run -m for manual", type=str, nargs="?")
    ap.add_argument("-m", "--get-token", help="Get Google API token manual", action="store_true")
    ap.add_argument("-n", "--threads", help="Threads limit, default: 2", type=int, default=2)
    ap.add_argument("--rate", help="Speech rate percent, default: 120", type=int, default=120)
    ap.add_argument("--pitch", help="Voice pitch, default: -5", type=int, default=-5)
    ap.add_argument("--line-pause", help="Pause after each line msec, default: 500", type=int, default=500)
    ap.add_argument("--file-pause", help="Pause between file request sec, default: 5", type=int, default=5)
    arg = ap.parse_args()

    if arg.get_token or (arg.folder and not arg.token):
        return print(GET_TOKEN)

    if arg.folder and arg.token:
        return tts_book(arg)

    ap.print_help()


if __name__ == "__main__":
    main()
