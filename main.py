#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import yaml # 导入 yaml 库
from pathlib import Path

# 导入新的客户端模块
import openai_client
import genai_client # 取消注释 GenAI 客户端导入


def process_directory(input_dir, output_dir, client_type,
                      openai_base_url, openai_api_key, openai_model,
                      genai_api_key, genai_model,
                      bind=1, translate_to=None):
    """
    处理输入目录中的所有图片，并将提取的文本保存到输出目录中。

    参数:
        input_dir (str): 包含图片的输入目录。
        output_dir (str): 保存文本文件的输出目录。
        client_type (str): 要使用的客户端类型 ('openai' 或 'genai')。
        openai_base_url (str): OpenAI API 的基础 URL。
        openai_api_key (str): OpenAI API 密钥。
        openai_model (str): 要使用的 OpenAI 模型名称。
        genai_api_key (str): GenAI API 密钥。
        genai_model (str): 要使用的 GenAI 模型名称。
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
    
    # 按文件名排序以确保一致的处理顺序
    image_files.sort() 

    selectModel = f"{openai_model if client_type == 'openai' else genai_model}"
    print(f"找到 {len(image_files)} 张图片需要处理,调用 {client_type} : {selectModel}")

    # 以 'bind' 大小的批次处理图片
    for i in range(0, len(image_files), bind):
        batch = image_files[i:i+bind]
        batch_paths = [os.path.join(input_dir, img) for img in batch]

        print(f"正在处理第 {i//bind + 1} 批，包含 {len(batch)} 张图片...")

        # 从批处理的图片中提取文本
        try:
            extracted_texts = []
            if client_type == 'openai':
                 # 调用 OpenAI 客户端函数
                if not openai_api_key:
                    print("错误：OpenAI API 密钥未提供。")
                    continue
                extracted_texts = openai_client.extract_text_from_images(
                    batch_paths, openai_base_url, openai_api_key, openai_model, translate_to
                )
            elif client_type == 'genai': # 取消注释 GenAI 处理分支
                # 调用 GenAI 客户端函数
                if not genai_api_key:
                    print("错误：GenAI API 密钥未提供。")
                    continue
                # 注意：GenAI 不需要 base_url
                extracted_texts = genai_client.extract_text_from_images(
                    batch_paths, genai_api_key, genai_model, translate_to
                )
            else:
                print(f"错误：不支持的客户端类型 '{client_type}'")
                break # 跳出

            # 将每个提取的文本保存到其对应的文件中
            for j, image_file in enumerate(batch):
                if j < len(extracted_texts):  # 安全检查
                    text = extracted_texts[j]
                    
                    # 只有当文本不为空时才保存文件
                    if text and text.strip(): # 检查 text 是否为 None 或空字符串
                        # 创建输出文件名（与输入文件名相同，但扩展名为 .txt）
                        base_name = os.path.splitext(image_file)[0]
                        output_file = os.path.join(output_dir, f"{base_name}.txt")

                        # 将提取的文本保存到文件
                        with open(output_file, 'w', encoding='utf-8') as f:
                            f.write(text)

                        print(f"提取的文本已保存到 {output_file}")
                    else:
                        print(f"图片 {image_file} 未提取到文本或提取失败，跳过保存")
                else:
                     print(f"警告：图片 {image_file} 的提取文本丢失。")

        except Exception as e:
            print(f"处理批处理时发生未捕获的错误: {str(e)}")


def main():
    # 默认配置
    config = {
        "input": "ImageInput",
        "output": "TXTResults",
        "openai_base_url": "https://api.openai.com/v1",
        "openai_api_key": "", # 需要用户提供 OpenAI API 密钥
        "openai_model": "gpt-4-vision-preview",
        "genai_api_key": "", # 需要用户提供 GenAI API 密钥
        "genai_model": "gemini-1.5-flash-latest", # GenAI 模型示例
        "bind": 10,
        "translateTo": "简体中文",
        "clientType": "openai", # 指定使用哪个客户端 ('openai' 或 'genai')
        "proxy": "" # 添加代理默认配置
    }

    # 从 YAML 配置文件读取参数
    config_path = os.path.join(os.path.dirname(__file__), 'config.yaml') # 更改为 .yaml
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r', encoding='utf-8') as cfg_file:
                config_data = yaml.safe_load(cfg_file) # 使用 yaml.safe_load
                # 使用 get 方法更新，以便在 config.yaml 中缺少某些键时保留默认值
                if config_data: # 确保文件不是空的
                    for key in config:
                        config[key] = config_data.get(key, config[key])
            print(f"已从 {config_path} 加载配置")
        except Exception as e:
            print(f"读取配置文件时发生错误: {str(e)}，将使用默认配置")
    else:
        print(f"配置文件 {config_path} 不存在，将使用默认配置")
        # 不再需要创建默认 JSON 文件

    # 配置代理环境变量
    proxy_url = config.get("proxy", "")
    if proxy_url and proxy_url.strip():
        os.environ["HTTP_PROXY"] = proxy_url
        os.environ["HTTPS_PROXY"] = proxy_url
        print(f"已设置代理: {proxy_url}")
    else:
        # 如果配置为空，则尝试移除环境变量以使用系统设置
        os.environ.pop("HTTP_PROXY", None)
        os.environ.pop("HTTPS_PROXY", None)
        print("未配置代理，将使用系统代理设置（如果存在）。")


    # 检查所选客户端的 API 密钥是否存在
    selected_client = config.get("clientType", "openai")
    api_key_to_check = ""
    key_name = "" # 初始化 key_name
    if selected_client == "openai":
        api_key_to_check = config.get("openai_api_key")
        key_name = "openai_api_key"
    elif selected_client == "genai":
        api_key_to_check = config.get("genai_api_key")
        key_name = "genai_api_key"
    else:
        print(f"错误：无效的 clientType '{selected_client}' 在配置中。")
        return

    if not api_key_to_check:
        # 确保 key_name 已被设置
        if key_name:
             print(f"错误：所需的 API 密钥 '{key_name}' 未在配置中设置。请编辑 config.yaml 或设置默认值。")
        else:
             # 如果 clientType 无效，key_name 可能未设置
             print(f"错误：无法确定所需的 API 密钥，因为 clientType '{selected_client}' 无效。")
        return # 缺少 API 密钥则退出

    # 处理目录 (不再传递 proxy 参数)
    process_directory(
        config["input"],
        config["output"],
        config["clientType"],
        config["openai_base_url"],
        config["openai_api_key"],
        config["openai_model"],
        config["genai_api_key"],
        config["genai_model"],
        config["bind"],
        config["translateTo"]
    )

    print("所有图片处理完成！")


if __name__ == "__main__":
    main()