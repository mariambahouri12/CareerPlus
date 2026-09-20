import pymupdf


class PDFParser:
    """Parse a PDF and extract its text."""

    def parse(self, file_path: str) -> str:
        doc = pymupdf.open(file_path)
        text = []
        try:
            for page in doc:
                page_text = page.get_text()
                if page_text:
                    text.append(page_text)
        finally:
            doc.close()
        return "\n".join(text).strip()

    def parse_bytes(self, pdf_bytes: bytes) -> str:
        doc = pymupdf.open(stream=pdf_bytes, filetype="pdf")
        text = []
        try:
            for page in doc:
                page_text = page.get_text()
                if page_text:
                    text.append(page_text)
        finally:
            doc.close()
        return "\n".join(text).strip()