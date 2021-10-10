from pathlib import Path
import argparse
import re


def book_split(book_name, part_max=2500, part_min=1000):
    book = Path(book_name)
    part_folder = f"{book.stem}"
    Path(part_folder).mkdir(parents=True, exist_ok=True)
    text = book.read_text(encoding="utf-8")
    lines = text.splitlines()
    lines_count = len(lines)
    part_id, part, subpart = 0, [], 0
    last_fname, last_part = None, None
    print(f"Start processing book '{book_name}', lines: {lines_count}")

    for line_n, line in enumerate(lines):
        part_head = re.match(r"\s*(?P<id>\d+)\s*$", line)
        if part_head or line_n == lines_count - 1 or len("\n".join(part)) > part_max:

            if not part_head:
                part += [line, ""]

            subpart += 1
            part_fname = f"{part_folder}/{book.stem}_{part_id:0>2}_{subpart:02}{book.suffix}"
            part_text = "\n".join(part)

            if len(part_text) > 1:
                if part_head and last_part and len(part_text) < part_min:
                    print(f"Extend {last_fname} lines:{len(part)}")
                    part_text = "\n".join(last_part + part)
                    Path(last_fname).write_text(part_text, encoding="utf-8")
                else:
                    print(f"Saved  {part_fname} lines:{len(part)}")
                    Path(part_fname).write_text(part_text, encoding="utf-8")
                    last_fname, last_part = part_fname, part
                part = []

            if part_head:
                part_id, subpart = part_head.groupdict()["id"], 0
                part += ["", f"Часть {part_id}"]
                last_fname, last_part = None, None

        else:
            part.append(line)


def main():
    ap = argparse.ArgumentParser(description="Split text file to small parts")
    ap.add_argument("file", help="Text file to split", type=str, nargs="?")
    ap.add_argument("-m", "--max", help="Max part size, default: 2500", type=int, default=2500)
    ap.add_argument("-t", "--min", help="Min part size, default: 1000", type=int, default=1000)
    arg = ap.parse_args()

    if arg.file:
        book_split(arg.file, part_max=arg.max, part_min=arg.min)
    else:
        ap.print_help()


if __name__ == "__main__":
    main()
