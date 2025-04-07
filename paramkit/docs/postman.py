# !/usr/bin/env python3
# _*_ coding:utf-8 _*_
"""
@File     : postman.py
@Project  : 
@Time     : 2025/4/6 20:39
@Author   : dylan
@Contact Email: cgq2012516@163.com
"""
import json
from datetime import datetime


def generate_postman_collection(api_data, collection_name):
    """生成Postman集合文件"""
    items = []

    for api_name, details in api_data.items():
        request = {
            "name": api_name,
            "request": {
                "method": details["method"].upper(),
                "header": [],
                "url": {
                    "raw": "{{base_url}}" + details["path"],
                    "host": ["{{base_url}}"],
                    "path": details["path"].strip("/").split("/"),
                },
                "description": details.get("description", ""),
            },
            "response": [],
        }

        # 处理查询参数
        if "params" in details:
            request["request"]["url"]["query"] = [
                {
                    "key": param["name"],
                    "value": param.get("example", ""),
                    "description": param.get("description", ""),
                }
                for param in details["params"]
                if param["in"] == "query"
            ]

        # 处理请求体参数
        if details["method"].lower() == "post" and "params" in details:
            body_params = [param for param in details["params"] if param["in"] == "body"]
            if body_params:
                request["request"]["body"] = {
                    "mode": "raw",
                    "raw": json.dumps({p["name"]: p.get("example", "") for p in body_params}, indent=2),
                    "options": {"raw": {"language": "json"}},
                }

        items.append(request)

    collection = {
        "info": {
            "name": collection_name,
            "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json",
            "_postman_id": "{{generated_id}}",
            "description": "Auto-generated API collection",
            "updatedAt": datetime.now().isoformat(),
        },
        "item": items,
    }

    return json.dumps(collection, indent=2)
