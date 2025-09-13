import os
from openai import OpenAI

client = OpenAI(
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    api_key="sk-94008d6ff04d42e583e4aa661694b92a",  # 替换为你的实际API Key
)

completion = client.chat.completions.create(
    model="qwen-vl-plus",  # 此处以qwen-vl-plus为例，可按需更换模型名称。模型列表：https://help.aliyun.com/zh/model-studio/getting-started/models
    messages=[{"role": "user",
               "content": [
            {"type": "image_url",
             "image_url": {"url": "https://piglet-picgo.oss-cn-guangzhou.aliyuncs.com/PixPin_2025-08-22_17-16-12.png"}},
            {"type": "text", "text": "转换成三元组"},
            ]}]
    )
print(completion.model_dump_json())