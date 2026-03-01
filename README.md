# gemini-image-fetcher-skill

从指定的 Gemini 聊天 URL 抓取最新生成的图片，并自动调用去水印工具。适用于用户提供 gemini.google.com 链接并希望下载“干净”图片的场景。

## Installation

This is a skill for [Gemini CLI](https://github.com/google/gemini-cli).

To install this skill:

1. Clone this repository.
2. Run the install command:

```bash
gemini skills install ./gemini-image-fetcher-skill
```

## Documentation

# Gemini Image Fetcher Skill

## 角色
你是一个自动化专家，负责连接 Gemini Web 和本地图像处理流程。你的任务是导航到特定聊天页面，下载最新图片，并将其传递给去水印工具。

## 工作流

### 第一步：获取图片
运行 Playwright 脚本以导航到 URL 并下载最新图片。脚本使用现有的 `~/.gemini_automation_profile` 进行身份验证。

```bash
./.venv/bin/python .gemini/skills/gemini-image-fetcher-skill/scripts/fetch_latest_image.py --url "<CHAT_URL>"
```

### 第二步：提取路径
脚本会输出一行以 `RESULT_FILE_PATH:` 开头的内容。从中提取文件路径。

### 第三步：去除水印
使用提取的路径调用 `gemini-watermark-remover-skill`：

```bash
python .gemini/skills/gemini-watermark-remover-skill/remover.py "<EXTRACTED_PATH>"
```

## 注意事项
- **身份验证**：假设用户已在 `.gemini_automation_profile` 配置文件中登录 Gemini。如果未登录，浏览器将以有头模式启动，等待用户登录。
- **超时**：如果脚本未找到下载按钮，可能是由于网络缓慢或图片尚未生成。
