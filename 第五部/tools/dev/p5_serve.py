# 默认只监听本机，测试通过端口0获取空闲端口，避免占用用户已经运行的服务。
import argparse
import functools
import json
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

GAME = Path(__file__).resolve().parents[2] / '游戏'


class Handler(SimpleHTTPRequestHandler):
    def log_message(self, *_):
        pass

    def end_headers(self):
        self.send_header('Cache-Control', 'no-store')
        super().end_headers()


def main():
    parser = argparse.ArgumentParser(description='第五部本地静态服务器')
    parser.add_argument('--port', type=int, default=8755)
    args = parser.parse_args()
    handler = functools.partial(Handler, directory=str(GAME))
    with ThreadingHTTPServer(('127.0.0.1', args.port), handler) as server:
        print(json.dumps({'url': f'http://127.0.0.1:{server.server_port}/'}), flush=True)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass


if __name__ == '__main__':
    main()
