from langchain_openai import ChatOpenAI
from config import Config
from langchain_community.llms import Ollama

# 🔹 **LLM 摘要生成**
class LLMTextSummarizer:
    """使用 LLM 生成文本摘要"""
    @staticmethod
    def summary_generator(chunks, prompt):
        """
        使用 LLM 對文本分段進行摘要生成

        參數：
        chunks (list): 分段的文本列表
        prompt_template (str): 摘要提示語模板，需包含 {context} 占位符

        回傳：
        str: 所有段落摘要的合併結果
        """
        prompt_template = prompt + "逐字稿：{context}"
        # 初始化 LLM 模型（這裡使用的是 Ollama 自架模型）
        model = Ollama(base_url=Config.LLM_API_BASE_URL, model=Config.LLM_MODEL_NAME)
        summaries = []

        # 逐段處理文本
        for chunk in chunks:
            prompt = prompt_template.format(context=chunk)
            response = model.invoke(prompt)
            if response:
                summaries.append(response)

        return "\n".join(summaries)
