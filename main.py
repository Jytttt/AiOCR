#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import base64
import requests
import json
import re
from pathlib import Path



def extract_text_from_images(image_paths, base_url, api_key, model, translate_to):
    """
    在单个请求中使用 OpenAI 的 Vision API 从多张图片中提取文本。

    参数:
        image_paths (list): 图片文件路径的列表。
        base_url (str): OpenAI API 的基础 URL。
        api_key (str): OpenAI API 密钥。
        model (str): 要使用的 OpenAI 模型名称。

    返回值:
        list: 包含对应每张图片提取的文本的列表。
    """
    content_sub = f"并翻译为{translate_to}" if translate_to else ""
    
    # 准备包含多张图片特定指令的消息内容
    content = [
        {
            "type": "text",
            "text": f"对于每张图片，提取文本{content_sub}，可以适当根据前后文对原文进行纠错或补充。在每个图片文本前使用唯一的标识符格式化响应，例如：第一张图片文本前添加 '###IMAGE_1###'，第二张图片文本前添加 '###IMAGE_2###'，依此类推。不要包含任何额外的文本、注释或解释。"
        }
    ]

    
    # 将每张图片添加到内容数组中
    for i, image_path in enumerate(image_paths):
        with open(image_path, "rb") as image_file:
            base64_image = base64.b64encode(image_file.read()).decode('utf-8')

        content.append({
            "type": "image_url",
            "image_url": {
                "url": f"data:image/jpeg;base64,{base64_image}"
            }
        })

    # 准备 API 请求头
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    # 准备 API 请求载荷
    payload = {
        "model": model,
        "messages": [
            {
                "role": "user",
                "content": content
            }
        ],
        "max_tokens": 1_048_576
    }

    try:
        response = requests.post(
            f"{base_url}/chat/completions",
            headers=headers,
            json=payload
        )
        response.raise_for_status()
        result = response.json()

        # 从响应中提取组合文本
        if "choices" in result and len(result["choices"]) > 0:
            combined_text = result["choices"][0]["message"]["content"]

            # 使用自定义标记分割文本
            pattern = r'###IMAGE_\d+###'
            sections = re.split(pattern, combined_text)

            # 移除开头的空部分
            if sections and not sections[0].strip():
                sections = sections[1:]

            # 如果我们获得了预期数量的部分，则返回它们
            if len(sections) == len(image_paths):
                return [section.strip() for section in sections]
            else:
                # 返回可用的部分，不足的用空字符串补充
                print(f"警告：返回的部分数量 ({len(sections)}) 与图片数量 ({len(image_paths)}) 不匹配")
                sections.extend([''] * (len(image_paths) - len(sections)))
                return [section.strip() for section in sections[:len(image_paths)]]
        else:
            return [""] * len(image_paths)

    except requests.exceptions.RequestException as e:
        print(f"API 调用期间发生错误: {str(e)}")
        return [""] * len(image_paths)


def process_directory(input_dir, output_dir, base_url, api_key, model, bind=1, translate_to=None):
    """
    处理输入目录中的所有图片，并将提取的文本保存到输出目录中。

    参数:
        input_dir (str): 包含图片的输入目录。
        output_dir (str): 保存文本文件的输出目录。
        base_url (str): OpenAI API 的基础 URL。
        api_key (str): OpenAI API 密钥。
        model (str): 要使用的 OpenAI 模型名称。
        bind (int): 在单个 API 请求中处理的图片数量 (默认为 1)。
        translate_to (str): 要翻译的目标语言。
    """
    # 如果输出目录不存在，则创建它
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    # 支持的图片格式
    image_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.gif', '.webp']

    # 获取输入目录中的所有图片文件
    image_files = [f for f in os.listdir(input_dir)
                   if os.path.isfile(os.path.join(input_dir, f)) and
                   os.path.splitext(f)[1].lower() in image_extensions]

    print(f"找到 {len(image_files)} 张图片需要处理")

    # 以 'bind' 大小的批次处理图片
    for i in range(0, len(image_files), bind):
        batch = image_files[i:i+bind]
        batch_paths = [os.path.join(input_dir, img) for img in batch]

        print(f"正在处理第 {i//bind + 1} 批，包含 {len(batch)} 张图片...")

        # 从批处理的图片中提取文本
        try:
            extracted_texts = extract_text_from_images(batch_paths, base_url, api_key, model, translate_to)

            # 将每个提取的文本保存到其对应的文件中
            for j, image_file in enumerate(batch):
                if j < len(extracted_texts):  # 安全检查
                    text = extracted_texts[j]
                    
                    # 只有当文本不为空时才保存文件
                    if text.strip():
                        # 创建输出文件名（与输入文件名相同，但扩展名为 .txt）
                        base_name = os.path.splitext(image_file)[0]
                        output_file = os.path.join(output_dir, f"{base_name}.txt")

                        # 将提取的文本保存到文件
                        with open(output_file, 'w', encoding='utf-8') as f:
                            f.write(text)

                        print(f"提取的文本已保存到 {output_file}")
                    else:
                        print(f"图片 {image_file} 未提取到文本，跳过保存")
        except Exception as e:
            print(f"处理批处理时发生错误: {str(e)}")


def main():
    # 默认配置
    config = {
        "input": "ImageInput",
        "output": "TXTResults",
        "baseurl": "https://api.openai.com/v1",
        "api": "",
        "model": "gpt-4-vision-preview",
        "bind": 10,
        "translateTo": "简体中文",
    }

    # 从配置文件读取参数
    config_path = os.path.join(os.path.dirname(__file__), 'config.json')
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r', encoding='utf-8') as cfg_file:
                config_data = json.load(cfg_file)
                config.update(config_data)
            print(f"已从 {config_path} 加载配置")
        except Exception as e:
            print(f"读取配置文件时发生错误: {str(e)}，将使用默认配置")
    else:
        print(f"配置文件 {config_path} 不存在，将使用默认配置")

    # 处理目录
    process_directory(
        config["input"],
        config["output"],
        config["baseurl"],
        config["api"],
        config["model"],
        config["bind"],
        config.get("translateTo")
    )

    print("所有图片处理完成！")


if __name__ == "__main__":
    main()