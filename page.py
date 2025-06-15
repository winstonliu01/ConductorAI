import logging
import re
from typing import List, Optional
from logging_config import setup_logging

setup_logging(log_level=logging.INFO, log_file="app.log")


class Page:
    """
    Represents a single page of a PDF document
    """

    def __init__(self, page_number: int, text: str):
        """
        Initializes a Page object.

        Args:
            page_number (int): The sequential number of the page in the document.
            text (str): The raw text content extracted from this page.
        """
        self.page_number = page_number
        self.text = text

        self.raw_numbers: List[str] = []
        self.parsed_numbers: List[float] = []
        self.contextualized_numbers: List[float] = (
            []
        )
        self.max_number: Optional[float] = None
        self.max_contextualized_number: Optional[float] = None

        logging.debug(
            f"Initializing Page {self.page_number} with {len(self.text)} characters"
        )
        self._process_page_content()

    def _process_page_content(self) -> None:
        """
        Processes the page content to extract and parse numbers.
        """
        logging.debug(f"Processing content for page {self.page_number}")

        processed_text = self._preprocess_text()
        self.raw_numbers = self._find_raw_numbers(processed_text)
        self.parsed_numbers = self._parse_numbers()
        self.contextualized_numbers = self._apply_quantifiers()

        self.max_number = self._calculate_max_number(False)
        self.max_contextualized_number = self._calculate_max_number(True)

        self._log_processing_results()

    def _preprocess_text(self) -> str:
        """
        Preprocesses the text to insert spaces between numbers and letters.

        Returns:
            str: Preprocessed text with spaces inserted between numbers and letters
        """
        text = self.text

        # Insert space between digit and letter: 1OPERATINGBUDGET -> 1 OPERATINGBUDGET
        text = re.sub(r"(\d)([A-Za-z])", r"\1 \2", text)

        # Insert space between letter and digit: BUDGET1ITEM -> BUDGET 1 ITEM
        text = re.sub(r"([A-Za-z])(\d)", r"\1 \2", text)

        return text

    def _find_raw_numbers(self, text: str) -> List[str]:
        """
        Finds all potential number strings in the text using regex patterns.

        Args:
            text (str): The preprocessed text to search for numbers

        Returns:
            List[str]: Raw number strings found in the text
        """
        patterns = [
            # Currency formats with commas: $1,234.56, $1,234
            r"\$\s*\d{1,3}(?:,\d{3})*(?:\.\d+)?\b",
            # Parenthetical numbers with commas: (1,234.56), (1,234)
            r"\(\s*\d{1,3}(?:,\d{3})*(?:\.\d+)?\s*\)",
            # Standard numbers with commas: 1,234.56, 1,234
            r"\b\d{1,3}(?:,\d{3})+(?:\.\d+)?\b",
            # Percentages: 25%, 12.5%
            r"\b\d+(?:\.\d+)?%",
            # Standalone decimal numbers (not part of comma-separated): 123.45, 0.25, .75
            r"(?<!\d,)\b\d*\.\d+\b",
            # Whole numbers (not part of comma-separated numbers and not already matched as decimal parts)
            r"(?<!\d\.)\b\d+\b(?!\.\d)",
        ]

        raw_numbers = []
        matched_positions = set()

        for _, pattern in enumerate(patterns):
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                start, end = match.span()

                if not any(pos in range(start, end) for pos in matched_positions):
                    raw_number = match.group().strip()
                    if (
                        raw_number and raw_number not in raw_numbers
                    ):
                        raw_numbers.append(raw_number)
                        matched_positions.update(range(start, end))

        return raw_numbers

    def _parse_numbers(self) -> List[float]:
        """
        Parses raw number strings into float values.

        Returns:
            List[float]: Parsed numbers
        """
        parsed_numbers = []

        for raw_number in self.raw_numbers:
            try:
                parsed_value = self._parse_single_number(raw_number)
                if parsed_value is not None:
                    parsed_numbers.append(parsed_value)
                    logging.debug(
                        f"Page {self.page_number}: '{raw_number}' -> {parsed_value}"
                    )

            except Exception as e:
                logging.debug(
                    f"Page {self.page_number}: Error parsing '{raw_number}': {e}"
                )
                continue

        return parsed_numbers

    def _parse_single_number(self, raw_number: str) -> Optional[float]:
        """
        Parses a single raw number string into a float value.

        Args:
            raw_number (str): The raw number string to parse

        Returns:
            Optional[float]: The parsed number or None if parsing fails
        """
        # Clean the number string
        cleaned = raw_number.strip()

        # Handle percentages
        if cleaned.endswith("%"):
            cleaned = cleaned[:-1]
            try:
                return float(cleaned) / 100
            except ValueError:
                return None

        # Handle currency symbols
        if cleaned.startswith("$"):
            cleaned = cleaned[1:].strip()

        # Handle parenthetical numbers
        if cleaned.startswith("(") and cleaned.endswith(")"):
            cleaned = cleaned[1:-1].strip()

        # Remove commas
        cleaned = cleaned.replace(",", "")

        # Handle empty strings or just symbols
        if not cleaned or cleaned in ["$", "(", ")", "."]:
            return None

        try:
            return float(cleaned)
        except ValueError:
            logging.debug(
                f"Page {self.page_number}: Could not parse '{cleaned}' as float"
            )
            return None

    def _calculate_max_number(self, is_contexual) -> Optional[float]:
        """
        Calculates the maximum number among the parsed numbers for this page.

        Args:
            is_contexual (bool): Boolean if we are looking for contexual number

        Returns:
            Optional[float]: The largest number on the page, or None if no numbers were found.
        """

        if (is_contexual):
            number = self.contextualized_numbers
        else:
            number = self.parsed_numbers

        if not number:
            return None

        max_val = max(number)

        return max_val

    def _log_processing_results(self) -> None:
        """
        Logs the processing results for this page.
        """
        if self.parsed_numbers:
            logging.debug(
                f"Page {self.page_number}: Successfully processed {len(self.parsed_numbers)} numbers"
            )
            logging.debug(
                f"Page {self.page_number}: Numbers found: {[f'{n:,.2f}' for n in self.parsed_numbers[:10]]}"
            )
        else:
            logging.debug(f"Page {self.page_number}: No valid numbers found")

        logging.debug(
            f"Page {self.page_number}: Text: '{self.text}'")

    def _apply_quantifiers(self) -> List[float]:
        """
        Applies quantifiers (million, thousand, billion) to numbers based on context.
        Only applies when quantifier immediately follows the number.

        Returns:
            List[float]: Numbers with quantifiers applied
        """
        contextualized_numbers = []
        processed_text = self._preprocess_text()

        # Define quantifiers and their multipliers
        quantifier_patterns = [
            (r"\b(\d+(?:,\d{3})*(?:\.\d+)?)\s+(millions?|mil)\b", 1_000_000),
            (r"\b(\d+(?:,\d{3})*(?:\.\d+)?)\s+(thousands?|k)\b", 1_000),
            (r"\b(\d+(?:,\d{3})*(?:\.\d+)?)\s+(billions?|bil)\b",
             1_000_000_000),
            (r"\b(\d+(?:,\d{3})*(?:\.\d+)?)\s+(trillions?|tril)\b",
             1_000_000_000_000),
        ]

        contextualized_raw_numbers = set()

        # Find numbers immediately followed by quantifiers
        for pattern, multiplier in quantifier_patterns:
            matches = re.finditer(pattern, processed_text, re.IGNORECASE)
            for match in matches:
                number_str = match.group(1)
                quantifier = match.group(2)

                logging.debug(
                    f"Page {self.page_number}: REGEX MATCH FOUND - Full match: '{match.group(0)}', Number: '{number_str}', Quantifier: '{quantifier}'"
                )

                parsed_value = self._parse_single_number(number_str)
                if parsed_value is not None:
                    contextualized_value = parsed_value * multiplier
                    contextualized_numbers.append(contextualized_value)
                    contextualized_raw_numbers.add(number_str)
                    logging.debug(
                        f"Page {self.page_number}: '{number_str} {quantifier}' -> {contextualized_value:,.2f}"
                    )

        for raw_number in self.raw_numbers:
            if raw_number not in contextualized_raw_numbers:
                parsed_value = self._parse_single_number(raw_number)
                if parsed_value is not None:
                    contextualized_numbers.append(parsed_value)

        return contextualized_numbers
