import os
import logging
from logging_config import setup_logging
from document import Document


# Retrieve PDF path from environment variable
PDF_PATH: str | None = os.getenv("PDF_PATH")

# Set up application-wide logging
log_level_str = os.getenv("LOG_LEVEL", "INFO").upper()
log_level = getattr(logging, log_level_str, logging.INFO)

setup_logging(log_level=log_level, log_file="app.log")


def main() -> None:
    """
    Entry point of the application.
    """
    if not PDF_PATH:
        logging.error(
            "PDF_PATH environment variable is not set. Please set it before running."
        )
        return

    try:
        document: Document = Document(pdf_path=PDF_PATH)
        document_summary: dict = document.get_document_summary()

        if document_summary["largest_number"] is not None:
            print(
                f"Largest Number: {document_summary['largest_number']:,.2f}; Found on Page: {document_summary['largest_number_page']}")
            print(
                f"Contextualized Largest Number: {document_summary['largest_contextualized_number']:,.2f}; Found on Page: {document_summary['largest_contextualized_number_page']}")
        else:
            print("No numbers found in the document")

    except FileNotFoundError as e:
        logging.error(e)
    except Exception as e:
        logging.critical(f"An unexpected error occurred: {e}", exc_info=True)


if __name__ == "__main__":
    main()
