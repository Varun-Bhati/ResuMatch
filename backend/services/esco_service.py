import os
import re
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

    if not os.path.exists(ESCO_FILE):
        raise FileNotFoundError(
            f"ESCO skills file not found: {ESCO_FILE}"
        )

    df = pd.read_csv(ESCO_FILE)

    # Keep only useful ESCO concepts
    df = df[
        df["skillType"].isin(
            ["skill/competence", "knowledge"]
        )
    ].copy()

    # Remove rows without a preferred label
    df = df.dropna(
        subset=["preferredLabel"]
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

    if not isinstance(label, str):
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


def label_in_text(label, normalized_text):
    """
    Check whether a complete ESCO label exists
    in the normalized text.
    """

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


def extract_alternative_labels(alt_labels):
    """
    Convert the ESCO altLabels field into a clean
    list of alternative labels.

    ESCO stores multiple alternative labels in a
    newline-separated field.
    """

    if not isinstance(alt_labels, str):
        return []

    labels = []

    for label in alt_labels.split("\n"):

        label = label.strip()

        if not label:
            continue

        labels.append(label)

    return labels


def extract_esco_skills(text):
    """
    Extract ESCO skills and knowledge concepts
    from resume text.

    Uses:

    - ESCO preferred labels
    - ESCO alternative labels

    No manually maintained skill list is used.

    The returned concept also preserves the complete
    set of ESCO alternative labels so that other
    ResuMatch services can use the official ESCO
    terminology when merging concepts.
    """

    if not text or not text.strip():
        return []

    df = load_esco_skills()

    normalized_text = normalize_label(text)

    matches = {}

    for _, row in df.iterrows():

        preferred_label = row["preferredLabel"]

        alternative_labels = (
            extract_alternative_labels(
                row["altLabels"]
            )
        )

        # -------------------------------------------------
        # 1. Check the preferred ESCO label
        # -------------------------------------------------

        normalized_preferred = normalize_label(
            preferred_label
        )

        if (
            len(normalized_preferred) >= 3
            and label_in_text(
                normalized_preferred,
                normalized_text
            )
        ):

            concept_uri = row["conceptUri"]

            matches[concept_uri] = {
                "concept_uri": concept_uri,
                "preferred_label": preferred_label,
                "skill_type": row["skillType"],
                "matched_label": preferred_label,
                "match_type": "preferred",
                "alternative_labels": alternative_labels
            }

            continue

        # -------------------------------------------------
        # 2. Check ESCO alternative labels
        # -------------------------------------------------

        for label in alternative_labels:

            normalized_alternative = normalize_label(
                label
            )

            if not normalized_alternative:
                continue

            # Ignore extremely short alternative labels.
            # This helps avoid false matches.
            if len(normalized_alternative) < 4:
                continue

            if label_in_text(
                normalized_alternative,
                normalized_text
            ):

                concept_uri = row["conceptUri"]

                matches[concept_uri] = {
                    "concept_uri": concept_uri,
                    "preferred_label": preferred_label,
                    "skill_type": row["skillType"],
                    "matched_label": label,
                    "match_type": "alternative",
                    "alternative_labels": alternative_labels
                }

                break

    return list(matches.values())