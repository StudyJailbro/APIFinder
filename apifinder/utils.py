import re
from urllib.parse import urlparse
import config

def color_print(message, color="INFO"):
    """带颜色的打印函数"""
    color_code = config.COLORS.get(color.upper(), config.COLORS["RESET"])
    print(f"{color_code}[*] {message}{config.COLORS['RESET']}")

def error_print(message):
    """错误信息打印"""
    color_print(message, "ERROR")

def success_print(message):
    """成功信息打印"""
    color_print(message, "SUCCESS")

def warning_print(message):
    """警告信息打印"""
    color_print(message, "WARNING")

def process_url(base_url, relative_url):
    """将相对URL转换为绝对URL"""
    if not base_url or not relative_url:
        return None
        
    blacklist = ["javascript:", "#", "data:", "mailto:", "tel:"]
    for item in blacklist:
        if relative_url.startswith(item):
            return None
    
    parsed_base = urlparse(base_url)
    base_scheme = parsed_base.scheme
    base_netloc = parsed_base.netloc
    base_path = parsed_base.path
    
    # 处理完整URL
    if relative_url.startswith(("http://", "https://")):
        return relative_url
    
    # 处理//开头的URL
    if relative_url.startswith("//"):
        return f"{base_scheme}:{relative_url}"
    
    # 处理绝对路径
    if relative_url.startswith("/"):
        return f"{base_scheme}://{base_netloc}{relative_url}"
    
    # 处理相对路径
    if base_path.endswith("/"):
        return f"{base_scheme}://{base_netloc}{base_path}{relative_url}"
    else:
        return f"{base_scheme}://{base_netloc}{'/'.join(base_path.split('/')[:-1])}/{relative_url}"

def find_last_occurrences(string, substring):
    """查找子字符串在字符串中所有出现的位置"""
    positions = []
    last_pos = -1
    while True:
        pos = string.find(substring, last_pos + 1)
        if pos == -1:
            break
        last_pos = pos
        positions.append(pos)
    return positions

def load_api_dictionary(file_path=None):
    """加载API路径字典"""
    api_patterns = []
    
    # 如果没有指定路径，使用默认路径
    if not file_path:
        file_path = config.API_DICTIONARY
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                # 跳过注释和空行
                if not line or line.startswith('#'):
                    continue
                api_patterns.append(line)
        
        color_print(f"成功加载API字典，共 {len(api_patterns)} 个模式", "SUCCESS")
        return api_patterns
        
    except FileNotFoundError:
        warning_print(f"API字典文件 {file_path} 未找到，将使用默认识别模式")
        return []
    except Exception as e:
        error_print(f"加载API字典时出错: {str(e)}")
        return []

def is_api_path(url, api_patterns):
    """检查URL是否匹配任何API模式"""
    if not url or not api_patterns:
        return False
        
    parsed_url = urlparse(url)
    path = parsed_url.path
    
    # 检查是否匹配任何字典模式
    for pattern in api_patterns:
        if pattern in path or path.startswith(pattern) or path.endswith(pattern):
            return True
    return False
