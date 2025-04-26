
# PDF Homework Automation System

## Overview

This project is a simple full-stack application that automates the process of generating assignments, simulating student answers, and grading the answers based on lesson PDFs. It combines FastAPI (backend) and React (frontend).

OCR is performed on uploaded PDFs using [OCRmyPDF](https://github.com/ocrmypdf/OCRmyPDF).

## Features

- Upload a lesson PDF and extract text via OCR.
- Automatically generate five questions and answers based on the extracted text.
- Simulate a student taking the assignment with some intentional mistakes.
- Grade the simulated answers against the original reference answers.
- Download the generated PDFs for assignment, fake answers, and grading results.

## Backend (FastAPI)

- Upload PDF (`/upload_pdf`)
- Perform OCR on uploaded PDF (`/ocr_pdf`)
- Extract text from OCR'd PDF (`/get_pdf_text`)
- Generate assignment based on extracted text (`/generate_assignment`)
- Generate fake student answers PDF (`/generate_fake_answer_pdf`)
- Grade the student answers (`/grade_from_pdf`)

The backend also serves generated PDFs through `/ocr_output` endpoint.

## Frontend (React)

- Upload a PDF and extract text.
- Generate assignment questions and answers.
- Generate fake answers PDF.
- Upload fake answer PDF and get grading results.
- Download assignment, fake answer, and grading PDFs.

## Installation

### Backend

1. Install dependencies:
    ```bash
    pip install fastapi uvicorn python-multipart openai pypdf2 pymupdf fpdf
    ```
2. Install OCRmyPDF (you must have Tesseract installed as well):
    ```bash
    choco install ocrmypdf  # for Windows (requires Chocolatey)
    brew install ocrmypdf   # for macOS
    apt install ocrmypdf    # for Ubuntu/Debian
    ```
3. Run the backend server:
    ```bash
    uvicorn main:app --reload
    ```

### Frontend

1. Install Node.js and npm.
2. Navigate to the frontend folder and install dependencies:
    ```bash
    npm install
    ```
3. Start the React development server:
    ```bash
    npm start
    ```

## Important Notes

- You must provide your own OpenAI API key to generate assignments and grading.
- OCR is **forced** even if the PDF already contains a text layer.
- Outputs are saved as PDFs under the `ocr_output/` directory.

