from pathlib import Path

from pypdf import PdfReader


root = Path(r"C:\Users\PC - Henkes\python\OC\p11\Portfolio_Web_Static")
pdfs = {
    "fr": root / "assets" / "cv" / "CV_Kevin_Henkes_public.pdf",
    "en": root / "assets" / "cv" / "CV_Kevin_Henkes_public_en.pdf",
}

for language, path in pdfs.items():
    reader = PdfReader(path)
    text = "\n".join(page.extract_text() or "" for page in reader.pages)
    normalized = text.casefold()
    required = ["Python", "2016-2017", "2016-2018"]
    if language == "fr":
        required.extend(["Développement", "Formations"])
    else:
        required.extend(["Development", "Education", "Five selected data projects"])
    missing = [value for value in required if value.casefold() not in normalized]
    private_hits = [value for value in ["03 88 49 31 68", "Rue Principale"] if value in text]
    print({"language": language, "pages": len(reader.pages), "missing": missing, "private_hits": private_hits, "chars": len(text)})
    if len(reader.pages) != 1 or missing or private_hits:
        raise SystemExit(1)

html = (root / "cv.html").read_text(encoding="utf-8")
js = (root / "assets" / "js" / "app.js").read_text(encoding="utf-8")
checks = {
    "english_pdf_exists": pdfs["en"].exists(),
    "html_has_both_pdf_sources": "data-src-fr=" in html and "data-src-en=" in html,
    "downloads_follow_language": html.count("data-cv-fr=") >= 2 and html.count("data-cv-en=") >= 2,
    "javascript_switches_pdf": "data-cv-pdf" in js and "data-src-${state.language}" in js,
    "html_development_has_python": "Development:</span></strong> Python" in html,
}
print(checks)
if not all(checks.values()):
    raise SystemExit(1)
