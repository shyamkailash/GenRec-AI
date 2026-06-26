import requests


OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "qwen2.5:1.5b"


def generate_lab_record(
    experiment_name,
    subject,
    language="",
    output_text="",
    code_text=""
):
    prompt = f"""
You are an academic lab record generator for engineering students.

Generate a lab record in this exact format:

Aim:
Procedure:
Program or Theory:
Output:
Result:

Details:
Experiment Name: {experiment_name}
Subject: {subject}
Programming Language: {language}
Output Text: {output_text}
Code: {code_text}

Rules:
- Use simple academic English.
- Suitable for college lab record.
- Keep content clear and short.
- Follow the exact section headings.
- Do not add extra explanation outside the sections.
"""

    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False
    }

    response = requests.post(OLLAMA_URL, json=payload, timeout=120)

    if response.status_code != 200:
        raise Exception(f"Ollama error: {response.text}")

    data = response.json()
    return data.get("response", "")
