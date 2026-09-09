"""Export Review 2 docx to PDF using Microsoft Word (Windows)."""

from pathlib import Path

try:
    import win32com.client  # type: ignore
except ImportError:
    raise SystemExit("pywin32 not installed; open the .docx in Word and Save As PDF.")

docx_path = Path(r"C:\Users\hp omen\Documents\PROJECT 1\VIT_Bhopal_Project_Report_Review2.docx")
pdf_path = Path(r"C:\Users\hp omen\Documents\PROJECT 1\VIT_Bhopal_Project_Report_Review2.pdf")

word = win32com.client.Dispatch("Word.Application")
word.Visible = False
doc = word.Documents.Open(str(docx_path))
doc.SaveAs(str(pdf_path), FileFormat=17)
doc.Close()
word.Quit()
print(f"Wrote {pdf_path}")
