import os
import re
import pandas as pd


ESCO_RELATIONS_FILE = os.path.join(
    "data",
    "esco",
    "broaderRelationsSkillPillar_en.csv"
)


def load_broader_relations():
    if not os.path.exists(ESCO_RELATIONS_FILE):
        return pd.DataFrame()

    df = pd.read_csv(ESCO_RELATIONS_FILE)

    required_columns = {
        "conceptUri",
        "broaderUri"
    }

    if not required_columns.issubset(df.columns):
        return pd.DataFrame()

    return (
        df[
            [
                "conceptUri",
                "broaderUri"
            ]
        ]
        .dropna()
        .drop_duplicates()
    )


def normalize_label(label):
    if not isinstance(label, str):
        return ""

    label = label.lower()

    label = re.sub(
        r"[^a-z0-9+#.]+",
        " ",
        label
    )

    label = re.sub(
        r"\s+",
        " ",
        label
    )

    return label.strip()


def get_concept_key(concept):
    """
    Create a stable identity for a technical concept.

    ESCO:
        concept URI identifies the concept.

    O*NET:
        technology name identifies the software technology.

    We intentionally DO NOT use O*NET Element ID as the
    technology identity because multiple technologies can
    share the same O*NET element/category.
    """

    if concept.get("concept_uri"):

        return (
            "esco",
            concept["concept_uri"]
        )

    if concept.get("technology"):

        technology = normalize_label(
            concept["technology"]
        )

        if technology:

            return (
                "onet",
                technology
            )

    if concept.get("element_id"):

        return (
            "onet_element",
            concept["element_id"]
        )

    return None


def get_concept_label(concept):
    """
    Return the most useful user-facing label.
    """

    if concept.get("preferred_label"):

        return concept["preferred_label"]

    if concept.get("technology"):

        return concept["technology"]

    if concept.get("element_name"):

        return concept["element_name"]

    return ""


def analyze_keywords(resume_analysis, job_analysis):
    """
    Compare technical concepts extracted by ResuMatch.

    Exact ESCO/O*NET matches receive full credit.

    Related ESCO concepts receive partial credit.

    O*NET technologies are identified by their technology
    names rather than their shared Element IDs.
    """

    resume_concepts = resume_analysis.get(
        "technical_concepts",
        []
    )

    job_concepts = job_analysis.get(
        "technical_concepts",
        []
    )

    # --------------------------------
    # Build resume concept map
    # --------------------------------

    resume_map = {}

    for concept in resume_concepts:

        key = get_concept_key(concept)

        if key:

            resume_map[key] = concept

    # --------------------------------
    # Build job concept map
    # --------------------------------

    job_map = {}

    for concept in job_concepts:

        key = get_concept_key(concept)

        if key:

            job_map[key] = concept

    resume_keys = set(
        resume_map.keys()
    )

    job_keys = set(
        job_map.keys()
    )

    # --------------------------------
    # Exact matches
    # --------------------------------

    exact_keys = (
        resume_keys.intersection(
            job_keys
        )
    )

    matched_keywords = []

    for key in exact_keys:

        job_concept = job_map[key]

        label = get_concept_label(
            job_concept
        )

        if label:

            matched_keywords.append(
                label
            )

    # --------------------------------
    # Related ESCO concepts
    # --------------------------------

    broader_relations = (
        load_broader_relations()
    )

    related_keywords = []

    related_keys = set()

    if not broader_relations.empty:

        resume_esco_uris = {
            concept["concept_uri"]
            for concept in resume_concepts
            if concept.get("concept_uri")
        }

        job_esco_uris = {
            concept["concept_uri"]
            for concept in job_concepts
            if concept.get("concept_uri")
        }

        exact_esco_uris = {
            key[1]
            for key in exact_keys
            if key[0] == "esco"
        }

        for _, row in broader_relations.iterrows():

            specific_uri = row[
                "conceptUri"
            ]

            broader_uri = row[
                "broaderUri"
            ]

            if (
                specific_uri
                in resume_esco_uris
                and
                broader_uri
                in job_esco_uris
                and
                broader_uri
                not in exact_esco_uris
            ):

                job_key = (
                    "esco",
                    broader_uri
                )

                if job_key in related_keys:
                    continue

                job_concept = job_map.get(
                    job_key
                )

                if not job_concept:
                    continue

                resume_concept = resume_map.get(
                    (
                        "esco",
                        specific_uri
                    )
                )

                if not resume_concept:
                    continue

                job_label = get_concept_label(
                    job_concept
                )

                resume_label = get_concept_label(
                    resume_concept
                )

                if not job_label:
                    continue

                related_keywords.append(
                    {
                        "job_keyword": job_label,
                        "resume_concept": resume_label,
                        "match_type": "related",
                        "match_weight": 0.5
                    }
                )

                related_keys.add(
                    job_key
                )

    # --------------------------------
    # Missing concepts
    # --------------------------------

    missing_keys = (
        job_keys
        - exact_keys
        - related_keys
    )

    missing_keywords = []

    for key in missing_keys:

        job_concept = job_map[key]

        label = get_concept_label(
            job_concept
        )

        if label:

            missing_keywords.append(
                label
            )

    # --------------------------------
    # Coverage
    # --------------------------------

    job_keyword_count = len(
        job_keys
    )

    matched_count = len(
        exact_keys
    )

    related_count = len(
        related_keys
    )

    coverage_score = (
        matched_count
        +
        (related_count * 0.5)
    )

    if job_keyword_count == 0:

        keyword_coverage = 0.0

    else:

        keyword_coverage = round(
            (
                coverage_score
                /
                job_keyword_count
            )
            * 100,
            2
        )

    # --------------------------------
    # Final result
    # --------------------------------

    return {
        "keyword_coverage_percentage":
            keyword_coverage,

        "matched_keywords":
            sorted(
                matched_keywords,
                key=lambda item: item.lower()
            ),

        "related_keywords":
            sorted(
                related_keywords,
                key=lambda item:
                    item["job_keyword"].lower()
            ),

        "missing_keywords":
            sorted(
                missing_keywords,
                key=lambda item: item.lower()
            ),

        "matched_count":
            matched_count,

        "related_count":
            related_count,

        "missing_count":
            len(missing_keywords),

        "job_keyword_count":
            job_keyword_count
    }