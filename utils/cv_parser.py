import pymupdf


class CVParser:
    """
    Parse a PDF CV and extract its text.
    """

    def parse(self, file_path: str) -> str:
        """
        Parse a PDF file from a file path.
        """

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
        """
        Parse a PDF directly from bytes.

        This is useful for Streamlit uploaded files,
        because we do not need to create a temporary file.
        """

        doc = pymupdf.open(
            stream=pdf_bytes,
            filetype="pdf",
        )

        text = []

        try:
            for page in doc:
                page_text = page.get_text()

                if page_text:
                    text.append(page_text)

        finally:
            doc.close()

        return "\n".join(text).strip()