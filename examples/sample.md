# md_to_html 用户指南

这是一份功能演示文档，展示 md_to_html 对各类 Markdown 语法的渲染效果。

## 文本格式

这是 **加粗**、*斜体*、~~删除线~~、`行内代码` 和 [链接](https://example.com) 的展示效果。

> 知识不是力量，分享知识才是力量。
> —— 这句话用引用来展现，左侧有醒目的大竖线。

## 列表

### 无序列表

- Rust: 高性能系统编程语言
- Python: 优雅的通用编程语言
- TypeScript: 带类型的 JavaScript

### 有序列表

1. 需求分析
2. 架构设计
3. 编码实现
4. 测试验证

### 任务列表

- [x] 完成核心转换引擎
- [x] 实现代码高亮
- [x] 设计响应式 CSS
- [ ] 添加暗色模式
- [ ] 支持自定义主题

## 代码

### Python 示例

```python
import asyncio
from dataclasses import dataclass


@dataclass
class User:
    name: str
    age: int


async def greet(user: User) -> str:
    await asyncio.sleep(0.1)
    return f"Hello, {user.name}!"


async def main():
    user = User(name="Alice", age=30)
    message = await greet(user)
    print(message)


if __name__ == "__main__":
    asyncio.run(main())
```

### Rust 示例

```rust
use std::collections::HashMap;

#[derive(Debug)]
struct Config {
    host: String,
    port: u16,
    max_connections: u32,
}

impl Config {
    fn new(host: &str, port: u16) -> Self {
        Self {
            host: host.to_string(),
            port,
            max_connections: 100,
        }
    }
}

fn main() {
    let config = Config::new("localhost", 8080);
    println!("{:#?}", config);
}
```

### TypeScript 示例

```typescript
interface ApiResponse<T> {
  data: T;
  status: number;
  message: string;
}

async function fetchData<T>(url: string): Promise<ApiResponse<T>> {
  const response = await fetch(url);
  if (!response.ok) {
    throw new Error(`HTTP ${response.status}`);
  }
  return response.json();
}
```

### 无语言标记的代码

```
$ md_to_html 输入文件.md --toc
✅ 已生成: 输入文件.html
```

## 表格

| 特性 | md_to_html | GitHub | Medium |
|------|-----------|--------|--------|
| 代码高亮 | ✅ Catppuccin | ✅ 基础 | ❌ |
| 自动目录 | ✅ | ✅ | ❌ |
| 响应式设计 | ✅ | ✅ | ✅ |
| 离线使用 | ✅ | ❌ | ❌ |
| 自定义 CSS | ✅ | ❌ | ❌ |

## 数学公式（扩展）

行内公式 `$E = mc^2$` 和块级公式：

$$ \sum_{k=1}^{n} k = \frac{n(n+1)}{2} $$

## 图片

![Placeholder](https://placehold.co/800x300/4f6ef7/ffffff?text=md_to_html+Banner)

## 多层嵌套

> ### 嵌套引用
>
> 引用中可以包含其他元素：
>
> - 列表项 1
> - 列表项 2
>
> ```python
> print("引用内的代码块")
> ```
>
> 引用可以在 **嵌套引用** > *嵌套引用* > ~~嵌套引用~~ 中继续嵌套：
>
> > 这是第二层嵌套
> >
> > > 这是第三层嵌套

## 结语

md_to_html 让你的 Markdown 文档具有接近专业出版物的阅读体验，特别适合 AI 生成的文档、技术博客、项目文档等场景。
