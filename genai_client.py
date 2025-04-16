import base64
import re
import google.generativeai as genai
from PIL import Image
import io
import os

def extract_text_from_images(image_paths, api_key, model, translate_to):
    """
    在单个请求中使用 Google GenAI 的 Vision API 从多张图片中提取文本。
    代理设置通过环境变量 HTTP_PROXY 和 HTTPS_PROXY 控制。

    参数:
        image_paths (list): 图片文件路径的列表。
        api_key (str): Google GenAI API 密钥。
        model (str): 要使用的 Google GenAI 模型名称 (例如 'gemini-pro-vision')。
        translate_to (str): 要翻译的目标语言。

    返回值:
        list: 包含对应每张图片提取的文本的列表。
    """
    try:
        genai.configure(api_key=api_key)
    except Exception as e:
        print(f"配置 GenAI 时出错: {str(e)}")
        return [""] * len(image_paths)

    content_sub = f"并翻译为{translate_to}" if translate_to else ""
    prompt = f"对于每张图片，提取文本{content_sub}，可以适当根据前后文对原文进行纠错或补充。在每个图片文本前使用唯一的标识符格式化响应，例如：第一张图片文本前添加 '###IMAGE_1###'，第二张图片文本前添加 '###IMAGE_2###'，依此类推。不要包含任何额外的文本、注释或解释。"

    # 准备包含文本提示和多张图片的内容列表
    content = [prompt]
    for image_path in image_paths:
        try:
            img = Image.open(image_path)
            # GenAI Python SDK 通常需要 PIL Image 对象
            content.append(img)
        except FileNotFoundError:
            print(f"错误：找不到图片文件 {image_path}")
            return [""] * len(image_paths)
        except Exception as e:
            print(f"加载图片 {image_path} 时出错: {str(e)}")
            return [""] * len(image_paths)

    try:
        # 选择支持视觉的模型
        genai_model = genai.GenerativeModel(model)
        
        # 发送 API 请求
        # 注意：确保模型支持多图片输入，如果不支持，可能需要为每张图片单独调用或调整策略
        response = genai_model.generate_content(content)

        # 从响应中提取组合文本
        if response.parts:
             # 查找文本部分
            combined_text = "".join(part.text for part in response.parts if hasattr(part, 'text'))
        elif hasattr(response, 'text'):
             combined_text = response.text # 有些模型可能直接在 response.text 中返回
        else:
            print("警告：GenAI 响应格式未知或不包含文本。")
            combined_text = ""


        if combined_text:
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
            print("警告：API 响应中没有提取到文本内容。")
            return [""] * len(image_paths)

    except Exception as e:
        # 捕获更具体的 GenAI 错误类型会更好，但 Exception 是一个通用回退
        print(f"GenAI API 调用期间发生错误: {str(e)}")
        return [""] * len(image_paths)
