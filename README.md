# Simple JPG to PDF Converter

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A lightweight and lightning-fast desktop application to convert multiple JPEG/JPG images into a single PDF document. This tool uses the `img2pdf` library to ensure lossless conversion.

🇯🇵 [日本語のREADMEはこちら (Japanese Version)](README_ja.md)

## 🌟 Features
* **Lossless Conversion:** Converts images without re-encoding, maintaining 100% of the original image quality.
* **High Speed:** Processing is nearly instantaneous.
* **Batch Processing:** Select multiple images at once to merge them into one PDF.
* **Standalone:** No installation required. Just download the EXE and run.

## 💻 Requirements
* Windows 10 / 11
* (No additional software like PowerPoint or Acrobat is needed)

## 🚀 How to Download
1.  Go to the [Releases](https://github.com/kiskyk/jpg2pdf/releases) page.
2.  Download the latest version of `jpg2pdf.exe`.
3.  Double-click the file to launch the app.

## 🛠️ Usage
1.  Click **"Select Files" (ファイル選択)**.
2.  Choose one or more `.jpg` or `.jpeg` files.
3.  Click **"Run" (実行)**.
4.  The generated `output.pdf` will be saved in your **Downloads** folder.
5.  A prompt will appear asking if you want to open the folder location.

## 👨‍💻 For Developers
If you want to run from source or build the EXE yourself:

### Prerequisites
```bash
pip install img2pdf