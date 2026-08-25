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
    private_hits = [value for value in ["03 88 49 31 68", "Rue Principale", "henkeskevin0@gmail.com"] if value in text]
    links = []
    for page in reader.pages:
        for annotation_ref in page.get("/Annots") or []:
            annotation = annotation_ref.get_object()
            action = annotation.get("/A") or {}
            if action.get("/URI"):
                links.append(action.get("/URI"))
    linkedin_ok = "https://www.linkedin.com/in/kevinhenkes/" in links
    print({"language": language, "pages": len(reader.pages), "missing": missing, "private_hits": private_hits, "linkedin_ok": linkedin_ok, "chars": len(text)})
    if len(reader.pages) != 1 or missing or private_hits or not linkedin_ok:
        raise SystemExit(1)

html = (root / "cv.html").read_text(encoding="utf-8")
js = (root / "assets" / "js" / "app.js").read_text(encoding="utf-8")
site_text = "\n".join(path.read_text(encoding="utf-8") for path in root.glob("*.html"))
checks = {
    "english_pdf_exists": pdfs["en"].exists(),
    "html_has_both_pdf_sources": "data-src-fr=" in html and "data-src-en=" in html,
    "downloads_follow_language": html.count("data-cv-fr=") >= 2 and html.count("data-cv-en=") >= 2,
    "javascript_switches_pdf": "data-cv-pdf" in js and "data-src-${state.language}" in js,
    "html_development_has_python": "Development:</span></strong> Python" in html,
    "email_removed_from_site": "henkeskevin0@gmail.com" not in site_text and "mailto:" not in site_text,
    "linkedin_added_to_all_pages": site_text.count("https://www.linkedin.com/in/kevinhenkes/") >= 6,
    "no_provisional_linkedin_url": "fr.linkedin.com/in/kevinhenkes" not in site_text,
}
print(checks)
if not all(checks.values()):
    raise SystemExit(1)
