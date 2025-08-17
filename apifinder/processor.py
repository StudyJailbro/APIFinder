from urllib.parse import urlparse
from .utils import color_print, success_print, find_last_occurrences

class ResultProcessor:
    """结果处理器，负责处理和分类提取的API"""
    
    def __init__(self):
        """初始化结果处理器"""
        self.categorized_apis = {
            "GET": [],
            "POST": [],
            "PUT": [],
            "DELETE": [],
            "PATCH": [],
            "OPTIONS": [],
            "HEAD": [],
            "UNKNOWN_METHOD": []
        }
        self.all_urls = set()
        self.related_domains = set()  # 存储所有相关域名
        self.domain_api_map = {}  # 存储域名和API的映射关系
    
    def process_apis(self, api_info_list, base_url):
        """处理API信息列表，按方法分类"""
        current_method = None
        
        for api_info in api_info_list:
            for item in api_info:
                type_, value = item
                if type_ == "method":
                    current_method = value
                elif type_ == "url" and value:
                    # 处理URL，转换为绝对URL
                    processed_url = self._process_api_url(base_url, value)
                    if processed_url:
                        self.all_urls.add(processed_url)
                        
                        # 根据当前方法分类
                        if current_method and current_method in self.categorized_apis:
                            self.categorized_apis[current_method].append(processed_url)
                            current_method = None  # 重置方法
                        else:
                            self.categorized_apis["UNKNOWN_METHOD"].append(processed_url)
    
    def _process_api_url(self, base_url, url):
        """处理API URL，确保是绝对URL"""
        if not url or not base_url:
            return None
            
        parsed_url = urlparse(url)
        parsed_base = urlparse(base_url)
        
        # 已经是完整URL
        if parsed_url.scheme and parsed_url.netloc:
            return url
            
        # 相对路径，需要拼接
        if url.startswith("/"):
            return f"{parsed_base.scheme}://{parsed_base.netloc}{url}"
        else:
            return f"{parsed_base.scheme}://{parsed_base.netloc}/{url.lstrip('/')}"
    
    def extract_related_domains(self, main_url):
        """提取所有相关域名（同一根域名下的所有域名）"""
        if not main_url or not self.all_urls:
            return
            
        parsed_main = urlparse(main_url)
        main_domain = parsed_main.netloc
        
        # 提取主域名的主要部分（去除www.等前缀）
        positions = find_last_occurrences(main_domain, ".")
        main_part = main_domain
        if len(positions) > 1:
            main_part = main_domain[positions[-2] + 1:]
        
        # 添加主域名到相关域名集合
        self.related_domains.add(main_domain)
        
        # 分析每个URL的域名
        for url in self.all_urls:
            parsed_url = urlparse(url)
            domain = parsed_url.netloc
            if domain and main_part in domain:
                self.related_domains.add(domain)
                
                # 建立域名和API的映射关系
                if domain not in self.domain_api_map:
                    self.domain_api_map[domain] = []
                if url not in self.domain_api_map[domain]:
                    self.domain_api_map[domain].append(url)
    
    def remove_duplicates(self):
        """去除重复的API和URL"""
        # 去重API
        for method in self.categorized_apis:
            unique_apis = []
            seen = set()
            for api in self.categorized_apis[method]:
                if api not in seen:
                    seen.add(api)
                    unique_apis.append(api)
            self.categorized_apis[method] = unique_apis
        
        # 去重URL
        self.all_urls = list(self.all_urls)
    
    def display_results(self):
        """展示处理后的结果"""
        # 统计总API数量
        total_apis = sum(len(apis) for apis in self.categorized_apis.values())
        
        success_print(f"\n发现 {total_apis} 个API端点:")
        for method, apis in self.categorized_apis.items():
            if apis:
                print(f"  {method}: {len(apis)} 个")
        
        success_print(f"\n发现 {len(self.all_urls)} 个URL")
        success_print(f"发现 {len(self.related_domains)} 个相关域名\n")
        
        # 详细展示API端点
        print("=" * 50)
        print("API端点详情:")
        print("=" * 50)
        
        for method, apis in self.categorized_apis.items():
            if apis:
                print(f"\n{method} ({len(apis)}):")
                print("-" * len(f"{method} ({len(apis)}):"))
                # 只显示前5个，其余计数
                for i, api in enumerate(apis[:5]):
                    print(f"  {api}")
                if len(apis) > 5:
                    print(f"  ... 还有 {len(apis) - 5} 个未显示")
        
        # 显示相关域名及其API
        if self.related_domains:
            print("\n" + "=" * 50)
            print("相关域名及API:")
            print("=" * 50)
            for domain in self.related_domains:
                print(f"\n域名: {domain}")
                print("-" * len(f"域名: {domain}"))
                if domain in self.domain_api_map and self.domain_api_map[domain]:
                    # 只显示前5个API，其余计数
                    for i, api in enumerate(self.domain_api_map[domain][:5]):
                        print(f"  {api}")
                    if len(self.domain_api_map[domain]) > 5:
                        print(f"  ... 还有 {len(self.domain_api_map[domain]) - 5} 个API未显示")
                else:
                    print("  无关联API")
    
    def save_results(self, output_api=None, output_url=None, output_subdomain=None):
        """保存结果到文件"""
        # 保存API端点
        if output_api:
            with open(output_api, "w", encoding="utf-8") as f:
                for method, apis in self.categorized_apis.items():
                    if apis:
                        f.write(f"{method} endpoints ({len(apis)}):\n")
                        for api in apis:
                            f.write(f"{api}\n")
                        f.write("\n")
            success_print(f"\n已将API端点保存到 {output_api}")
        
        # 保存URL
        if output_url:
            with open(output_url, "w", encoding="utf-8") as f:
                for url in self.all_urls:
                    f.write(f"{url}\n")
            success_print(f"已将URL保存到 {output_url}")
        
        # 保存子域名
        if output_subdomain:
            with open(output_subdomain, "w", encoding="utf-8") as f:
                for subdomain in self.subdomains:
                    f.write(f"{subdomain}\n")
            success_print(f"已将子域名保存到 {output_subdomain}")
