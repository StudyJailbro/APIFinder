import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 默认配置
DEFAULT_USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
DEFAULT_TIMEOUT = 10
DEFAULT_MAX_DEPTH = 2
DEFAULT_MAX_URLS = 100
DEFAULT_API_DICTIONARY = "api_dictionary.txt"

# 从环境变量获取配置，没有则使用默认值
USER_AGENT = os.getenv("USER_AGENT", DEFAULT_USER_AGENT)
TIMEOUT = int(os.getenv("TIMEOUT", DEFAULT_TIMEOUT))
MAX_DEPTH = int(os.getenv("MAX_DEPTH", DEFAULT_MAX_DEPTH))
MAX_URLS = int(os.getenv("MAX_URLS", DEFAULT_MAX_URLS))
API_DICTIONARY = os.getenv("API_DICTIONARY", DEFAULT_API_DICTIONARY)

# 颜色配置
COLORS = {
    "INFO": "\033[94m",    # 蓝色
    "SUCCESS": "\033[92m", # 绿色
    "WARNING": "\033[93m", # 黄色
    "ERROR": "\033[91m",   # 红色
    "RESET": "\033[0m"     # 重置
}

# API 正则表达式模式
API_REGEX_PATTERNS = r"""
    # 匹配 API 路径和方法
    (?:["']|(?:method:\s*["']))
    (
        # 常见 API 路径模式
        (?:/api/|/v\d+/|/rest/|/service/|/interface/|/action/|/graphql|/rpc/)[\w\-/]+
        (?:\?[\w=&%\-]*|)
        |
        # 完整 URL 形式的 API
        (?:[a-zA-Z]{1,10}://|//)[^"'/]{1,}\.[a-zA-Z]{2,}[^"']{0,}/(?:api/|v\d+/|rest/)[\w\-/?=&%]+
    )
    (?:["']|(?=["']))
    |
    # 匹配 HTTP 方法
    (?:method:\s*["'])(GET|POST|PUT|DELETE|PATCH|OPTIONS|HEAD)(?:["'])
    |
    # 匹配 fetch/axios 调用
    (?:fetch|axios)\s*\(\s*["']([^"']+?)["']
    |
    # 匹配 jQuery AJAX 调用
    \$.ajax\(\s*\{[^}]*(?:url|url)\s*:\s*["']([^"']+?)["']
"""
