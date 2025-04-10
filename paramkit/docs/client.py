# !/usr/bin/env python3
# _*_ coding:utf-8 _*_
"""
@File     : client.py
@Project  : 
@Time     : 2025/4/9 15:42
@Author   : dylan
@Contact Email: cgq2012516@163.com
"""
import os
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse


class MarkdownHandler(BaseHTTPRequestHandler):
    PROJECT_ROOT = r"/Users/dylan/Desktop/python-projects/paramkit/paramkit/src/paramkit/docs"  # macOS用户目录适配
    MD_FILE_PATH = os.path.join(PROJECT_ROOT, "api_doc.md")  # 实际Markdown文件路径
    STATIC_DIR = os.path.join(PROJECT_ROOT, "static")

    def do_GET(self):
        # 路径路由
        if self.path.startswith('/static/'):
            self.handle_static()
        elif self.path == '/':
            self.handle_homepage()
        elif self.path == '/download':
            self.handle_download()
        else:
            self.send_error(404)

    def handle_static(self):
        """处理静态资源请求"""
        path = urlparse(self.path).path  # 安全解析路径
        file_path = os.path.join(self.STATIC_DIR, path[len('/static/') :])

        if not os.path.isfile(file_path):
            self.send_error(404)
            return

        # 设置MIME类型
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
        """渲染Markdown到模板"""
        try:
            # 读取模板
            with open(os.path.join(self.STATIC_DIR, 'html/index.html'), 'r', encoding='utf-8') as f:
                template = f.read()

            # 读取Markdown内容
            with open(self.MD_FILE_PATH, 'r', encoding='utf-8') as f:
                md_content = f.read().replace('`', r'\`').replace('\n', r'\n')

            # 替换占位符
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
        """处理下载请求"""
        try:
            with open(self.MD_FILE_PATH, 'rb') as f:
                content = f.read()

            self.send_response(200)
            self.send_header('Content-Type', 'text/markdown; charset=utf-8')
            self.send_header('Content-Disposition', 'attachment; filename="document.md"')
            self.end_headers()
            self.wfile.write(content)
        except Exception as e:  # pylint: disable=W0718
            self.send_error(500, f"Download Failed: {str(e)}")
