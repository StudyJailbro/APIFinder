#!/usr/bin/env python
# coding: utf-8
"""
APIFinder - API端点识别工具
能够从网页和JavaScript文件中提取API端点，支持自定义路径字典
"""

import argparse
import sys
from requests.packages import urllib3
from apifinder.core import APIFinderCore
from apifinder.utils import color_print, error_print
import config

def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description="APIFinder - API端点识别工具",
        epilog='示例: \r\npython ' + sys.argv[0] + " -u http://www.example.com -ad api_dictionary.txt"
    )
    parser.add_argument("-u", "--url", help="目标网站URL")
    parser.add_argument("-c", "--cookie", help="网站Cookie")
    parser.add_argument("-f", "--file", help="包含URL或JS文件的文件路径")
    parser.add_argument("-ou", "--outputurl", help="URL结果输出文件")
    parser.add_argument("-os", "--outputsubdomain", help="子域名结果输出文件")
    parser.add_argument("-oa", "--outputapi", help="API端点结果输出文件")
    parser.add_argument("-j", "--js", help="直接处理JS文件", action="store_true")
    parser.add_argument("-d", "--deep", help="深度爬取", action="store_true")
    parser.add_argument("-ad", "--apidict", help="API路径字典文件")
    parser.add_argument("-md", "--maxdepth", type=int, help=f"最大爬取深度 (默认: {config.MAX_DEPTH})")
    parser.add_argument("-mu", "--maxurls", type=int, help=f"最大爬取URL数量 (默认: {config.MAX_URLS})")
    
    return parser.parse_args()

def main():
    """主函数"""
    # 禁用SSL警告
    urllib3.disable_warnings()
    
    # 解析命令行参数
    args = parse_args()
    
    # 检查参数合法性
    if not args.url and not args.file:
        error_print("请指定目标URL (-u) 或包含URL的文件 (-f)")
        sys.exit(1)
    
    # 初始化APIFinder核心
    finder = APIFinderCore(
        cookie=args.cookie,
        api_dictionary_path=args.apidict
    )
    
    # 执行分析
    try:
        if args.file:
            # 从文件分析
            finder.analyze_urls_from_file(args.file, is_js=args.js)
        else:
            # 从单个URL分析
            if args.deep:
                # 深度分析
                finder.deep_analyze(
                    args.url,
                    max_depth=args.maxdepth,
                    max_urls=args.maxurls
                )
            else:
                # 简单分析
                finder.analyze_single_url(args.url)
        
        # 显示结果
        finder.display_results()
        
        # 保存结果
        finder.save_results(
            output_api=args.outputapi,
            output_url=args.outputurl,
            output_subdomain=args.outputsubdomain
        )
        
        color_print("APIFinder 分析完成", "SUCCESS")
        
    except Exception as e:
        error_print(f"执行过程中出错: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
