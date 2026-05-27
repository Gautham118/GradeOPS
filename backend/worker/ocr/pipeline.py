import io
from PIL import Image
from core.config import supabase_admin
from worker.ocr.pdf_utils import pdf_to_images
from worker.ocr.crop_utils import detect_question_regions
from worker.ocr.vision import transcribe_with_groq


def pil_to_bytes(img: Image.Image) -> bytes:
    buffer = io.BytesIO()
    img.save(buffer, format="JPEG", quality=95)
    return buffer.getvalue()


def run_ocr(submission_id: str) -> list[dict]:
    """
    Full OCR pipeline for one submission.
    Returns list of {"grade_id": str} for each question found.
    """
    # 1. Fetch submission + exam records
    sub = supabase_admin.table("submissions")\
        .select("*, exams(rubric_json)")\
        .eq("id", submission_id)\
        .single()\
        .execute().data

    rubric_json = sub["exams"]["rubric_json"]
    exam_id = sub["exam_id"]

    # 2. Download PDF from Supabase Storage
    pdf_bytes = supabase_admin.storage\
        .from_("exam-pdfs")\
        .download(sub["pdf_path"])

    # 3. Convert PDF pages to images
    page_images = pdf_to_images(pdf_bytes)
    print(f"[OCR] {len(page_images)} pages found for submission {submission_id}")

    grade_ids = []

    # 4. Process each page
    for page_index, page_image in enumerate(page_images):
        regions = detect_question_regions(page_image, rubric_json, page_index)

        for region in regions:
            question_id = region["question_id"]
            bbox = region["bbox"]

            # 5. Crop the answer region
            crop_image = page_image.crop(bbox)

            # 6. Transcribe with vision model
            print(f"[OCR] Transcribing {question_id} on page {page_index}...")
            transcription = transcribe_with_groq(crop_image)
            print(f"[OCR] Transcription: {transcription[:80]}...")

            # 7. Upload crop image to Supabase Storage
            crop_path = f"{submission_id}/{question_id}.jpg"
            crop_bytes = pil_to_bytes(crop_image)

            try:
                supabase_admin.storage\
                    .from_("answer-crops")\
                    .upload(crop_path, crop_bytes, {"content-type": "image/jpeg"})
            except Exception:
                # File might already exist on retry — update instead
                supabase_admin.storage\
                    .from_("answer-crops")\
                    .update(crop_path, crop_bytes, {"content-type": "image/jpeg"})

            # 8. Find max_marks for this question from rubric
            question_rubric = next(
                (q for q in rubric_json["questions"] if q["id"] == question_id),
                None
            )
            max_marks = question_rubric["max_marks"] if question_rubric else 10

            # 9. Create grade record in DB
            grade = supabase_admin.table("grades").insert({
                "submission_id": submission_id,
                "exam_id": exam_id,
                "question_id": question_id,
                "transcription": transcription,
                "crop_url": crop_path,
                "max_marks": max_marks,
                "status": "ocr_complete"
            }).execute().data[0]

            grade_ids.append({"grade_id": grade["id"]})

    return grade_ids