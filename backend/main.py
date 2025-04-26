from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from openai import OpenAI
import os, subprocess, fitz
from fpdf import FPDF

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

app.mount("/ocr_output", StaticFiles(directory="ocr_output"), name="ocr_output")

UPLOAD_DIR = "uploads"
OCR_DIR = "ocr_output"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OCR_DIR, exist_ok=True)

class AssignmentRequest(BaseModel):
    text: str
    api_key: str

def save_pdf(text: str, filename: str):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    for line in text.split("\n"):
        pdf.multi_cell(0, 10, line.encode("latin-1", "replace").decode("latin-1"))
    path = f"{OCR_DIR}/{filename}"
    pdf.output(path)
    return path

@app.post("/upload_pdf")
def upload_pdf(file: UploadFile = File(...)):
    path = f"{UPLOAD_DIR}/{file.filename}"
    with open(path, "wb") as f:
        f.write(file.file.read())
    return {"filename": file.filename}

@app.post("/ocr_pdf")
def ocr_pdf(filename: str = Form(...)):
    input_path = f"{UPLOAD_DIR}/{filename}"
    output_path = f"{OCR_DIR}/ocr_{filename}"
    subprocess.run([
        "ocrmypdf", "--rotate-pages", "--deskew", "--force-ocr", "-l", "eng",
        input_path, output_path
    ], check=True)
    return {"ocr_pdf": f"ocr_{filename}"}

@app.get("/get_pdf_text")
def get_pdf_text(filename: str):
    path = f"{OCR_DIR}/{filename}" if os.path.exists(f"{OCR_DIR}/{filename}") else f"{UPLOAD_DIR}/{filename}"
    if not os.path.exists(path):
        return {"error": "File not found."}
    doc = fitz.open(path)
    return {"text": "\n".join(page.get_text() for page in doc)}

@app.post("/generate_assignment")
def generate_assignment(req: AssignmentRequest):
    client = OpenAI(api_key=req.api_key)
    prompt = f"You are a teacher. Please generate 5 questions and answers from the following lesson content:\n{req.text}"
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ]
    )
    content = response.choices[0].message.content
    save_pdf(content, "assignment_with_answers.pdf")
    return {"result": content, "pdf": "assignment_with_answers.pdf"}

@app.post("/generate_fake_answer_pdf")
def generate_fake_answer_pdf(req: AssignmentRequest):
    client = OpenAI(api_key=req.api_key)
    prompt = f"Given the following questions and answers, simulate a student taking the test and answering with some mistakes:\n{req.text}"
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a student taking a test and making small mistakes."},
            {"role": "user", "content": prompt}
        ]
    )
    content = response.choices[0].message.content
    save_pdf(content, "student_fake_answers.pdf")
    return {"pdf": "student_fake_answers.pdf"}

@app.post("/grade_from_pdf")
def grade_from_pdf(pdf_filename: str = Form(...), api_key: str = Form(...), reference_text: str = Form(...)):
    path = f"{OCR_DIR}/{pdf_filename}"
    if not os.path.exists(path):
        return {"error": "File not found."}
    doc = fitz.open(path)
    student_text = "\n".join(page.get_text() for page in doc)
    client = OpenAI(api_key=api_key)
    prompt = (
        f"Please grade the following student's answers based on the reference. Each question is worth 10 points, include suggestions:\n"
        f"Reference:\n{reference_text}\n\nStudent Answers:\n{student_text}"
    )
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a responsible and detailed teacher."},
            {"role": "user", "content": prompt}
        ]
    )
    content = response.choices[0].message.content
    save_pdf(content, "grading_result.pdf")
    return {"result": content, "pdf": "grading_result.pdf"}
