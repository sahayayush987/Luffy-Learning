from pypdf import PdfReader

def extract_text_from_file(uploaded_file):
    if uploaded_file.type == "text/plain":
        return uploaded_file.read().decode("utf-8")

    pdf = PdfReader(uploaded_file)
    text = ""
    for i, page in enumerate(pdf.pages):
        # limit pages for speed
        if i > 10:  
            break
        text += page.extract_text() or ""
    return text

