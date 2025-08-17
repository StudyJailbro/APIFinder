import re
import config
from urllib.parse import urlparse
from .utils import color_print, is_api_path, process_url

class APIExtractor:
    """API提取器类，负责从内容中提取API信息"""
    
    def __init__(self, api_dictionary=None):
        """初始化提取器，加载正则表达式和API字典"""
        self.api_patterns = re.compile(config.API_REGEX_PATTERNS, re.VERBOSE | re.IGNORECASE)
        self.api_dictionary = api_dictionary or []
        self.found_apis = set()  # 用于去重
        # 添加CSS URL匹配模式
        self.css_url_pattern = re.compile(r'url\(\s*[\'"]([^\'")]+)[\'"]?\s*\)', re.IGNORECASE)
        
    def extract_apis(self, content, base_url=None):
        """从内容中提取API信息"""
        if not content:
            return []
            
        api_info = []
        matches = self.api_patterns.finditer(str(content))
        
        for match in matches:
            group = match.group().strip('"').strip("'")
            
            # 检查HTTP方法
            if group.upper() in ["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS", "HEAD"]:
                api_info.append(("method", group.upper()))
            
            # 检查fetch/axios调用
            elif match.group(3):
                url = match.group(3)
                if self._is_valid_api(url):
                    api_info.append(("url", url))
            
            # 检查jQuery AJAX调用
            elif match.group(4):
                url = match.group(4)
                if self._is_valid_api(url):
                    api_info.append(("url", url))
            
            # 其他URL匹配
            elif group and self._is_valid_api(group):
                api_info.append(("url", group))
        
        # 如果有API字典，进行额外检查
        if self.api_dictionary:
            self._check_dictionary_matches(content, api_info)
            
        return api_info
    
    def _is_valid_api(self, url):
        """检查是否为有效的API URL"""
        if not url:
            return False
            
        # 避免重复
        if url in self.found_apis:
            return False
            
        # 检查基本API模式
        basic_patterns = ["/api/", "/v1/", "/v2/", "/rest/", "/graphql", "/rpc/"]
        for pattern in basic_patterns:
            if pattern in url.lower():
                self.found_apis.add(url)
                return True
                
        # 检查字典模式
        if is_api_path(url, self.api_dictionary):
            self.found_apis.add(url)
            return True
            
        return False
    
    def _check_dictionary_matches(self, content, api_info):
        """使用字典检查内容中的API路径"""
        # 简化内容，便于匹配
        simplified_content = content.replace('"', ' ').replace("'", ' ').replace('/', ' / ')

        for pattern in self.api_dictionary:
            # 创建匹配模式，考虑前后可能的字符
            regex_pattern = r'\b' + re.escape(pattern) + r'\b'
            if re.search(regex_pattern, simplified_content, re.IGNORECASE):
                # 确保不添加重复项
                if not any(item[0] == "url" and item[1] == pattern for item in api_info):
                    api_info.append(("url", pattern))
                    self.found_apis.add(pattern)

    def extract_apis_from_html_elements(self, elements, base_url=None):
        """从HTML元素中提取API信息"""
        api_info = []
        for element_type, value in elements:
            if value and self._is_valid_api(value):
                api_info.append(("url", value))
        return api_info

    def extract_apis_from_css(self, css_content, base_url=None):
        """从CSS内容中提取API信息"""
        api_info = []
        if not css_content:
            return api_info

        # 匹配CSS中的URL
        matches = self.css_url_pattern.finditer(css_content)
        for match in matches:
            url = match.group(1)
            if url and self._is_valid_api(url):
                # 处理相对URL
                if base_url and not url.startswith(('http://', 'https://')):
                    url = process_url(base_url, url)
                api_info.append(("url", url))

        # 检查CSS中的API字典匹配
        self._check_dictionary_matches(css_content, api_info)

        return api_info
