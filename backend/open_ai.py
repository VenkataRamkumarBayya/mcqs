from dotenv import load_dotenv
load_dotenv()

import os
import pdfplumber
from pathlib import Path
from openai import OpenAI

# ✅ Initialize OpenAI client using key from .env
client = OpenAI()

# ✅ Extract raw text from the PDF
def extract_raw_text(pdf_path):
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text

# ✅ Keep only meaningful lines
def split_into_chunks(text, min_length=40):
    lines = [line.strip() for line in text.split("\n") if len(line.strip()) >= min_length]
    return lines

# ✅ Use GPT-4 to clean and format the content
def gpt_clean_facts(raw_text):
    prompt = f"""Extract clean, fact-based one-line science statements from the text below.
Each fact should be a single sentence starting with a noun or concept (e.g., "Photosynthesis is...").
Ignore headings or non-scientific content.

Text:
{raw_text}

Return each fact on a new line.
"""

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )
    return response.choices[0].message.content

# ✅ Save result in same folder as the input PDF
def save_to_file(cleaned_text, output_path):
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(cleaned_text.strip())

# ✅ Main function
def process_pdf_to_clean_txt(pdf_path, max_lines=None):
    print(f"📥 Reading PDF from: {pdf_path}")
    raw_text = extract_raw_text(pdf_path)

    print("✂️ Filtering lines...")
    chunks = split_into_chunks(raw_text)
    input_text = "\n".join(chunks[:max_lines]) if max_lines else "\n".join(chunks)

    print("🤖 Sending to GPT...")
    cleaned = gpt_clean_facts(input_text)

    output_path = Path(pdf_path).with_suffix(".cleaned.txt")  # ✅ update here
    print(f"💾 Saving cleaned facts to: {output_path.name}")
    save_to_file(cleaned, output_path)
    print("✅ Done!")


# ✅ Run script
if __name__ == "__main__":
    folder_path = r"C:\Users\ramsb\OneDrive\Desktop\Random\qa-app\backend\data"
    for file in os.listdir(folder_path):
        if file.lower().endswith(".pdf"):
            pdf_path = os.path.join(folder_path, file)
            process_pdf_to_clean_txt(pdf_path, max_lines=150)
