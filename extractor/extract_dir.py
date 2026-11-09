import argparse
import fnmatch
import os
from datetime import datetime

from pypdf import PdfReader


def path_exists(path):
    return os.path.exists(path)


def get_depth(root, folder):
    relative = os.path.relpath(folder, root)
    if relative == ".":
        return 0
    return relative.count(os.sep) + 1


def get_created_time(path):
    info = os.stat(path)
    return datetime.fromtimestamp(getattr(info, "st_birthtime", info.st_mtime))


def scan_files(path, depth=None, pattern="*", from_date=None):
    if not path_exists(path):
        raise FileNotFoundError(f"Path does not exist: {path}")

    file_paths = []

    for folder, subfolders, files in os.walk(path):
        if depth is not None and get_depth(path, folder) >= depth:
            subfolders.clear()

        for name in files:
            file_path = os.path.join(folder, name)
            if not fnmatch.fnmatch(name, pattern):
                continue
            if from_date is not None and get_created_time(file_path) < from_date:
                continue
            file_paths.append(file_path)

    return file_paths


def read_pdf(path):
    reader = PdfReader(path)
    pages = [page.extract_text() or "" for page in reader.pages]
    return "\n".join(pages)


def read_file(path):
    if path.lower().endswith(".pdf"):
        return read_pdf(path)

    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("path")
    parser.add_argument("--depth", type=int, default=None)
    parser.add_argument("--pattern", default="*")
    parser.add_argument("--from", dest="from_date", type=datetime.fromisoformat, default=None)
    args = parser.parse_args()

    for file_path in scan_files(args.path, args.depth, args.pattern, args.from_date):
        print(file_path)


if __name__ == "__main__":
    main()
