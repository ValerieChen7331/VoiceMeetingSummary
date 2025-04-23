from langchain_openai import ChatOpenAI
from config import Config
from langchain_community.llms import Ollama

# 🔹 **LLM 摘要生成**
class LLMTextSummarizer:
    """使用 LLM 生成文本摘要"""
    @staticmethod
    def summary_generator(chunks, prompt_template):
        """
        使用 LLM 對文本分段進行摘要生成

        參數：
        chunks (list): 分段的文本列表
        prompt_template (str): 摘要提示語模板，需包含 {context} 占位符

        回傳：
        str: 所有段落摘要的合併結果
        """
        # 初始化 LLM 模型 (這裡使用的是 Ollama 自架模型)
        # model = ChatOpenAI(
        #     api_key="ollama",
        #     model=Config.LLM_MODEL_NAME,
        #     base_url=Config.LLM_API_BASE_URL
        # )
        model = Ollama(base_url=Config.LLM_API_BASE_URL, model=Config.LLM_MODEL_NAME)
        summaries = []

        # 逐段處理文本
        for chunk in chunks:
            # 將當前段落帶入提示模板中
            prompt = prompt_template.format(context=chunk)
            # 呼叫 LLM 模型進行摘要生成
            response = model.invoke(prompt)
            # 如果模型有回應，且內容存在，加入摘要結果
            if response and response.content:
                summaries.append(response.content)

        # 將所有摘要段落合併為單一文本並回傳
        return "\n".join(summaries)
