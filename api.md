# 生成效果示例：

## 创建用户 <a id="创建用户">cgq</a>

**接口地址**: `/api/v1/users`
**请求方法**: `POST`
**描述**: 创建新用户

### 请求体参数

| 参数名        | 类型     | 必填 | 说明   | 示例                 |
|------------|--------|----|------|--------------------|
| `username` | string | ✅  | 用户名  | `john_doe`         |
| `email`    | string | ✅  | 邮箱地址 | `john@example.com` |

### 请求示例

```json
{
  "username": "john_doe",
  "email": "john@example.com"
}
```