# AiOCR

## 简介 (Introduction)

AiOCR 是一个基于 OpenAI Vision API 的图片文字提取和翻译工具。它可以从指定目录中的图片中提取文本，并将结果保存为文本文件。支持批量处理和多语言翻译。

AiOCR is an image text extraction and translation tool based on the OpenAI Vision API. It extracts text from images in a specified directory and saves the results as text files. It supports batch processing and multilingual translation.

---

## 功能特点 (Features)

- **批量处理**：支持一次处理多张图片。
- **多语言翻译**：可以将提取的文本翻译为指定语言。
- **自动化**：通过配置文件自动加载参数。
- **支持多种图片格式**：如 `.jpg`, `.jpeg`, `.png`, `.bmp`, `.gif`, `.webp`。

- **Batch Processing**: Supports processing multiple images at once.
- **Multilingual Translation**: Translates extracted text into a specified language.
- **Automation**: Automatically loads parameters via a configuration file.
- **Supports Various Image Formats**: Such as `.jpg`, `.jpeg`, `.png`, `.bmp`, `.gif`, `.webp`.

---

## 安装与运行 (Installation and Usage)

### 依赖 (Dependencies)

- Python 3.7 或更高版本 (Python 3.7 or higher)
- 必需的 Python 库 (Required Python Libraries):
  - `requests`
  - `pathlib`

使用以下命令安装依赖：
Install dependencies using the following command:
```bash
pip install -r requirements.txt
```

---

### 配置 (Configuration)

在项目根目录下创建一个 `config.json` 文件，或使用默认配置。以下是配置文件的示例：
Create a `config.json` file in the project root directory or use the default configuration. Below is an example configuration file:

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

- `input`: 输入图片的目录路径 (Directory path for input images)
- `output`: 输出文本的目录路径 (Directory path for output text files)
- `baseurl`: OpenAI API 的基础 URL (Base URL for OpenAI API)
- `api`: OpenAI API 密钥 (OpenAI API key)
- `model`: 使用的模型名称 (Model name to use)
- `bind`: 每次请求处理的图片数量 (Number of images processed per request)
- `translateTo`: 翻译目标语言 (Target language for translation)

---

### 运行 (Run)

运行以下命令开始处理图片：
Run the following command to start processing images:
```bash
python main.py
```

---

## 输出 (Output)

- 提取的文本将保存到 `output` 目录中，每张图片对应一个 `.txt` 文件。
- 如果未提取到文本，将跳过保存。

- Extracted text will be saved in the `output` directory, with each image corresponding to a `.txt` file.
- If no text is extracted, the file will be skipped.

---

## 注意事项 (Notes)

1. 确保输入目录中包含支持的图片格式。
2. 确保提供有效的 OpenAI API 密钥。
3. 如果需要翻译，请在配置中指定 `translateTo` 参数。

1. Ensure the input directory contains supported image formats.
2. Ensure a valid OpenAI API key is provided.
3. If translation is required, specify the `translateTo` parameter in the configuration.

---

## 示例 (Example)

假设输入目录为 `ImageInput`，输出目录为 `TXTResults`，运行后将提取 `ImageInput` 中的图片文本并保存到 `TXTResults` 中。

For example, if the input directory is `ImageInput` and the output directory is `TXTResults`, running the script will extract text from images in `ImageInput` and save them to `TXTResults`.

---

## 许可证 (License)

本项目基于 MIT 许可证开源。
This project is open-sourced under the MIT License.
