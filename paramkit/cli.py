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
    """Custom error prompts and help information"""

    def _check_value(self, action, value):
        if action.choices is not None and value not in action.choices:
            raise argparse.ArgumentError(action, f"Invalid command: '{value}', available commands: {', '.join(action.choices)}")


def main():
    parser = argparse.ArgumentParser(
        prog="paramkit",
        description="ParamKit command-line tool",
        formatter_class=CustomHelpFormatter,
        # Bind custom formatter
    )
    subparsers = parser.add_subparsers(
        dest="command",
        required=True,
        title="Available commands",
        help="Enter a subcommand to execute an operation",
        # Require subcommand input
    )

    # ===== serve subcommand =====
    serve_parser = subparsers.add_parser("serve", help="Start HTTP service")
    serve_parser.add_argument("-H", "--host", default="localhost", help="Listening address (default: localhost)")
    serve_parser.add_argument("-p", "--port", type=int, default=996, help="Listening port (default: 996)")
    args = parser.parse_args()

    # ===== Command dispatch logic =====
    if args.command == "serve":
        server = HTTPServer((args.host, args.port), MarkdownHandler)  # noqa
        print(f"Web server of API documents is running on: http://{args.host}:{args.port}")
        server.serve_forever()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
