import os
import re
import pandas as pd


ONET_FILE = os.path.join(
    "data",
    "onet",
    "software_skills.csv"
)


def load_onet_software():
    if not os.path.exists(ONET_FILE):
        raise FileNotFoundError(
            f"O*NET software skills file not found: {ONET_FILE}"
        )

    df = pd.read_csv(ONET_FILE)

    required_columns = {
        "O*NET-SOC Code",
        "Title",
        "Workplace Example",
        "Element ID",
        "Element Name",
        "Hot Technology",
        "In Demand"
    }

    missing_columns = required_columns - set(df.columns)

    if missing_columns:
        raise ValueError(
            f"Missing O*NET columns: {missing_columns}"
        )

    return df


def normalize_onet_text(text):
    if not isinstance(text, str):
        return ""

    text = text.lower()

    text = re.sub(
        r"[^a-z0-9+#.]+",
        " ",
        text
    )

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


def label_in_text(label, normalized_text):
    if not label:
        return False

    pattern = (
        r"(?<!\w)"
        + re.escape(label)
        + r"(?!\w)"
    )

    return re.search(
        pattern,
        normalized_text
    ) is not None


def short_label_in_original_text(
    label,
    original_text
):
    if not label or not original_text:
        return False

    pattern = (
        r"(?<![\w.])"
        + re.escape(label)
        + r"(?!\w)"
    )

    return re.search(
        pattern,
        original_text
    ) is not None


def extract_acronyms_from_workplace_example(
    workplace_example
):
    """
    Extract uppercase acronym-like tokens directly
    from the O*NET Workplace Example.
    """

    if not isinstance(workplace_example, str):
        return []

    acronym_pattern = r"\b[A-Z][A-Z0-9+#.]{1,9}\b"

    return re.findall(
        acronym_pattern,
        workplace_example
    )


def is_primary_acronym_entry(
    workplace_example,
    acronym
):
    """
    Determine whether an acronym is being used as
    the primary technology identity.

    Examples accepted:

        Structured query language SQL
        Structure query language SQL
        Amazon Web Services AWS software

    Examples rejected:

        Oracle PL/SQL
        SAP Sybase SQL Anywhere
        Data Recovery Software SQL Server Data Recovery
    """

    if not workplace_example or not acronym:
        return False

    words = workplace_example.split()

    cleaned_words = []

    for word in words:

        cleaned_word = re.sub(
            r"[^A-Za-z0-9+#.]",
            "",
            word
        )

        if cleaned_word:
            cleaned_words.append(
                cleaned_word
            )

    if acronym not in cleaned_words:
        return False

    acronym_index = cleaned_words.index(
        acronym
    )

    if acronym_index < 2:
        return False

    words_before = cleaned_words[
        :acronym_index
    ]

    for word in words_before:

        if len(word) <= 2:
            return False

        if word.isupper():
            return False

    return True


def get_canonical_technology(
    workplace_example,
    matched_term
):
    """
    Convert duplicate O*NET technology descriptions
    into one canonical technology label.

    This is intentionally limited to cases where O*NET
    itself contains duplicate descriptions for the same
    technology.

    We do NOT collapse related technologies such as:

        AWS
        AWS CloudFormation
        AWS SageMaker

    because they are distinct technologies.
    """

    normalized_example = normalize_onet_text(
        workplace_example
    )

    # O*NET contains two nearly identical descriptions
    # for the SQL programming language.
    if normalized_example in {
        "structured query language sql",
        "structure query language sql"
    }:
        return "SQL"

    # For all other technologies, keep the original
    # O*NET Workplace Example.
    return workplace_example


def extract_onet_software(text):
    if not text or not text.strip():
        return []

    df = load_onet_software()

    normalized_text = normalize_onet_text(text)

    matches = {}

    ignored_terms = {
        "analyze",
        "analyse",
        "use",
        "using",
        "manage",
        "management",
        "create",
        "develop",
        "development",
        "design",
        "test",
        "testing"
    }

    for _, row in df.iterrows():

        workplace_example = row["Workplace Example"]

        if not isinstance(workplace_example, str):
            continue

        workplace_example = workplace_example.strip()

        normalized_workplace_example = (
            normalize_onet_text(
                workplace_example
            )
        )

        if not normalized_workplace_example:
            continue

        if normalized_workplace_example in ignored_terms:
            continue

        if len(normalized_workplace_example) < 3:
            continue

        matched_term = None
        match_source = None

        # ---------------------------------------------
        # 1. Exact Workplace Example match
        # ---------------------------------------------

        if len(normalized_workplace_example) <= 3:

            if short_label_in_original_text(
                workplace_example,
                text
            ):
                matched_term = workplace_example
                match_source = "workplace_example"

        else:

            if label_in_text(
                normalized_workplace_example,
                normalized_text
            ):
                matched_term = workplace_example
                match_source = "workplace_example"

        # ---------------------------------------------
        # 2. Primary acronym matching
        # ---------------------------------------------

        if matched_term is None:

            acronyms = (
                extract_acronyms_from_workplace_example(
                    workplace_example
                )
            )

            for acronym in acronyms:

                # SQL is particularly ambiguous in O*NET.
                #
                # Only treat it as an acronym match for
                # the actual SQL language entries that exist
                # in the dataset.
                if acronym.upper() == "SQL":

                    normalized_example = (
                        normalize_onet_text(
                            workplace_example
                        )
                    )

                    if normalized_example not in {
                        "structured query language sql",
                        "structure query language sql"
                    }:
                        continue

                if not is_primary_acronym_entry(
                    workplace_example,
                    acronym
                ):
                    continue

                if not short_label_in_original_text(
                    acronym,
                    text
                ):
                    continue

                matched_term = acronym
                match_source = "onet_acronym"

                break

        # ---------------------------------------------
        # No match
        # ---------------------------------------------

        if matched_term is None:
            continue

        # ---------------------------------------------
        # Canonical technology label
        # ---------------------------------------------

        technology = get_canonical_technology(
            workplace_example,
            matched_term
        )

        technology_key = normalize_onet_text(
            technology
        )

        key = (
            technology_key,
            matched_term.lower()
        )

        matches[key] = {
            "source": "onet",
            "onet_soc_code": row["O*NET-SOC Code"],
            "occupation": row["Title"],
            "technology": technology,
            "matched_term": matched_term,
            "match_source": match_source,
            "element_id": row["Element ID"],
            "element_name": row["Element Name"],
            "hot_technology": row["Hot Technology"],
            "in_demand": row["In Demand"]
        }

    return list(matches.values())