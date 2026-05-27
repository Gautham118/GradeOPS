from PIL import Image

def detect_question_regions(
    page_image: Image.Image,
    rubric_json: dict,
    page_index: int
) -> list[dict]:
    """
    Heuristic region detector:
    - Assumes one question per page (simple layout)
    - For multi-question pages, splits page into N equal horizontal strips
    
    Returns list of {"question_id": str, "bbox": (x1,y1,x2,y2), "page_index": int}
    """
    questions = rubric_json.get("questions", [])
    W, H = page_image.size

    # Questions mapped to pages by index
    # Page 0 → questions 0,1  |  Page 1 → questions 2,3  etc.
    # Adjust this mapping based on your actual exam layout
    questions_on_page = [q for i, q in enumerate(questions) if i == page_index]

    if not questions_on_page:
        return []

    regions = []
    strip_height = H // len(questions_on_page)

    for i, question in enumerate(questions_on_page):
        y1 = i * strip_height
        y2 = (i + 1) * strip_height if i < len(questions_on_page) - 1 else H
        regions.append({
            "question_id": question["id"],
            "bbox": (0, y1, W, y2),
            "page_index": page_index
        })

    return regions