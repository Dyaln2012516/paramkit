# !/usr/bin/env python3
# _*_ coding:utf-8 _*_
"""
@File     : cli.py
@Project  :
@Time     : 2025/3/31 14:26
@Author   : dylan
@Contact Email: cgq2012516@163.com
"""
import argparse
from http.server import HTTPServer

from paramkit.docs.client import MarkdownHandler


class CustomHelpFormatter(argparse.HelpFormatter):
    """自定义错误提示和帮助信息"""

    def _check_value(self, action, value):
        if action.choices is not None and value not in action.choices:
            raise argparse.ArgumentError(action, f"无效命令: '{value}'，可选命令: {', '.join(action.choices)}")


def main():
    parser = argparse.ArgumentParser(
        prog="paramkit", description="ParamKit 命令行工具", formatter_class=CustomHelpFormatter  # 绑定自定义格式化器
    )
    subparsers = parser.add_subparsers(
        dest="command", required=True, title="可用命令", help="输入子命令以执行操作"  # 强制要求输入子命令
    )

    # ===== serve 子命令 =====
    serve_parser = subparsers.add_parser("serve", help="启动 HTTP 服务")
    serve_parser.add_argument("-H", "--host", default="0.0.0.0", help="监听地址 (默认: 0.0.0.0)")
    serve_parser.add_argument("-p", "--port", type=int, default=996, help="监听端口 (默认: 996)")
    args = parser.parse_args()

    # ===== 命令分发逻辑 =====
    if args.command == "serve":
        server = HTTPServer((args.host, args.port), MarkdownHandler)  # noqa
        print(f"服务已启动: http://{args.host}:{args.port}")
        server.serve_forever()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
