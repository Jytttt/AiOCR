# AiOCR

## 简介 (Introduction)

AiOCR 是一个基于 OpenAI Vision API 的图片文字提取和翻译工具。支持批量处理、多语言翻译，并将结果保存为文本文件。

AiOCR is an image text extraction and translation tool based on the OpenAI Vision API. It supports batch processing, multilingual translation, and saves results as text files.

---

## 功能特点 (Features)

- **批量处理 / Batch Processing**：一次处理多张图片。
- **多语言翻译 / Multilingual Translation**：将提取文本翻译为指定语言。
- **自动化 / Automation**：通过配置文件加载参数。
- **支持多种图片格式 / Various Image Formats**：如 `.jpg`, `.jpeg`, `.png`, `.bmp`, `.gif`, `.webp`。

---

## 安装与运行 (Installation and Usage)

### 依赖 (Dependencies)

- Python 3.7 或更高版本 (Python 3.7 or higher)
- 必需库 (Required Libraries): `requests`, `pathlib`

安装依赖：
Install dependencies:
```bash
pip install -r requirements.txt
```

---

### 配置 (Configuration)

在项目根目录创建 `config.json` 文件，或使用默认配置。示例：
Create a `config.json` file in the project root or use the default configuration. Example:

```json
{
    "input": "ImageInput",
    "output": "TXTResults",
    "baseurl": "https://api.openai.com/v1",
    "api": "your_openai_api_key",
    "model": "gpt-4-vision-preview",
    "bind": 10,
    "translateTo": "简体中文"
}
```

- `input`: 输入图片目录 (Input image directory)
- `output`: 输出文本目录 (Output text directory)
- `baseurl`: OpenAI API 基础 URL (Base URL for OpenAI API)
- `api`: OpenAI API 密钥 (API key)
- `model`: 模型名称 (Model name)
- `bind`: 每次请求处理图片数量 (Images per request)
- `translateTo`: 翻译目标语言 (Target language for translation)

---

### 运行 (Run)

运行以下命令处理图片：
Run the following command to process images:
```bash
python main.py
```

---

## 输出 (Output)

- 提取文本保存到 `output` 目录，每张图片对应一个 `.txt` 文件。
- 未提取到文本的图片将跳过。

- Extracted text is saved in the `output` directory, one `.txt` file per image.
- Images with no extracted text are skipped.

---

## 注意事项 (Notes)

1. 输入目录需包含支持的图片格式。
2. 提供有效的 OpenAI API 密钥。
3. 若需翻译，请在配置中指定 `translateTo` 参数。
4. 视频硬字幕提取建议搭配 VideoSubFinder 提取关键帧后使用。

1. Ensure the input directory contains supported image formats.
2. Provide a valid OpenAI API key.
3. Specify the `translateTo` parameter for translation.
4. For hard subtitle extraction, use VideoSubFinder to extract keyframes first.

---

## 示例 (Example)

假设输入目录为 `ImageInput`，输出目录为 `TXTResults`，运行后将提取图片文本并保存到 `TXTResults`。

For example, if the input directory is `ImageInput` and the output directory is `TXTResults`, running the script will extract text from images and save them to `TXTResults`.

---

## 许可证 (License)

本项目基于 MIT 许可证开源。
This project is open-sourced under the MIT License.
