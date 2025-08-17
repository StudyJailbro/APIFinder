# APIFinder

APIFinder 是一个强大的 API 端点识别工具，能够从网页和 JavaScript 文件中智能提取 API 接口信息。它结合了正则表达式识别和自定义字典匹配，能够精准发现各种 API 路径模式，并按 HTTP 方法分类展示结果。

![APIFinder Logo](https://picsum.photos/800/200?random=1)

## 核心功能

- **多源 API 提取**：从网页、JavaScript 文件、CSS 文件和 HTML 元素中智能提取 API 端点
- **自定义 API 字典**：支持使用自定义 API 路径字典文件，提高特定网站的 API 识别准确性
- **智能模式识别**：自动识别常见 API 路径模式（/api/、/v1/、/rest/ 等）
- **HTTP 方法检测**：识别 GET、POST、PUT、DELETE 等 HTTP 请求方法
- **多类型 API 调用识别**：支持识别 fetch、axios、jQuery.ajax 等多种 JavaScript API 调用方式
- **结果分类展示**：按 HTTP 方法分类展示 API 端点，便于分析
- **深度爬取功能**：支持深度爬取网站，跟随页面链接发现更多 API
- **批量处理**：支持从文件读取多个 URL 或 JS 文件进行批量处理
- **结果导出**：支持将 API 端点、URL 和子域名等结果保存到文件

## 技术原理

APIFinder 主要由以下核心模块组成：
- **Crawler**：负责爬取网页内容、脚本文件和样式表
- **APIExtractor**：使用正则表达式和字典匹配从内容中提取 API 信息
- **ResultProcessor**：处理、分类和去重提取到的 API 信息
- **Utils**：提供辅助功能如 URL 处理、日志输出等

## 安装方法

```bash
# 克隆仓库
git clone https://github.com/StudyJailbro/apifinder.git
cd apifinder

# 创建并激活虚拟环境 (可选但推荐)
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

## 使用方法

### 命令行参数说明

以下是APIFinder支持的所有命令行参数的详细说明：

| 参数 | 长格式 | 描述 | 示例 |
|------|--------|------|------|
| `-h` | `--help` | 显示帮助信息并退出 | `python APIFinder.py -h` |
| `-u` | `--url` | 目标网站URL | `python APIFinder.py -u http://www.example.com` |
| `-c` | `--cookie` | 网站Cookie，用于访问需要登录的网站 | `python APIFinder.py -u http://www.example.com -c "sessionid=abc123; token=xyz789"` |
| `-f` | `--file` | 包含URL或JS文件的文件路径 | `python APIFinder.py -f urls.txt` |
| `-ou` | `--outputurl` | URL结果输出文件 | `python APIFinder.py -u http://www.example.com -ou all_urls.txt` |
| `-os` | `--outputsubdomain` | 子域名结果输出文件 | `python APIFinder.py -u http://www.example.com -os subdomains.txt` |
| `-oa` | `--outputapi` | API端点结果输出文件 | `python APIFinder.py -u http://www.example.com -oa api_results.txt` |
| `-j` | `--js` | 直接处理JS文件（与`-f`配合使用） | `python APIFinder.py -f js_files.txt -j` |
| `-d` | `--deep` | 启用深度爬取 | `python APIFinder.py -u http://www.example.com -d` |
| `-ad` | `--apidict` | API路径字典文件 | `python APIFinder.py -u http://www.example.com -ad api_dictionary.txt` |
| `-md` | `--maxdepth` | 最大爬取深度（默认：3） | `python APIFinder.py -u http://www.example.com -d -md 5` |
| `-mu` | `--maxurls` | 最大爬取URL数量（默认：200） | `python APIFinder.py -u http://www.example.com -d -mu 300` |

### 基本使用示例

从单个 URL 提取 API：
```bash
python APIFinder.py -u http://www.example.com
```

**示例输出：**
```
开始分析URL: http://www.example.com
从 http://www.example.com 提取API...
从HTML元素中提取API...
从 http://www.example.com/css/style.css 提取API...

API 端点发现结果:

GET 方法:
- /api/users
- /api/products
- /api/categories

POST 方法:
- /api/login
- /api/register

PUT 方法:
- /api/users/1

DELETE 方法:
- /api/users/1

其他 API:
- /api/data
- /v2/status

共发现 8 个 API 端点
APIFinder 分析完成
```

### 使用 API 字典

使用自定义字典文件提高 API 识别能力：
```bash
python APIFinder.py -u http://www.example.com -ad api_dictionary.txt
```

项目中已包含一个默认的 `api_dictionary.txt`，包含常见的 API 路径模式，例如：
```
# api_dictionary.txt 示例内容
/user
/products
/orders
/payment
/api/v2/
```

### 深度爬取

深度爬取会跟随页面中的链接，从更多页面提取 API：
```bash
python APIFinder.py -u http://www.example.com -d
```

指定最大爬取深度和最大 URL 数量：
```bash
python APIFinder.py -u http://www.example.com -d -md 3 -mu 150
```

**示例输出：**
```
开始分析URL: http://www.example.com
从 http://www.example.com 提取API...
发现链接: http://www.example.com/about
发现链接: http://www.example.com/contact
...

开始分析URL: http://www.example.com/about
从 http://www.example.com/about 提取API...
...

API 端点发现结果:
...
共发现 24 个 API 端点
已保存 150 个 URL 到 urls.txt
已保存 5 个子域名到 subdomains.txt
APIFinder 分析完成
```

### 保存结果

将结果保存到文件：
```bash
python APIFinder.py -u http://www.example.com -d \
    -oa api_results.txt \
    -ou all_urls.txt \
    -os subdomains.txt
```

参数说明：
- `-oa`: 保存 API 端点结果
- `-ou`: 保存所有发现的 URL
- `-os`: 保存发现的子域名
- `-ad`: 指定 API 路径字典文件

### 批量处理

从文件处理多个 URL：
```bash
python APIFinder.py -f urls.txt -ad custom_api_dict.txt
```

直接处理多个 JavaScript 文件：
```bash
python APIFinder.py -f js_files.txt -j
```

### 使用 Cookie

对于需要登录的网站，可以提供 Cookie 进行访问：
```bash
python APIFinder.py -u http://www.example.com -c "sessionid=abc123; token=xyz789"
```

## 配置

可以通过修改 `config.py` 或创建 `.env` 文件来调整工具行为：

```python
# config.py 示例内容
import os
from dotenv import load_dotenv

load_dotenv()

# 用户代理
USER_AGENT = os.getenv("USER_AGENT", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

# 超时时间（秒）
TIMEOUT = int(os.getenv("TIMEOUT", "15"))

# 深度爬取最大深度
MAX_DEPTH = int(os.getenv("MAX_DEPTH", "3"))

# 最大爬取URL数量
MAX_URLS = int(os.getenv("MAX_URLS", "200"))

# 默认API字典路径
API_DICTIONARY = os.getenv("API_DICTIONARY", "api_dictionary.txt")

# API正则表达式模式
API_REGEX_PATTERNS = r'''
    (?:GET|POST|PUT|DELETE|PATCH|OPTIONS|HEAD)\s+["']([^"']+)["']  # 方法+URL
    |
    (?:fetch|axios)\(["']([^"']+)["']  # fetch/axios调用
    |
    \.ajax\(\s*["']([^"']+)["']  # jQuery.ajax调用
    |
    ["']([^"']+?)/(?:api|v1|v2|rest|graphql)[^"']*["']  # 包含API路径的字符串
'''
```

```env
# .env 示例文件
USER_AGENT = "自定义用户代理字符串"
TIMEOUT = 15  # 超时时间（秒）
MAX_DEPTH = 3  # 深度爬取最大深度
MAX_URLS = 200  # 最大爬取URL数量
API_DICTIONARY = "path/to/your/dictionary.txt"  # 默认API字典路径
```

## 许可证

本项目采用 MIT 许可证 - 详见 LICENSE 文件
