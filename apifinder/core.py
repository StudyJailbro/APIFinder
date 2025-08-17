from .crawler import Crawler
from .extractor import APIExtractor
from .processor import ResultProcessor
from .utils import color_print, success_print, load_api_dictionary

class APIFinderCore:
    """APIFinder核心类，协调各模块工作"""
    
    def __init__(self, cookie=None, api_dictionary_path=None):
        """初始化核心组件"""
        self.crawler = Crawler(cookie=cookie)
        self.api_dictionary = load_api_dictionary(api_dictionary_path)
        self.extractor = APIExtractor(self.api_dictionary)
        self.processor = ResultProcessor()
    
    def analyze_single_url(self, url):
        """分析单个URL"""
        color_print(f"开始分析URL: {url}")
        
        # 获取页面内容
        html_content = self.crawler.fetch_content(url)
        if not html_content:
            return False
        
        all_api_info = []
        
        # 获取并处理脚本内容
        scripts = self.crawler.get_scripts(url, html_content)
        if scripts:
            for script_url, content in scripts.items():
                color_print(f"从 {script_url} 提取API...")
                api_info = self.extractor.extract_apis(content, url)
                if api_info:
                    all_api_info.append(api_info)
        else:
            color_print("未找到任何脚本内容")
        
        # 获取并处理HTML元素
        html_elements = self.crawler.get_html_elements(url, html_content)
        if html_elements:
            color_print(f"从HTML元素中提取API...")
            api_info = self.extractor.extract_apis_from_html_elements(html_elements, url)
            if api_info:
                all_api_info.append(api_info)
        
        # 获取并处理样式表
        stylesheets = self.crawler.get_stylesheets(url, html_content)
        if stylesheets:
            for style_url, content in stylesheets.items():
                color_print(f"从 {style_url} 提取API...")
                api_info = self.extractor.extract_apis_from_css(content, url)
                if api_info:
                    all_api_info.append(api_info)
        
        # 处理提取的API
        if all_api_info:
            self.processor.process_apis(all_api_info, url)
            self.processor.extract_related_domains(url)
            self.processor.remove_duplicates()
            
            success_print(f"URL {url} 分析完成")
            return True
        else:
            color_print("未提取到任何API信息")
            return False
    
    def analyze_urls_from_file(self, file_path, is_js=False):
        """从文件分析多个URL"""
        color_print(f"从文件 {file_path} 加载URL...")
        
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                urls = [line.strip() for line in f if line.strip()]
            
            color_print(f"共加载 {len(urls)} 个URL")
            
            for i, url in enumerate(urls, 1):
                color_print(f"\n处理第 {i}/{len(urls)} 个URL: {url}")
                
                if is_js:
                    # 直接处理JS文件
                    content = self.crawler.fetch_content(url)
                    if content:
                        api_info = self.extractor.extract_apis(content, url)
                        if api_info:
                            self.processor.process_apis([api_info], url)
                else:
                    # 处理网页
                    self.analyze_single_url(url)
            
            self.processor.extract_subdomains(urls[0] if urls else "")
            self.processor.remove_duplicates()
            return True
            
        except Exception as e:
            from .utils import error_print
            error_print(f"处理文件时出错: {str(e)}")
            return False
    
    def deep_analyze(self, start_url, max_depth=None, max_urls=None):
        """深度分析网站"""
        # 获取所有要分析的URL
        urls = self.crawler.deep_crawl(
            start_url,
            max_depth=max_depth,
            max_urls=max_urls
        )
        
        # 分析每个URL
        for i, url in enumerate(urls, 1):
            color_print(f"\n分析第 {i}/{len(urls)} 个URL: {url}")
            self.analyze_single_url(url)
        
        self.processor.extract_subdomains(start_url)
        self.processor.remove_duplicates()
        return True
    
    def display_results(self):
        """展示结果"""
        self.processor.display_results()
    
    def save_results(self, output_api=None, output_url=None, output_subdomain=None):
        """保存结果"""
        self.processor.save_results(output_api, output_url, output_subdomain)
