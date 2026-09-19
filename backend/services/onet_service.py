import os
import re
from functools import lru_cache

import pandas as pd


ONET_FILE = os.path.join(
    "data",
    "onet",
    "software_skills.csv"
)


IGNORED_TERMS = {
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


SQL_EXAMPLES = {
    "structured query language sql",
    "structure query language sql"
}


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

    padded_label = " " + label + " "
    padded_text = " " + normalized_text + " "

    return padded_label in padded_text


def short_label_in_original_text(
    label,
    original_text
):

    if not label or not original_text:

        return False

    normalized_label = normalize_onet_text(
        label
    )

    normalized_text = normalize_onet_text(
        original_text
    )

    if not normalized_label or not normalized_text:

        return False

    padded_label = " " + normalized_label + " "
    padded_text = " " + normalized_text + " "

    return padded_label in padded_text


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

    if normalized_example in SQL_EXAMPLES:

        return "SQL"

    # For all other technologies, keep the original
    # O*NET Workplace Example.

    return workplace_example


@lru_cache(maxsize=1)
def prepare_onet_software():

    """
    Load and preprocess the O*NET software dataset once.

    The prepared data is cached so subsequent resume
    analyses do not repeatedly load the CSV or perform
    the same normalization and acronym extraction.
    """

    df = load_onet_software()

    exact_matches = {}
    acronym_matches = {}

    for row in df.itertuples(index=False):

        workplace_example = row[
            df.columns.get_loc("Workplace Example")
        ]

        if not isinstance(
            workplace_example,
            str
        ):

            continue

        workplace_example = workplace_example.strip()

        if not workplace_example:

            continue

        normalized_example = normalize_onet_text(
            workplace_example
        )

        if not normalized_example:

            continue

        if normalized_example in IGNORED_TERMS:

            continue

        if len(normalized_example) < 3:

            continue

        record = {
            "onet_soc_code": row[
                df.columns.get_loc("O*NET-SOC Code")
            ],
            "occupation": row[
                df.columns.get_loc("Title")
            ],
            "workplace_example": workplace_example,
            "normalized_example": normalized_example,
            "element_id": row[
                df.columns.get_loc("Element ID")
            ],
            "element_name": row[
                df.columns.get_loc("Element Name")
            ],
            "hot_technology": row[
                df.columns.get_loc("Hot Technology")
            ],
            "in_demand": row[
                df.columns.get_loc("In Demand")
            ]
        }

        exact_matches.setdefault(
            normalized_example,
            []
        ).append(record)

        acronyms = (
            extract_acronyms_from_workplace_example(
                workplace_example
            )
        )

        primary_acronyms = []

        for acronym in acronyms:

            # SQL is particularly ambiguous in O*NET.
            #
            # Only treat it as an acronym match for
            # the actual SQL language entries.

            if acronym.upper() == "SQL":

                if normalized_example not in SQL_EXAMPLES:

                    continue

            if not is_primary_acronym_entry(
                workplace_example,
                acronym
            ):

                continue

            primary_acronyms.append(
                acronym
            )

        for acronym in primary_acronyms:

            acronym_key = acronym.lower()

            acronym_matches.setdefault(
                acronym_key,
                []
            ).append(record)

    return (
        exact_matches,
        acronym_matches
    )


def extract_onet_software(text):

    if not text or not text.strip():

        return []

    normalized_text = normalize_onet_text(
        text
    )

    if not normalized_text:

        return []

    exact_matches, acronym_matches = (
        prepare_onet_software()
    )

    matches = {}

    # -------------------------------------------------
    # 1. Exact Workplace Example matches
    # -------------------------------------------------

    for normalized_example, records in (
        exact_matches.items()
    ):

        if not label_in_text(
            normalized_example,
            normalized_text
        ):

            continue

        for record in records:

            workplace_example = record[
                "workplace_example"
            ]

            matched_term = workplace_example
            match_source = "workplace_example"

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

                "onet_soc_code": record[
                    "onet_soc_code"
                ],

                "occupation": record[
                    "occupation"
                ],

                "technology": technology,

                "matched_term": matched_term,

                "match_source": match_source,

                "element_id": record[
                    "element_id"
                ],

                "element_name": record[
                    "element_name"
                ],

                "hot_technology": record[
                    "hot_technology"
                ],

                "in_demand": record[
                    "in_demand"
                ]
            }

    # -------------------------------------------------
    # 2. Primary acronym matching
    # -------------------------------------------------

    resume_acronyms = set(
        extract_acronyms_from_workplace_example(
            text
        )
    )

    for acronym in resume_acronyms:

        acronym_key = acronym.lower()

        records = acronym_matches.get(
            acronym_key,
            []
        )

        if not records:

            continue

        for record in records:

            workplace_example = record[
                "workplace_example"
            ]

            if not is_primary_acronym_entry(
                workplace_example,
                acronym
            ):

                continue

            matched_term = acronym
            match_source = "onet_acronym"

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

                "onet_soc_code": record[
                    "onet_soc_code"
                ],

                "occupation": record[
                    "occupation"
                ],

                "technology": technology,

                "matched_term": matched_term,

                "match_source": match_source,

                "element_id": record[
                    "element_id"
                ],

                "element_name": record[
                    "element_name"
                ],

                "hot_technology": record[
                    "hot_technology"
                ],

                "in_demand": record[
                    "in_demand"
                ]
            }

    return list(matches.values())