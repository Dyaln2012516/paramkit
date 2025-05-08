"""
@File     : client.py
@Project  : 
@Time     : 2025/4/9 15:42
@Author   : dylan
@Contact Email: cgq2012516@163.com
"""

import json
import threading
from http.server import BaseHTTPRequestHandler
from pathlib import Path
from urllib.parse import urlparse

from paramkit.db.core import query_api
from paramkit.docs.markdown import generate_markdown


class MarkdownHandler(BaseHTTPRequestHandler):
    PROJECT_ROOT = Path(__file__).parent
    STATIC_DIR = PROJECT_ROOT.joinpath("static")
    DOC_PATH = PROJECT_ROOT.joinpath("api.md")
    _lock = threading.Lock()

    def do_GET(self):
        # Path routing
        if self.path.startswith('/_app/'):
            self.handle_static()
        elif self.path == '/':
            self.handle_homepage()
        elif self.path == '/download':
            self.handle_download()
        elif self.path == '/api/items/':
            self.query_api()
        else:
            self.send_error(404)

    def end_headers(self):
        # 开发环境允许所有来源访问
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', '*')
        self.send_header('Access-Control-Allow-Headers', '*')
        super().end_headers()

    def handle_static(self):
        """Handle static resource requests"""
        path = urlparse(self.path).path  # Safely parse the path
        file_path = self.STATIC_DIR.joinpath(*path.split('/'))

        print("file_path", file_path)
        if not file_path.is_file():
            self.send_error(404)
            return

        print("file_path333", file_path.exists())
        # Set MIME type
        mime_types = {'.html': 'text/html', '.js': 'application/javascript', '.css': 'text/css', '.json': 'application/json'}
        content_type = mime_types.get(file_path.suffix, 'text/plain')
        try:
            with file_path.open('rb') as f:
                self.send_response(200)
                self.send_header('Content-Type', content_type)
                self.send_header('Cache-Control', 'no-store')  # 推荐添加缓存控制
                self.end_headers()
                self.wfile.write(f.read())
        except FileNotFoundError:
            self.send_error(404, "File Not Found")
        except PermissionError:
            self.send_error(403, "Forbidden")
        except Exception as e:  # pylint: disable=W0718
            self.send_error(500, f"Internal Server Error: {str(e)}")

    def handle_homepage(self):
        """Render Markdown to template"""
        try:
            # Read the template
            template = self.STATIC_DIR.joinpath('index.html').read_text(encoding='utf-8')

            md_content = generate_markdown()
            with self._lock:
                self.DOC_PATH.write_text(md_content, encoding='utf-8')
            # Read Markdown content
            md_content = md_content.replace('`', r'\`').replace('\n', r'\n')
            # Replace placeholders
            final_html = template.replace('<!-- MARKDOWN_CONTENT -->', md_content)

            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(final_html.encode('utf-8'))
        except FileNotFoundError as e:
            self.send_error(500, f"File not found: {str(e)}")
        except Exception as e:  # pylint: disable=W0718
            self.send_error(500, f"Internal Error: {str(e)}")

    def handle_download(self):
        """Handle download requests"""
        try:
            self.send_response(200)
            self.send_header('Content-Type', 'text/markdown; charset=utf-8')
            self.send_header('Content-Disposition', 'attachment; filename="document.md"')
            self.end_headers()
            with self._lock:
                self.wfile.write(self.DOC_PATH.read_bytes())
        except Exception as e:  # pylint: disable=W0718
            self.send_error(500, f"Download Failed: {str(e)}")

    # 统一响应方法
    def send_json_response(self, status_code, data):
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))

    def query_api(self):
        try:
            response_data = {"code": 200, "message": '接口获取成功', "data": query_api()}
            self.send_json_response(200, response_data)
        except Exception as e:  # pylint: disable=W0718
            self.send_json_response(500, {"code": 500, "message": str(e), "data": []})
