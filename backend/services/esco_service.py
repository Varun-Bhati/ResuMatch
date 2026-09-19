import os
import re
from functools import lru_cache

import pandas as pd


ESCO_FILE = os.path.join(
    "data",
    "esco",
    "skills_en.csv"
)


def load_esco_skills():
    """
    Load skill/competence and knowledge concepts
    from the ESCO dataset.
    """

    if not os.path.exists(
        ESCO_FILE
    ):
        raise FileNotFoundError(
            f"ESCO skills file not found: {ESCO_FILE}"
        )

    df = pd.read_csv(
        ESCO_FILE
    )

    # Keep only useful ESCO concepts

    df = df[
        df["skillType"].isin(
            [
                "skill/competence",
                "knowledge"
            ]
        )
    ].copy()

    # Remove rows without a preferred label

    df = df.dropna(
        subset=[
            "preferredLabel"
        ]
    )

    return df


def get_esco_skill_count():
    """
    Return the number of available ESCO concepts.
    """

    df = load_esco_skills()

    return len(df)


def normalize_label(label):
    """
    Normalize an ESCO label for text matching.
    """

    if not isinstance(
        label,
        str
    ):
        return ""

    label = label.lower()

    # Replace punctuation/separators with spaces

    label = re.sub(
        r"[^a-z0-9+#.]+",
        " ",
        label
    )

    # Remove repeated spaces

    label = re.sub(
        r"\s+",
        " ",
        label
    )

    return label.strip()


def label_in_text(
    label,
    normalized_text
):
    """
    Check whether a complete ESCO label exists
    in the normalized text.
    """

    if not label:
        return False

    padded_label = (
        " "
        + label
        + " "
    )

    padded_text = (
        " "
        + normalized_text
        + " "
    )

    return padded_label in padded_text


def extract_alternative_labels(
    alt_labels
):
    """
    Convert the ESCO altLabels field into a clean
    list of alternative labels.

    ESCO stores multiple alternative labels in a
    newline-separated field.
    """

    if not isinstance(
        alt_labels,
        str
    ):
        return []

    labels = []

    for label in alt_labels.split(
        "\n"
    ):

        label = label.strip()

        if not label:
            continue

        labels.append(
            label
        )

    return labels


@lru_cache(maxsize=1)
def prepare_esco_concepts():
    """
    Load and preprocess ESCO concepts once.

    The returned structure contains normalized
    preferred labels and alternative labels so
    extraction does not repeatedly process the
    entire pandas DataFrame.
    """

    df = load_esco_skills()

    concepts = []

    for row in df.itertuples(
        index=False
    ):

        preferred_label = getattr(
            row,
            "preferredLabel",
            None
        )

        if not isinstance(
            preferred_label,
            str
        ):
            continue

        preferred_label = (
            preferred_label.strip()
        )

        if not preferred_label:
            continue

        normalized_preferred = (
            normalize_label(
                preferred_label
            )
        )

        if len(
            normalized_preferred
        ) < 3:
            continue

        alternative_labels = (
            extract_alternative_labels(
                getattr(
                    row,
                    "altLabels",
                    None
                )
            )
        )

        normalized_alternatives = []

        for label in alternative_labels:

            normalized_alternative = (
                normalize_label(
                    label
                )
            )

            if not normalized_alternative:
                continue

            if len(
                normalized_alternative
            ) < 4:
                continue

            normalized_alternatives.append(
                (
                    label,
                    normalized_alternative
                )
            )

        concepts.append(
            {
                "concept_uri": getattr(
                    row,
                    "conceptUri",
                    None
                ),
                "preferred_label": preferred_label,
                "normalized_preferred": (
                    normalized_preferred
                ),
                "skill_type": getattr(
                    row,
                    "skillType",
                    None
                ),
                "alternative_labels": (
                    alternative_labels
                ),
                "normalized_alternatives": (
                    normalized_alternatives
                )
            }
        )

    return concepts


def extract_esco_skills(text):
    """
    Extract ESCO skills and knowledge concepts
    from resume or job description text.

    Uses:

    - ESCO preferred labels
    - ESCO alternative labels

    The ESCO dataset is loaded and preprocessed
    once, then reused for subsequent requests.

    No manually maintained skill list is used.

    The returned concept also preserves the complete
    set of ESCO alternative labels so that other
    ResuMatch services can use the official ESCO
    terminology when merging concepts.
    """

    if not text or not text.strip():
        return []

    normalized_text = normalize_label(
        text
    )

    if not normalized_text:
        return []

    concepts = prepare_esco_concepts()

    matches = {}

    for concept in concepts:

        concept_uri = (
            concept["concept_uri"]
        )

        preferred_label = (
            concept["preferred_label"]
        )

        alternative_labels = (
            concept["alternative_labels"]
        )

        normalized_preferred = (
            concept["normalized_preferred"]
        )

        # -------------------------------------------------
        # 1. Check the preferred ESCO label
        # -------------------------------------------------

        if label_in_text(
            normalized_preferred,
            normalized_text
        ):

            matches[concept_uri] = {

                "concept_uri":
                    concept_uri,

                "preferred_label":
                    preferred_label,

                "skill_type":
                    concept["skill_type"],

                "matched_label":
                    preferred_label,

                "match_type":
                    "preferred",

                "alternative_labels":
                    alternative_labels
            }

            continue

        # -------------------------------------------------
        # 2. Check ESCO alternative labels
        # -------------------------------------------------

        for (
            label,
            normalized_alternative
        ) in concept[
            "normalized_alternatives"
        ]:

            if label_in_text(
                normalized_alternative,
                normalized_text
            ):

                matches[concept_uri] = {

                    "concept_uri":
                        concept_uri,

                    "preferred_label":
                        preferred_label,

                    "skill_type":
                        concept["skill_type"],

                    "matched_label":
                        label,

                    "match_type":
                        "alternative",

                    "alternative_labels":
                        alternative_labels
                }

                break

    return list(
        matches.values()
    )