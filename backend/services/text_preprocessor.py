import re


def clean_text(text):
    """
    Clean and normalize extracted resume text.
    """

    if not text:
        return ""

    # Normalize line breaks
    text = text.replace("\r\n", "\n")
    text = text.replace("\r", "\n")

    # Remove unwanted non-printable characters
    text = "".join(
        character
        for character in text
        if character.isprintable() or character == "\n"
    )

    # Normalize common OCR-generated whitespace
    text = re.sub(r"[ \t]+", " ", text)

    # Remove excessive blank lines
    text = re.sub(r"\n\s*\n+", "\n\n", text)

    # Remove obvious OCR noise characters when they appear
    # as isolated characters rather than meaningful text.
    text = re.sub(
        r"(?m)^\s*[|~©®§]+\s*$",
        "",
        text
    )

    # Remove repeated standalone punctuation noise
    text = re.sub(
        r"(?m)^\s*[/\\|~`^]+\s*$",
        "",
        text
    )

    return text.strip()


def normalize_text(text):
    """
    Create a normalized version of the text
    for analysis and matching.
    """

    if not text:
        return ""

    text = clean_text(text)

    # Remove email addresses
    text = re.sub(
        r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b",
        " ",
        text
    )

    # Remove URLs
    text = re.sub(
        r"https?://\S+|www\.\S+",
        " ",
        text
    )

    # Convert to lowercase
    text = text.lower()

    # Normalize common separators
    text = re.sub(r"[•●▪]", "-", text)

    # Remove repeated spaces
    text = re.sub(r"\s+", " ", text)

    return text.strip()