from pathlib import Path
from google import genai
from google.genai import types


def ocr_pdf(
    pdf_path: Path,
    out_path: Path,
    model_config: dict
) -> str:
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")
    api_key = model_config["api_key"]
    client = genai.Client(api_key=api_key)

    uploaded = client.files.upload(
        file=pdf_path,
        config=types.UploadFileConfig(mime_type="application/pdf"),
    )

    prompt = model_config.get("prompt")
    model = model_config.get("model", "gemini-2.5-flash")

    if not prompt:
        raise ValueError("model_config must include a non-empty 'prompt'.")

    response = client.models.generate_content(
        model=model,
        contents=[uploaded, prompt],
        config=types.GenerateContentConfig(
            temperature=0,
        ),
    )

    text = response.text or ""
    out_path.write_text(text, encoding="utf-8")
    return text

