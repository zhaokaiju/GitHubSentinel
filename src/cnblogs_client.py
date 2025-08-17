import os  # 导入os模块用于文件和目录操作
from datetime import datetime  # 导入datetime模块用于获取日期和时间

import requests  # 导入requests库用于HTTP请求
from bs4 import BeautifulSoup  # 导入BeautifulSoup库用于解析HTML内容

from logger import LOG  # 导入日志模块


class CnblogsTopicClient:
    def __init__(self):
        self.url = "https://www.cnblogs.com/pick/"

    def fetch_top_articles(self):
        LOG.debug("准备获取 cnblogs 的最新精华区博文。")
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                              "AppleWebKit/537.36 (KHTML, like Gecko) "
                              "Chrome/122.0.0.0 Safari/537.36"
            }

            response = requests.get(self.url, headers=headers, timeout=10)
            response.raise_for_status()  # 检查请求是否成功
            top_articles = self.parse_articles(response.text)  # 解析博文数据
            return top_articles
        except Exception as e:
            LOG.error(f"获取 cnblogs 的最新精华区博文失败：{str(e)}")
            return []

    def parse_articles(self, html_content):
        LOG.debug("解析 cnblogs 的最新精华区博文的HTML内容。")
        soup = BeautifulSoup(html_content, "html.parser")

        top_articles = []
        for item in soup.select(".post-item"):
            title_tag = item.select_one(".post-item-title")
            summary_tag = item.select_one(".post-item-summary")
            meta_tag = item.select_one(".post-meta")

            if title_tag:
                title = title_tag.get_text(strip=True)
                link = title_tag["href"]
                summary = summary_tag.get_text(strip=True) if summary_tag else ""
                meta = meta_tag.get_text(strip=True) if meta_tag else ""

                top_articles.append({
                    "title": title,
                    "link": link,
                    "summary": summary,
                    "meta": meta
                })

        LOG.info(f"成功解析 {len(top_articles)} 条 cnblogs 的最新精华区博文。")
        return top_articles

    def export_top_articles(self, date=None, hour=None):
        LOG.debug("准备导出 cnblogs 的最新精华区博文。")
        top_articles = self.fetch_top_articles()  # 获取新闻数据

        if not top_articles:
            LOG.warning("未找到任何 cnblogs 的最新精华区博文。")
            return None

        # 如果未提供 date 和 hour 参数，使用当前日期和时间
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
        if hour is None:
            hour = datetime.now().strftime('%H')

        # 构建存储路径
        dir_path = os.path.join('cnblogs_pick', date)
        os.makedirs(dir_path, exist_ok=True)  # 确保目录存在

        file_path = os.path.join(dir_path, f'{hour}.md')  # 定义文件路径
        with open(file_path, 'w') as file:
            file.write(f"# Cnblogs Topic Top articles ({date} {hour}:00)\n\n")
            for idx, article in enumerate(top_articles, start=1):
                file.write(f"{idx}. [{article['title']}]({article['link']})\n")

        LOG.info(f"cnblogs 的最新精华区博文文件生成：{file_path}")
        return file_path


if __name__ == "__main__":
    client = CnblogsTopicClient()
    client.export_top_articles()  # 默认情况下使用当前日期和时间
