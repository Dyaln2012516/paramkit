# !/usr/bin/env python3
# _*_ coding:utf-8 _*_
"""
@File     : markdown.py
@Project  : 
@Time     : 2025/4/6 20:39
@Author   : dylan
@Contact Email: cgq2012516@163.com
"""
from abc import abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, List, Optional, Tuple

from mdutils import MdUtils

from paramkit.db.model import APIHeaderRecord, APIParamRecord, APIRecord


@dataclass
class BaseUrl:
    name: str
    url: str


class BaseTable:
    data: List[Any]
    head: Tuple[str, ...]

    @property
    @abstractmethod
    def text(self) -> List[str]:
        raise NotImplementedError("Subclasses must implement this method")

    @property
    def rows(self):
        return len(self.text) // self.columns

    @property
    def columns(self):
        return len(self.head)


@dataclass
class Headers(BaseTable):
    data: List[APIHeaderRecord]
    head: Tuple[str, ...] = ('参数名', '参数值')

    @property
    def text(self) -> List[str]:
        data = list(self.head)
        for header in self.data:
            data.extend([header.header_key, header.header_value])
        return data


@dataclass
class Params(BaseTable):
    data: List[APIParamRecord]
    head: Tuple[str, ...] = ('参数名', '类型', '必填', '说明', '示例')

    @property
    def text(self) -> List[str]:
        data = list(self.head)
        for param in self.data:
            data.extend(
                [
                    param.param_name,
                    param.param_type,
                    '✅' if param.is_required == 'True' else '❌',
                    param.param_desc or '-',
                    param.param_demo or '-',
                ]
            )
        return data


@dataclass
class ApiData:
    header: Headers
    param: Params
    uid: Optional[str] = None
    description: str = ''
    duration: Optional[str] = None
    update_at: Optional[str] = None
    path: Optional[str] = None
    method: Optional[str] = None
    request: Optional[str] = ''
    response: Optional[str] = ''

    def __post_init__(self):
        self.request = self.request or ''
        self.response = self.response or ''
        self.description = self.description or ''


@dataclass
class MarkdownData:
    title: str
    version: str
    author: str
    base_url: List[BaseUrl]
    apis: List[ApiData] = field(default_factory=list)


def _data_from_db(request_uid: str = '') -> MarkdownData:
    data = MarkdownData(
        'API文档',
        'v1.0',
        author='cgq',
        base_url=[
            BaseUrl('开发环境domain', 'https://api.example.com/dev/v1'),
            BaseUrl('测试环境domain', 'https://api.example.com/stg/v1'),
            BaseUrl('生产环境domain', 'https://api.example.com/prd/v1'),
        ],
    )
    for record in APIRecord.select():
        api = ApiData(
            uid=record.request_uid,
            update_at=record.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            path=record.path,
            method=record.method,
            duration=f'{record.duration:.3f}',
            description=record.api_desc,
            header=Headers(APIHeaderRecord.select().where(APIHeaderRecord.request_uid == record.request_uid)),
            param=Params(APIParamRecord.select().where(APIParamRecord.request_uid == record.request_uid)),
            request=record.request_body,
            response=record.response_body,
        )
        data.apis.append(api)
    return data


def _api_markdown(api: ApiData, md: MdUtils):
    # === 目录 ===
    md.new_line(f'<a id="{api.uid}"></a>')
    md.new_header(3, "接口信息", add_table_of_contents='n')
    md.new_line(f"**接口简介**：`{api.description.strip()}`")
    md.new_line(f"**接口地址**：`{api.path}`")
    md.new_line(f"**请求方法**：`{api.method}`")
    md.new_line(f"**接口耗时**：`{api.duration}ms`")
    md.new_line(f"**更新时间**：`{api.update_at}`")

    # === 认证 ===
    md.new_header(3, "认证方式", add_table_of_contents='n')
    md.new_line("```http\nAuthorization: Bearer {your_token}\n```")

    md.new_header(3, "请求头", add_table_of_contents='n')
    md.new_table(columns=api.header.columns, rows=api.header.rows, text=api.header.text, text_align='left')

    md.new_header(3, "请求参数", add_table_of_contents='n')
    md.new_table(columns=api.param.columns, rows=api.param.rows, text=api.param.text, text_align='left')

    # 示例代码
    md.new_header(3, "请求示例", add_table_of_contents='n')
    md.insert_code(api.request, 'json')

    md.new_header(3, "响应示例", add_table_of_contents='n')
    md.insert_code(api.response, 'json')

    # md.new_header(2, "目录")
    # md.new_list(
    #     [
    #         "[认证方式](#认证方式)",
    #         "[全局参数](#全局参数)",
    #         "[错误代码](#错误代码)",
    #         *[f"[{interface['name']}](#{interface['name'].replace(' ', '-')})" for interface in api_spec['interfaces']],
    #     ]
    # )
    md.new_line('---')


def generate_markdown(request_uid: str = '') -> str:
    data = _data_from_db(request_uid)

    md = MdUtils(file_name="API-DOC", title=data.title, author=data.author)
    # === 文档头 ===
    md.new_header(1, data.title)
    md.new_line(f"> **更新日期**: {datetime.now().strftime('%Y-%m-%d')}")
    md.new_line(f"> **版本**: {data.version}")
    md.new_list([f"- **{url.name}**: `{url.url}`" for url in data.base_url])

    md.new_header(2, "接口目录")
    md.new_list([f"[{api.path}](#{api.uid})" for api in data.apis])

    # api 文档
    _ = [_api_markdown(api, md=md) for api in data.apis]

    # === 附录 ===
    md.new_header(2, "附录")
    md.new_line("### 速率限制")
    md.new_list(["认证用户：1000次请求/小时", "匿名用户：100次请求/小时"])

    return md.file_data_text
