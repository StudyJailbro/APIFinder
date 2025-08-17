import requests
from bs4 import BeautifulSoup
import config
import mimetypes
from .utils import color_print, error_print, process_url, find_last_occurrences

class Crawler:
    """网页爬虫类，负责获取网页内容和链接"""
    
    def __init__(self, cookie=None, timeout=config.TIMEOUT):
        """初始化爬虫"""
        self.session = requests.Session()
        self.headers = {
            "User-Agent": config.USER_AGENT,
            "Cookie": cookie if cookie else ""
        }
        self.timeout = timeout
        self.visited_urls = set()
        self.external_scripts = set()
        self.external_stylesheets = set()
        
    def fetch_content(self, url):
        """获取URL内容"""
        try:
            response = self.session.get(
                url, 
                headers=self.headers, 
                timeout=self.timeout, 
                verify=False,
                allow_redirects=True
            )
            response.raise_for_status()  # 抛出HTTP错误
            return response.content.decode("utf-8", "ignore")
        except requests.exceptions.RequestException as e:
            error_print(f"获取 {url} 内容失败: {str(e)}")
            return None
    
    def get_scripts(self, url, html_content=None):
        """从HTML中提取所有脚本内容和外部脚本URL"""
        if not html_content:
            html_content = self.fetch_content(url)
            if not html_content:
                return {}

        soup = BeautifulSoup(html_content, "html.parser")
        scripts = soup.find_all("script")
        script_contents = {}

        # 内联脚本
        inline_script = ""
        for script in scripts:
            if not script.get("src"):
                inline_script += script.get_text() + "\n\n"

        if inline_script:
            script_contents[url + "#inline-script"] = inline_script

        # 外部脚本
        for script in scripts:
            src = script.get("src")
            if src:
                script_url = process_url(url, src)
                if script_url and script_url not in self.external_scripts:
                    self.external_scripts.add(script_url)
                    color_print(f"发现外部脚本: {script_url}")
                    script_content = self.fetch_content(script_url)
                    if script_content:
                        script_contents[script_url] = script_content

        return script_contents

    def get_stylesheets(self, url, html_content=None):
        """从HTML中提取所有样式表内容和外部样式表URL"""
        if not html_content:
            html_content = self.fetch_content(url)
            if not html_content:
                return {}

        soup = BeautifulSoup(html_content, "html.parser")
        stylesheets = soup.find_all("link", rel="stylesheet")
        style_contents = {}

        # 内联样式
        style_tags = soup.find_all("style")
        inline_style = ""
        for style in style_tags:
            inline_style += style.get_text() + "\n\n"

        if inline_style:
            style_contents[url + "#inline-style"] = inline_style

        # 外部样式表
        for stylesheet in stylesheets:
            href = stylesheet.get("href")
            if href:
                style_url = process_url(url, href)
                if style_url and style_url not in self.external_stylesheets:
                    self.external_stylesheets.add(style_url)
                    color_print(f"发现外部样式表: {style_url}")
                    style_content = self.fetch_content(style_url)
                    if style_content:
                        style_contents[style_url] = style_content

        return style_contents

    def get_html_elements(self, url, html_content=None):
        """从HTML中提取可能包含API的元素"""
        if not html_content:
            html_content = self.fetch_content(url)
            if not html_content:
                return []

        soup = BeautifulSoup(html_content, "html.parser")
        elements_with_api = []

        # 提取表单action
        forms = soup.find_all("form")
        for form in forms:
            action = form.get("action")
            if action:
                elements_with_api.append(("form_action", process_url(url, action)))

        # 提取data-api属性
        for tag in soup.find_all(lambda t: t.has_attr("data-api")):
            api_url = tag["data-api"]
            if api_url:
                elements_with_api.append(("data_api", process_url(url, api_url)))

        # 提取其他可能包含API的属性
        for tag in soup.find_all(lambda t: t.has_attr("data-url")):
            data_url = tag["data-url"]
            if data_url:
                elements_with_api.append(("data_url", process_url(url, data_url)))

        return elements_with_api
    
    def find_links(self, url, html_content=None):
        """从HTML中提取所有链接"""
        if not html_content:
            html_content = self.fetch_content(url)
            if not html_content:
                return []
        
        soup = BeautifulSoup(html_content, "html.parser")
        links = []
        
        for a_tag in soup.find_all("a"):
            href = a_tag.get("href")
            if href:
                full_url = process_url(url, href)
                if full_url and full_url not in links:
                    links.append(full_url)
        
        return links
    
    def deep_crawl(self, start_url, max_depth=config.MAX_DEPTH, max_urls=config.MAX_URLS):
        """深度爬取网站"""
        color_print(f"开始深度爬取: {start_url} (最大深度: {max_depth})")
        
        crawl_queue = [(start_url, 1)]  # (url, depth)
        all_links = []
        
        while crawl_queue and len(self.visited_urls) < max_urls:
            url, depth = crawl_queue.pop(0)
            
            if url in self.visited_urls:
                continue
                
            if depth > max_depth:
                continue
                
            self.visited_urls.add(url)
            color_print(f"正在爬取: {url} (深度: {depth})")
            
            # 获取页面内容
            html_content = self.fetch_content(url)
            if not html_content:
                continue
                
            # 查找页面中的链接
            page_links = self.find_links(url, html_content)
            for link in page_links:
                if link not in self.visited_urls and link not in [u for u, d in crawl_queue]:
                    all_links.append(link)
                    crawl_queue.append((link, depth + 1))
        
        color_print(f"深度爬取完成，共访问 {len(self.visited_urls)} 个URL")
        return list(self.visited_urls)
