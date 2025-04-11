"""
@File     : client.py
@Project  : 
@Time     : 2025/4/9 15:42
@Author   : dylan
@Contact Email: cgq2012516@163.com
"""

import os
import threading
from http.server import BaseHTTPRequestHandler
from pathlib import Path
from urllib.parse import urlparse

from paramkit.docs.markdown import generate_markdown


class MarkdownHandler(BaseHTTPRequestHandler):
    PROJECT_ROOT = Path(__file__).parent  # Adaptation for macOS user directory
    STATIC_DIR = PROJECT_ROOT.joinpath("static")
    DOC_PATH = PROJECT_ROOT.joinpath("api.md")
    _lock = threading.Lock()

    def do_GET(self):
        # Path routing
        if self.path.startswith('/static/'):
            self.handle_static()
        elif self.path == '/':
            self.handle_homepage()
        elif self.path == '/download':
            self.handle_download()
        else:
            self.send_error(404)

    def handle_static(self):
        """Handle static resource requests"""
        path = urlparse(self.path).path  # Safely parse the path
        file_path = os.path.join(self.STATIC_DIR, path[len('/static/') :])

        if not os.path.isfile(file_path):
            self.send_error(404)
            return

        # Set MIME type
        mime_types = {'.html': 'text/html', '.js': 'application/javascript', '.css': 'text/css'}
        ext = os.path.splitext(file_path)[1]
        content_type = mime_types.get(ext, 'text/plain')

        try:
            with open(file_path, 'rb') as f:
                self.send_response(200)
                self.send_header('Content-Type', content_type)
                self.end_headers()
                self.wfile.write(f.read())
        except Exception as e:  # pylint: disable=W0718
            self.send_error(500, f"Error: {str(e)}")

    def handle_homepage(self):
        """Render Markdown to template"""
        try:
            # Read the template
            template = self.STATIC_DIR.joinpath('html', 'index.html').read_text(encoding='utf-8')

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
