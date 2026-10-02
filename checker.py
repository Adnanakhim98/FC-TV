import re
import urllib.request
from pathlib import Path

MASTER = Path("master.m3u")
OUTPUT = Path("live.m3u")

TIMEOUT = 8

def check_stream(url):
    try:
        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": "Mozilla/5.0"
            }
        )

        with urllib.request.urlopen(req, timeout=TIMEOUT) as response:
            if response.status != 200:
                return False

            content = response.read(4096).decode(
                "utf-8", errors="ignore"
            )

            # HLS playlist হলে সাধারণত এই signature থাকে
            if "#EXTM3U" in content or "#EXT-X-" in content:
                return True

            return False

    except Exception:
        return False


def build_playlist():
    if not MASTER.exists():
        print("master.m3u পাওয়া যায়নি")
        return

    lines = MASTER.read_text(
        encoding="utf-8"
    ).splitlines()

    output = [
        "#EXTM3U",
        ""
    ]

    current_entry = []
    current_url = None

    for line in lines:
        line = line.strip()

        if not line:
            continue

        # নতুন channel entry
        if line.startswith("#EXTINF:"):
            # আগের entry process
            if current_entry and current_url:
                if check_stream(current_url):
                    output.extend(current_entry)
                    output.append(current_url)
                    output.append("")

            current_entry = [line]
            current_url = None

        # EXT header/comment
        elif line.startswith("#"):
            if current_entry:
                current_entry.append(line)

        # Stream URL
        elif line.startswith("http://") or line.startswith("https://"):
            current_url = line

    # শেষ entry
    if current_entry and current_url:
        if check_stream(current_url):
            output.extend(current_entry)
            output.append(current_url)
            output.append("")

    OUTPUT.write_text(
        "\n".join(output),
        encoding="utf-8"
    )

    print("live.m3u তৈরি হয়েছে")


if __name__ == "__main__":
    build_playlist()
