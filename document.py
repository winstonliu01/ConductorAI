import logging
import os
from pdfminer.high_level import extract_text
from pdfminer.pdfpage import PDFPage
from logging_config import setup_logging
from page import Page

setup_logging(log_level=logging.INFO, log_file="app.log")


class Document:
    """
    Represents an entire PDF document, managing its pages and identifying
    the largest numerical value across all pages.
    """

    def __init__(self, pdf_path: str, document_name: str | None = None):
        """
        Initializes a Document object.

        Args:
            pdf_path (str): The file path to the PDF document.
            document_name (str | None): An optional name for the document. If None,
                                        it's derived from the PDF file name.
        """
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF file not found at: {pdf_path}")

        self.pdf_path = pdf_path
        self.document_name = (
            document_name if document_name else os.path.basename(pdf_path)
        )
        self.pages: list[Page] = []
        self.max_number: float | None = None
        self.max_number_page_number: int | None = None
        self.max_contextualized_number: float | None = None
        self.max_contextualized_number_page_number: int | None = None
        self._full_document_text: str = ""

        self._extract_full_document_text()
        self._process_pages()
        self._find_global_maximum()

    def _extract_full_document_text(self) -> None:
        """
        Extracts the full text content from the PDF document for analysis.
        """
        logging.info(
            f"Extracting full document text from '{self.document_name}'")

        try:
            self._full_document_text = extract_text(self.pdf_path)
            logging.info(
                f"Successfully extracted {len(self._full_document_text)} characters from document"
            )
        except Exception as e:
            logging.error(f"Error extracting full document text: {e}")
            self._full_document_text = ""

    def _process_pages(self) -> None:
        """
        Processes the PDF document page by page, extracting text and numbers.
        """
        logging.info(f"Processing pages for document '{self.document_name}'")

        try:
            with open(self.pdf_path, "rb") as file:
                pages = list(PDFPage.get_pages(file))
                total_pages = len(pages)
                logging.info(f"Found {total_pages} pages to process")

                for page_index, _ in enumerate(pages):
                    page_number = page_index + 1
                    self._process_single_page(page_number, page_index)

        except Exception as e:
            logging.error(f"Error during page processing: {e}")

    def _process_single_page(self, page_number: int, page_index: int) -> None:
        """
        Processes a single page of the PDF document.

        Args:
            page_number (int): The human-readable page number (1-based)
            page_index (int): The zero-based page index for extraction
        """
        try:
            logging.info(f"Processing page {page_number}")

            page_text = extract_text(self.pdf_path, page_numbers=[page_index])
            page = Page(page_number, page_text)
            self.pages.append(page)

            if page.parsed_numbers:
                logging.debug(
                    f"Page {page_number} - Found {len(page.parsed_numbers)} numbers, max: {page.max_number:,.2f}, max contextualized: {page.max_contextualized_number:,.2f}"
                )
            else:
                logging.debug(f"Page {page_number} - No numbers found")

        except Exception as e:
            logging.error(f"Error processing page {page_number}: {e}")

    def _find_global_maximum(self) -> None:
        """
        Finds the largest number and largest contextualized number across all processed pages.
        """
        logging.info("Finding global maximum numbers across all pages")

        for page in self.pages:

            if page.max_number is not None:
                if (self.max_number is None) or (page.max_number > self.max_number):
                    self.max_number = page.max_number
                    self.max_number_page_number = page.page_number
                    logging.info(
                        f"New global maximum found: {self.max_number:,.2f} on page {self.max_number_page_number}"
                    )

            if page.max_contextualized_number is not None:
                if (self.max_contextualized_number is None) or (
                    page.max_contextualized_number > self.max_contextualized_number
                ):
                    self.max_contextualized_number = page.max_contextualized_number
                    self.max_contextualized_number_page_number = page.page_number
                    logging.info(
                        f"New global contextualized maximum found: {self.max_contextualized_number:,.2f} on page {self.max_contextualized_number_page_number}"
                    )

        if self.max_number is None:
            logging.warning(
                f"No numbers found in document '{self.document_name}'")
        elif self.max_contextualized_number is None:
            logging.warning(
                f"No contextualized numbers found in document '{self.document_name}'"
            )

    def get_document_summary(self) -> dict:
        """
        Returns a summary of the document processing results.

        Returns:
            dict: A dictionary containing document processing statistics
        """
        total_numbers = sum(len(page.parsed_numbers) for page in self.pages)
        pages_with_numbers = len(
            [page for page in self.pages if page.parsed_numbers])

        return {
            "document_name": self.document_name,
            "total_pages": len(self.pages),
            "pages_with_numbers": pages_with_numbers,
            "total_numbers_found": total_numbers,
            "largest_number": self.max_number,
            "largest_number_page": self.max_number_page_number,
            "largest_contextualized_number": self.max_contextualized_number,
            "largest_contextualized_number_page": self.max_contextualized_number_page_number,
            "document_text_length": len(self._full_document_text),
        }
