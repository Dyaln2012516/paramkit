# !/usr/bin/env python3
# _*_ coding:utf-8 _*_
"""
@File     : markdown.py
@Project  : 
@Time     : 2025/4/6 20:39
@Author   : dylan
@Contact Email: cgq2012516@163.com
"""
import json
from datetime import datetime

from mdutils import MdUtils


def generate_full_api_docs(api_spec):
    md = MdUtils(file_name="API_DOC", title=api_spec['title'])

    # === 文档头 ===
    md.new_header(1, api_spec['title'])
    md.new_line(f"**版本**: {api_spec['version']}")
    md.new_line(f"**基础URL**: `{api_spec['base_url']}`")
    md.new_line(f"**更新日期**: {datetime.now().strftime('%Y-%m-%d')}")

    # === 目录 ===
    md.new_header(2, "目录")
    md.new_list(
        [
            "[认证方式](#认证方式)",
            "[全局参数](#全局参数)",
            "[错误代码](#错误代码)",
            *[f"[{interface['name']}](#{interface['name'].replace(' ', '-')})" for interface in api_spec['interfaces']],
        ]
    )

    # === 认证 ===
    md.new_header(2, "认证方式", add_table_of_contents="n")
    md.new_line("```http\nAuthorization: Bearer {your_token}\n```")

    # === 全局参数 ===
    md.new_header(2, "全局参数")
    md.new_line("### 请求头")
    t_data = ['参数名', '类型', '必填', '说明'] + [
        item
        for param in api_spec['global_headers']
        for item in [param['name'], param['type'], '✅' if param['required'] else '❌', param['desc']]
    ]

    md.new_table(columns=4, rows=len(t_data) // 4, text=t_data, text_align='left')

    # === 错误码 ===
    md.new_header(2, "错误代码")
    t_data = ['HTTP状态码', '错误码', '说明'] + [
        item for code in api_spec['error_codes'] for item in [str(code['status']), code['code'], code['message']]
    ]

    md.new_table(columns=3, rows=len(t_data) // 3, text=t_data, text_align='left')

    # === 接口详情 ===
    md.new_header(2, "接口详情")
    for interface in api_spec['interfaces']:
        # 接口标题
        md.new_header(3, f"{interface['name']}", add_table_of_contents="n")
        md.new_line(f"`{interface['method'].upper()} {interface['path']}`  \n")
        md.new_line(interface['description'])

        # 请求参数
        if interface['params']:
            md.new_header(3, "请求参数")
            param_rows = ['参数名', '位置', '类型', '必填', '说明']
            for param in interface['params']:
                param_rows += [
                    param['name'],
                    param['in'],
                    param.get('type', 'string'),
                    '✅' if param['required'] else '❌',
                    param.get('description', ''),
                ]
            md.new_table(columns=5, rows=len(param_rows) // 5, text=param_rows, text_align='left')

        # 示例代码
        md.new_header(4, "请求示例")
        md.insert_code(json.dumps(interface['request_example'], indent=2), 'json')

        md.new_header(4, "成功响应")
        md.insert_code(json.dumps(interface['response_success'], indent=2), 'json')

        if interface.get('response_error'):
            md.new_header(4, "错误响应")
            md.insert_code(json.dumps(interface['response_error'], indent=2), 'json')

        md.new_line('---')

    # === 附录 ===
    md.new_header(2, "附录")
    md.new_line("### 速率限制")
    md.new_list(["认证用户：1000次请求/小时", "匿名用户：100次请求/小时"])

    return md.file_data_text


# 示例数据
api_specs = {
    "title": "用户服务API文档",
    "version": "v1.2",
    "base_url": "https://api.example.com/v1",
    "global_headers": [
        {"name": "Authorization", "type": "string", "required": True, "desc": "Bearer Token"},
        {"name": "X-Request-ID", "type": "string", "required": False, "desc": "请求唯一标识"},
    ],
    "error_codes": [{"status": 400, "code": "invalid_params", "message": "参数校验失败"}],
    "interfaces": [
        {
            "name": "创建用户",
            "method": "post",
            "path": "/users",
            "description": "创建新用户账号",
            "params": [
                {
                    "name": "username",
                    "in": "body",
                    "type": "string",
                    "required": True,
                    "description": "用户名",
                },
                {
                    "name": "email",
                    "in": "body",
                    "type": "email",
                    "required": True,
                    "description": "邮箱地址",
                },
            ],
            "request_example": {"username": "test_user", "email": "user@example.com"},
            "response_success": {"code": 201, "data": {"user_id": 123}},
            "response_error": {"code": 409, "error": "user_exists"},
        }
    ],
}

# 生成文档
full_docs = generate_full_api_docs(api_specs)
with open("full_api_doc.md", "w", encoding="utf-8") as f:
    f.write(full_docs)
