#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import json
from pathlib import Path

def install_paddleocr():
    """
    检查并安装必要的PaddleOCR库
    """
    try:
        # 尝试导入PaddleOCR，如果已安装则直接使用
        from paddleocr import PaddleOCR
    except ImportError:
        print("正在安装PaddleOCR...")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "paddleocr"])
        print("PaddleOCR安装完成")

# 确保PaddleOCR已安装
install_paddleocr()

# 在安装后导入
from paddleocr import PaddleOCR, draw_ocr

def clean_empty_images(input_dir, use_gpu=False, lang="japan"):
    """
    使用PaddleOCR识别图片中的文字，删除没有文字的图片。

    参数:
        input_dir (str): 包含图片的输入目录
        use_gpu (bool): 是否使用GPU进行推理
        lang (str): 识别语言，默认为"jp"（日语）
    
    返回:
        tuple: (处理的图片数量, 删除的图片数量)
    """
    # 确保输入目录存在
    input_path = Path(input_dir)
    if not input_path.exists() or not input_path.is_dir():
        print(f"错误：输入目录 '{input_dir}' 不存在或不是一个目录")
        return 0, 0

    # 支持的图片格式
    image_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.gif', '.webp']

    # 获取输入目录中的所有图片文件
    image_files = [f for f in os.listdir(input_dir)
                  if os.path.isfile(os.path.join(input_dir, f)) and
                  os.path.splitext(f)[1].lower() in image_extensions]
    
    total_images = len(image_files)
    print(f"找到 {total_images} 张图片需要处理")

    if total_images == 0:
        return 0, 0

    # 初始化PaddleOCR
    try:
        ocr = PaddleOCR(use_angle_cls=True, use_gpu=use_gpu, lang=lang)
        print(f"OCR引擎初始化完成 [语言:{lang}] [{'GPU' if use_gpu else 'CPU'}]")
    except Exception as e:
        print(f"OCR引擎初始化失败: {str(e)}")
        return 0, 0

    # 处理每张图片
    deleted_count = 0
    for i, image_file in enumerate(image_files):
        image_path = os.path.join(input_dir, image_file)
        print(f"[{i+1}/{total_images}] {image_file}", end="")
        
        try:
            # 进行OCR识别
            result = ocr.ocr(image_path, cls=True)
            
            # 检查是否包含文本
            has_text = False
            if result:
                for line in result:
                    if line and isinstance(line, list) and len(line) > 0:
                        has_text = True
                        # 输出识别到的文字
                        for text_line in line:
                            if isinstance(text_line, list) and len(text_line) >= 2:
                                if isinstance(text_line[1], tuple) and len(text_line[1]) >= 1:
                                    # 新版本格式 [[points], (text, confidence)]
                                    text, confidence = text_line[1]
                                    print(f" → 识别文字: \"{text}\" ({confidence:.2f})")
                                elif isinstance(text_line, dict) and "text" in text_line:
                                    # 某些版本可能使用字典格式
                                    print(f" → 识别文字: \"{text_line['text']}\"")
                        break
            
            if not has_text:
                # 删除没有文字的图片
                os.remove(image_path)
                deleted_count += 1
                print(" [已删除]")
            else:
                print(" [已保留]")
                
        except Exception as e:
            print(f" [错误] {str(e)}")
    
    print(f"处理完成！共处理 {total_images} 张图片，删除了 {deleted_count} 张没有文字的图片")
    return total_images, deleted_count

def main():
    # 默认配置
    config = {
        "input": "ImageInput",
        "use_gpu": False,
        "lang": "japan"  # 默认改为日语识别
    }

    # 从配置文件读取参数
    config_path = os.path.join(os.path.dirname(__file__), 'config.json')
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r', encoding='utf-8') as cfg_file:
                config_data = json.load(cfg_file)
                # 只更新已存在的配置项
                for key in ["input", "use_gpu", "lang"]:
                    if key in config_data:
                        config[key] = config_data[key]
            print(f"已加载配置")
        except Exception as e:
            print(f"读取配置失败: {str(e)}")
    else:
        # 创建默认配置文件
        try:
            with open(config_path, 'w', encoding='utf-8') as cfg_file:
                json.dump(config, cfg_file, indent=4, ensure_ascii=False)
            print(f"已创建默认配置")
        except Exception as e:
            print(f"创建配置失败: {str(e)}")

    # 清理没有文字的图片
    clean_empty_images(
        config["input"],
        config["use_gpu"],
        config["lang"]
    )

if __name__ == "__main__":
    main()
