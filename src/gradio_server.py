import gradio as gr  # 导入gradio库用于创建GUI

from config import Config  # 导入配置管理模块
from github_client import GitHubClient  # 导入用于GitHub API操作的客户端
from report_generator import ReportGenerator  # 导入报告生成器模块
from llm import LLM  # 导入可能用于处理语言模型的LLM类
from subscription_manager import SubscriptionManager  # 导入订阅管理器
from logger import LOG  # 导入日志记录器

# 创建各个组件的实例
config = Config()
github_client = GitHubClient(config.github_token)
llm = LLM()
report_generator = ReportGenerator(llm)
subscription_manager = SubscriptionManager(config.subscriptions_file)


def export_progress_by_date_range(repo, days):
    # 定义一个函数，用于导出和生成指定时间范围内项目的进展报告
    raw_file_path = github_client.export_progress_by_date_range(repo, days)  # 导出原始数据文件路径
    report, report_file_path = report_generator.generate_report_by_date_range(raw_file_path, days)  # 生成并获取报告内容及文件路径

    return report, report_file_path  # 返回报告内容和报告文件路径


# 创建Gradio界面
github_sentinel_app = gr.Blocks(
    title="GitHubSentinel - 项目进展追踪",
    theme=gr.themes.Soft(primary_hue="emerald"),  # 使用现代主题
    css=".report-box {border: 1px solid #e0e0e0; border-radius: 8px; padding: 20px; margin-top: 20px}"
)

with github_sentinel_app:
    gr.Markdown("# 🛰️ GitHubSentinel")
    gr.Markdown("### 追踪订阅的GitHub项目进展")

    with gr.Row():
        with gr.Column(scale=3):
            project = gr.Dropdown(
                subscription_manager.list_subscriptions(),
                label="选择订阅项目",
                info="从已订阅项目中选择",
                interactive=True
            )
            time_range = gr.Slider(
                value=2,
                minimum=1,
                maximum=7,
                step=1,
                label="报告周期(天)",
                info="选择要追踪的时间范围"
            )
            submit_btn = gr.Button("生成报告", variant="primary")

        with gr.Column(scale=2):
            gr.Markdown("### 使用说明")
            gr.Markdown("""
            1. 从下拉菜单选择GitHub项目  
            2. 设置报告周期(1-7天)  
            3. 点击"生成报告"按钮  
            4. 查看报告并下载  
            """)

    with gr.Row():
        with gr.Column():
            gr.Markdown("## 📊 项目进展报告")
            report_output = gr.Markdown(elem_classes="report-box")
        with gr.Column():
            gr.Markdown("## 📥 下载报告")
            file_output = gr.File(label="报告文件", file_count="single")

    # 交互逻辑
    submit_btn.click(
        fn=export_progress_by_date_range,
        inputs=[project, time_range],
        outputs=[report_output, file_output]
    )

if __name__ == "__main__":
    github_sentinel_app.launch(share=True, server_name="0.0.0.0")  # 启动界面并设置为公共可访问
    # 可选带有用户认证的启动方式
    # github_sentinel_app.launch(share=True, server_name="0.0.0.0", auth=("yudao", "Abc123"))
