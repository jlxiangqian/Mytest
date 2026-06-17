#!/usr/bin/env python3
"""禅意贪吃蛇 · 本地服务器
启动后自动打开浏览器，扫描 music/ 目录提供播放列表。
"""

import http.server
import json
import os
import pathlib
import socketserver
import webbrowser
from urllib.parse import urlparse

PORT = 8080
DIR = pathlib.Path(__file__).parent
MUSIC_DIR = DIR / "music"


def read_url_tracks():
    """读取 music/url.txt 中的远程音乐链接"""
    urls = []
    url_file = MUSIC_DIR / "url.txt"
    if url_file.is_file():
        for line in url_file.read_text("utf-8").strip().splitlines():
            line = line.strip()
            if line and not line.startswith("#"):
                urls.append(line)
    return urls

class Handler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)

        # ── API：播放列表 ──
        if parsed.path == "/api/playlist":
            tracks = []
            if MUSIC_DIR.is_dir():
                for f in sorted(MUSIC_DIR.iterdir()):
                    if f.suffix.lower() in (".mp3", ".wav", ".ogg", ".flac", ".m4a", ".webm", ".mp4"):
                        tracks.append(f.name)
            # 追加远程 URL 曲目
            tracks.extend(read_url_tracks())
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Cache-Control", "no-cache")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps(tracks, ensure_ascii=False).encode("utf-8"))
            return

        # ── 默认页面 ──
        if parsed.path == "/":
            self.path = "/zen-snake.html"

        return super().do_GET()

    def log_message(self, fmt, *args):
        if args:
            print(f"  ->  {args[0]} {args[1] if len(args) > 1 else ''}")


def main():
    os.chdir(DIR)
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        url = f"http://localhost:{PORT}"
        count = len(list(MUSIC_DIR.glob("*.mp3")))
        print(f"\n  **  Zen Snake  **")
        print(f"  --------------")
        print(f"  Open: {url}")
        print(f"  Tracks: {count}")
        print(f"  Ctrl+C to quit\n")
        webbrowser.open(url)
        httpd.serve_forever()


if __name__ == "__main__":
    main()
