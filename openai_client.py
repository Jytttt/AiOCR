import base64
import re
import openai
import os

# 函数定义不变，不再需要 proxy 参数
def extract_text_from_images(image_paths, base_url, api_key, model, translate_to):
    """
    在单个请求中使用 OpenAI 的 Vision API 从多张图片中提取文本。
    代理设置通过环境变量 HTTP_PROXY 和 HTTPS_PROXY 控制。

    参数:
        image_paths (list): 图片文件路径的列表。
        base_url (str): OpenAI API 的基础 URL。
        api_key (str): OpenAI API 密钥。
        model (str): 要使用的 OpenAI 模型名称。
        translate_to (str): 要翻译的目标语言。

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
        try:
            with open(image_path, "rb") as image_file:
                base64_image = base64.b64encode(image_file.read()).decode('utf-8')

            content.append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{base64_image}" # 假设图片是JPEG，可以根据需要调整
                }
            })
        except FileNotFoundError:
            print(f"错误：找不到图片文件 {image_path}")
            # 返回空字符串表示此图片处理失败
            return [""] * len(image_paths) 
        except Exception as e:
            print(f"读取或编码图片 {image_path} 时出错: {str(e)}")
            return [""] * len(image_paths)

    try:
        # 使用OpenAI客户端代替requests
        # OpenAI 客户端会自动使用环境变量中的代理
        client = openai.OpenAI(api_key=api_key, base_url=base_url)
        
        # 发送API请求
        response = client.chat.completions.create(
            model=model,
            messages=[{
                "role": "user",
                "content": content
            }],
            max_tokens=4096 # 调整 max_tokens，1M 太大了，通常 vision 模型有上限，例如 4096
        )
        
        # 从响应中提取组合文本
        if response.choices and len(response.choices) > 0:
            combined_text = response.choices[0].message.content

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
            print("警告：API 响应中没有找到有效的 choices。")
            return [""] * len(image_paths)

    except openai.APIConnectionError as e:
        print(f"无法连接到 OpenAI API: {e}")
        return [""] * len(image_paths)
    except openai.RateLimitError as e:
        print(f"达到 OpenAI API 速率限制: {e}")
        return [""] * len(image_paths)
    except openai.APIStatusError as e:
        print(f"OpenAI API 返回状态错误: {e.status_code} - {e.response}")
        return [""] * len(image_paths)
    except Exception as e:
        print(f"API 调用期间发生意外错误: {str(e)}")
        return [""] * len(image_paths)

