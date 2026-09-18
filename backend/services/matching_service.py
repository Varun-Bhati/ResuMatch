import os
import re

import pandas as pd


ESCO_RELATIONS_FILE = os.path.join(
    "data",
    "esco",
    "broaderRelationsSkillPillar_en.csv"
)


def normalize_concept_label(label):
    """
    Normalize a concept label so it can be
    compared consistently.
    """

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


def load_broader_relations():
    """
    Load direct broader relationships between
    ESCO concepts.
    """

    if not os.path.exists(
        ESCO_RELATIONS_FILE
    ):
        return pd.DataFrame()

    df = pd.read_csv(
        ESCO_RELATIONS_FILE
    )

    required_columns = {
        "conceptUri",
        "broaderUri"
    }

    if not required_columns.issubset(
        set(df.columns)
    ):
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


def get_concept_key(concept):
    """
    Return a unique identifier for either
    ESCO or O*NET concepts.

    ESCO:
        concept URI is the identity.

    O*NET:
        technology identity is the identity.

    We intentionally do NOT use O*NET Element ID
    as the technology identity because multiple
    technologies can share the same O*NET element.
    """

    # ----------------------------------------------------
    # ESCO concept
    # ----------------------------------------------------

    if concept.get("concept_uri"):

        return (
            "esco",
            concept["concept_uri"]
        )

    # ----------------------------------------------------
    # O*NET concept
    # ----------------------------------------------------

    if concept.get("technology"):

        matched_term = concept.get(
            "matched_term"
        )

        match_source = concept.get(
            "match_source"
        )

        # O*NET acronym identity
        #
        # Example:
        #
        # Amazon Web Services AWS software
        # matched_term = AWS
        #
        # Identity becomes:
        #
        # ("onet", "aws")

        if (
            match_source == "onet_acronym"
            and isinstance(
                matched_term,
                str
            )
        ):

            normalized_matched_term = (
                normalize_concept_label(
                    matched_term
                )
            )

            if normalized_matched_term:

                return (
                    "onet",
                    normalized_matched_term
                )

        # Normal O*NET technology identity

        technology = (
            normalize_concept_label(
                concept["technology"]
            )
        )

        if technology:

            return (
                "onet",
                technology
            )

    return None


def get_concept_label(concept):
    """
    Get a readable label from either
    ESCO or O*NET concept data.
    """

    if concept.get("preferred_label"):
        return concept[
            "preferred_label"
        ]

    if concept.get("technology"):
        return concept[
            "technology"
        ]

    if concept.get("element_name"):
        return concept[
            "element_name"
        ]

    return "Unknown"


def match_resume_to_job(
    resume_matches,
    job_matches
):
    """
    Compare technical concepts found in a resume
    with technical concepts found in a job description.

    Matching:

    1. Exact ESCO concept match = 100%
    2. Direct ESCO broader concept match = 50%
    3. Exact O*NET technology match = 100%
    4. No match = 0%

    ESCO concepts use their concept URI.

    O*NET concepts use their technology identity,
    not their Element ID.
    """

    if not job_matches:

        return {
            "match_percentage": 0,
            "matched": [],
            "related": [],
            "missing": [],
            "matched_count": 0,
            "related_count": 0,
            "missing_count": 0,
            "resume_concept_count": len(
                resume_matches
            ),
            "job_concept_count": 0
        }

    # ====================================================
    # 1. Build concept maps
    # ====================================================

    resume_by_key = {}

    job_by_key = {}

    for concept in resume_matches:

        key = get_concept_key(
            concept
        )

        if key:
            resume_by_key[key] = concept

    for concept in job_matches:

        key = get_concept_key(
            concept
        )

        if key:
            job_by_key[key] = concept

    resume_keys = set(
        resume_by_key.keys()
    )

    job_keys = set(
        job_by_key.keys()
    )

    # ====================================================
    # 2. Exact matching
    # ====================================================

    exact_keys = (
        resume_keys.intersection(
            job_keys
        )
    )

    matched = []

    for key in exact_keys:

        matched.append({

            "job_concept":
                job_by_key[key],

            "resume_concept":
                resume_by_key[key],

            "match_type":
                "exact",

            "match_weight":
                1.0
        })

    # ====================================================
    # 3. ESCO hierarchy matching
    # ====================================================

    broader_relations = (
        load_broader_relations()
    )

    related = []

    related_job_keys = set()

    if not broader_relations.empty:

        # Only ESCO concepts can use
        # ESCO hierarchy relationships.

        resume_esco_uris = {

            concept["concept_uri"]

            for concept in resume_matches

            if concept.get(
                "concept_uri"
            )
        }

        job_esco_uris = {

            concept["concept_uri"]

            for concept in job_matches

            if concept.get(
                "concept_uri"
            )
        }

        exact_esco_uris = {

            key[1]

            for key in exact_keys

            if key[0] == "esco"
        }

        for _, row in (
            broader_relations.iterrows()
        ):

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

                if (
                    job_key
                    in related_job_keys
                ):
                    continue

                resume_key = (
                    "esco",
                    specific_uri
                )

                job_concept = (
                    job_by_key.get(
                        job_key
                    )
                )

                resume_concept = (
                    resume_by_key.get(
                        resume_key
                    )
                )

                if not job_concept:
                    continue

                if not resume_concept:
                    continue

                related.append({

                    "job_concept":
                        job_concept,

                    "resume_concept":
                        resume_concept,

                    "match_type":
                        "broader",

                    "match_weight":
                        0.5
                })

                related_job_keys.add(
                    job_key
                )

    # ====================================================
    # 4. Find missing concepts
    # ====================================================

    missing_keys = (
        job_keys
        - exact_keys
        - related_job_keys
    )

    missing = [

        job_by_key[key]

        for key in missing_keys
    ]

    # ====================================================
    # 5. Calculate score
    # ====================================================

    exact_score = len(
        exact_keys
    )

    related_score = (
        len(
            related_job_keys
        )
        * 0.5
    )

    total_score = (
        exact_score
        + related_score
    )

    match_percentage = round(

        (
            total_score
            / len(job_keys)
        )
        * 100,

        2
    )

    # ====================================================
    # 6. Return complete result
    # ====================================================

    return {

        "match_percentage":
            match_percentage,

        "matched":
            matched,

        "related":
            related,

        "missing":
            missing,

        "matched_count":
            len(exact_keys),

        "related_count":
            len(
                related_job_keys
            ),

        "missing_count":
            len(missing_keys),

        "resume_concept_count":
            len(resume_keys),

        "job_concept_count":
            len(job_keys)
    }