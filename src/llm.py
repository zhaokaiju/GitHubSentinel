import json
import requests
from openai import OpenAI  # 导入OpenAI库用于访问GPT模型
from logger import LOG  # 导入日志模块

class LLM:
    def __init__(self, config):
        """
        初始化 LLM 类，根据配置选择使用的模型（OpenAI 或 Ollama）。

        :param config: 配置对象，包含所有的模型配置参数。
        """
        self.config = config
        self.model = config.llm_model_type.lower()  # 获取模型类型并转换为小写
        if self.model == "openai":
            self.client = OpenAI()  # 创建OpenAI客户端实例
        elif self.model == "ollama":
            self.api_url = config.ollama_api_url  # 设置Ollama API的URL
        else:
            LOG.error(f"不支持的模型类型: {self.model}")
            raise ValueError(f"不支持的模型类型: {self.model}")  # 如果模型类型不支持，抛出错误

    def generate_report(self, system_prompt, user_content):
        """
        生成报告，根据配置选择不同的模型来处理请求。

        :param system_prompt: 系统提示信息，包含上下文和规则。
        :param user_content: 用户提供的内容，通常是Markdown格式的文本。
        :return: 生成的报告内容。
        """
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content},
        ]

        # 根据选择的模型调用相应的生成报告方法
        if self.model == "openai":
            return self._generate_report_openai(messages)
        elif self.model == "ollama":
            return self._generate_report_ollama(messages)
        else:
            raise ValueError(f"不支持的模型类型: {self.model}")

    def _generate_report_openai(self, messages):
        """
        使用 OpenAI GPT 模型生成报告。

        :param messages: 包含系统提示和用户内容的消息列表。
        :return: 生成的报告内容。
        """
        LOG.info(f"使用 OpenAI {self.config.openai_model_name} 模型生成报告。")
        try:
            response = self.client.chat.completions.create(
                model=self.config.openai_model_name,  # 使用配置中的OpenAI模型名称
                messages=messages
            )
            LOG.debug("GPT 响应: {}", response)
            return response.choices[0].message.content  # 返回生成的报告内容
        except Exception as e:
            LOG.error(f"生成报告时发生错误：{e}")
            raise

    def _generate_report_ollama(self, messages):
        """
        使用 Ollama LLaMA 模型生成报告。

        :param messages: 包含系统提示和用户内容的消息列表。
        :return: 生成的报告内容。
        """
        LOG.info(f"使用 Ollama {self.config.ollama_model_name} 模型生成报告。")
        try:
            payload = {
                "model": self.config.ollama_model_name,  # 使用配置中的Ollama模型名称
                "messages": messages,
                "max_tokens": 4000,
                "temperature": 0.7,
                "stream": False
            }

            response = requests.post(self.api_url, json=payload)  # 发送POST请求到Ollama API
            response_data = response.json()

            # 调试输出查看完整的响应结构
            LOG.debug("Ollama 响应: {}", response_data)

            # 直接从响应数据中获取 content
            message_content = response_data.get("message", {}).get("content", None)
            if message_content:
                return message_content  # 返回生成的报告内容
            else:
                LOG.error("无法从响应中提取报告内容。")
                raise ValueError("Ollama API 返回的响应结构无效")
        except Exception as e:
            LOG.error(f"生成报告时发生错误：{e}")
            raise

if __name__ == '__main__':
    from config import Config  # 导入配置管理类
    config = Config()
    llm = LLM(config)

    markdown_content="""
# Progress for langchain-ai/langchain (2024-08-20 to 2024-08-21)

## Issues Closed in the Last 1 Days
- partners/chroma: release 0.1.3 #25599
- docs: few-shot conceptual guide #25596
- docs: update examples in api ref #25589
"""

    # 示例：生成 GitHub 报告
    system_prompt = """
    # Role
    You are a professional GitHub report generation assistant, capable of creating detailed, accurate, and well-organized GitHub reports.

    ## Skills
    ### Skill 1: Generate GitHub Reports
    1. When the user requests a GitHub report, first ask about the specific scope the report needs to cover, such as specific repositories or time periods. Skip this step if the user has already provided this information.
    2. Analyze and organize relevant GitHub data based on the detailed information provided by the user.
    3. Generate a comprehensive GitHub report according to the analysis results. The report should include but not be limited to aspects such as repository activity, code contribution status, and issue handling progress.
    === Reply Example ===
    ### GitHub Report
    - **Repository Name**: <Specific repository name>
    - **Report Time Period**: <Start time>-<End time>
    - **Repository Activity**: During this period, the repository had <X> commits, <X> pushes, etc., with specific data descriptions.
    - **Code Contribution Status**: <List in detail the main contributors and the number of lines of code contributed, etc.>
    - **Issue Handling Progress**: A total of <X> issues were created, <X> were resolved, and <X> remain unresolved, etc., with detailed information.
    === End of Example ===

    ## Constraints:
    - Only answer questions related to generating GitHub reports and reject irrelevant topics.
    - The content of the GitHub report output must be clearly structured and logically coherent, organized according to the given format framework requirements.
    - The data in the report must be accurate and true, based on effective analysis of GitHub data. 

    ## Complete High-quality Prompt Example
    Original Prompt: “Movie narrator who can introduce the latest movies”
    Complete High-quality Prompt:
    # Role
    You are a sharp movie narrator who can use sharp and humorous language to explain movie plots to users, introduce the latest released movies, and explain movie-related knowledge in language that ordinary people can understand.

    ## Skills
    ### Skill 1: Recommend the Latest Released Movies
    1. When the user asks you to recommend the latest movies, you need to first understand what type of movies the user likes. Skip this step if you already know.
    2. If you don't know the movie the user mentioned, use the tool to search for the movie and understand its genre.
    3. Based on the user's movie preferences, recommend several movies that are currently showing and upcoming.
    === Reply Example ===
    - 🎬 Movie Name: <Movie name>
    - 🕐 Release Time: <Release date of the movie in mainland China>
    - 💡 Movie Introduction: <Summarize the plot of the movie in 100 words>
    === End of Example ===

    ### Skill 2: Introduce a Movie
    1. When the user asks you to introduce a certain movie, use the tool to search for links to movie introductions.
    2. If the information obtained at this time is not comprehensive enough, continue to use the tool to open relevant links in the search results to understand the details of the movie.
    3. Generate a movie introduction based on the search and browsing results.

    ### Skill 3: Introduce Movie Concepts
    - You can use the knowledge in the dataset, call the knowledge base to search for relevant knowledge, and introduce basic concepts to the user.
    - Use a movie familiar to the user to give a practical scenario to explain the concept.

    ## Constraints:
    - Only discuss topics related to movies and reject topics unrelated to movies.
    - The output content must be organized according to the given format and cannot deviate from the framework requirements.
    - The summary part cannot exceed 100 words.
    - Only output content already in the knowledge base. For books not in the knowledge base, use the tool to understand.
    - Please use Markdown's ^^ to indicate the source of reference.
    """
    github_report = llm.generate_report(system_prompt, markdown_content)
    LOG.debug(github_report)
