import base64
import io
from PIL import Image
from groq import Groq
from core.config import settings

groq_client = Groq(api_key=settings.GROQ_API_KEY)

def image_to_base64(img: Image.Image) -> str:
    buffer = io.BytesIO()
    img.save(buffer, format="JPEG", quality=95)
    return base64.b64encode(buffer.getvalue()).decode("utf-8")


def transcribe_with_groq(crop_image: Image.Image) -> str:
    """
    Uses Groq vision API (llama-4-scout) for OCR.
    Fast, free, no GPU needed — perfect for dev.
    """
    img_b64 = image_to_base64(crop_image)

    response = groq_client.chat.completions.create(
        model="meta-llama/llama-4-scout-17b-16e-instruct",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{img_b64}"
                        }
                    },
                    {
                        "type": "text",
                        "text": (
                            "This is a cropped image of a handwritten student exam answer. "
                            "Transcribe ALL the handwritten text exactly as written. "
                            "Preserve mathematical notation, symbols, and diagrams described in words. "
                            "Output only the transcribed text, nothing else."
                        )
                    }
                ]
            }
        ],
        max_tokens=1024
    )

    return response.choices[0].message.content.strip()


# ── Production swap: uncomment to use Qwen2-VL on Colab/Kaggle ──────────────
# from transformers import Qwen2VLForConditionalGeneration, AutoProcessor
# import torch
#
# model = Qwen2VLForConditionalGeneration.from_pretrained(
#     "Qwen/Qwen2-VL-7B-Instruct",
#     torch_dtype=torch.float16,
#     device_map="auto"
# )
# processor = AutoProcessor.from_pretrained("Qwen/Qwen2-VL-7B-Instruct")
#
# def transcribe_with_qwen(crop_image: Image.Image) -> str:
#     messages = [{"role": "user", "content": [
#         {"type": "image", "image": crop_image},
#         {"type": "text", "text": "Transcribe all handwritten text exactly as written."}
#     ]}]
#     text = processor.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
#     inputs = processor(text=[text], images=[crop_image], return_tensors="pt").to("cuda")
#     output = model.generate(**inputs, max_new_tokens=512)
#     return processor.batch_decode(output, skip_special_tokens=True)[0].strip()