# Encoding book to MP3 with using Google TTS engine

1. Split text book file

   Split text to small parts with using `book_split.py book_name.txt`


2. Get Google API token

   Run `book_tts.py -m` and read short manual


3. Encode book files with

   Run `book_tts.py book_name [options] -t token_content`


4. Join mp3 files to book parts if needed

   Run `book_join.py book_name`
