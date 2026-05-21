from PIL import Image

def detect_question_regions(img: Image.Image, rubric_json: dict, page_num: int) -> list[dict]:
    questions = rubric_json.get("questions", [])
    width, height = img.size
    questions_per_page = max(1, len(questions) // max(1, page_num + 1))
    start_idx = page_num * questions_per_page

    regions = []
    for i in range(questions_per_page):
        q_idx = start_idx + i
        if q_idx >= len(questions):
            break
        top = int((i / questions_per_page) * height)
        bottom = int(((i + 1) / questions_per_page) * height)
        regions.append({
            "question_id": questions[q_idx]["id"],
            "bbox": (0, top, width, bottom)
        })
    return regions
