import os
import re
from functools import lru_cache

import pandas as pd


ESCO_RELATIONS_FILE = os.path.join(
    "data",
    "esco",
    "broaderRelationsSkillPillar_en.csv"
)


# ============================================================
# Cross-source technology identities
# ============================================================
#
# Some technologies can appear in both ESCO and O*NET.
#
# ESCO identifies concepts using a concept URI, while O*NET
# identifies technologies using the technology name.
#
# For these shared technologies, use the normalized technology
# name as the identity so ESCO and O*NET can match each other.
#
CROSS_SOURCE_TECHNOLOGIES = {
    "javascript",
    "typescript",
    "node.js",
}


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


@lru_cache(maxsize=1)
def load_broader_relations():
    """
    Load direct broader relationships between
    ESCO concepts once and cache them in memory.
    """

    if not os.path.exists(
        ESCO_RELATIONS_FILE
    ):
        return set()

    df = pd.read_csv(
        ESCO_RELATIONS_FILE,
        usecols=[
            "conceptUri",
            "broaderUri"
        ]
    )

    df = (
        df[
            [
                "conceptUri",
                "broaderUri"
            ]
        ]
        .dropna()
        .drop_duplicates()
    )

    return set(
        zip(
            df["conceptUri"],
            df["broaderUri"]
        )
    )


def get_concept_key(concept):
    """
    Return a unique identifier for ESCO or O*NET concepts.

    ESCO:
        Normally uses the concept URI.

    O*NET:
        Normally uses the technology identity.

    Cross-source technologies:
        Known technologies that can appear in both ESCO
        and O*NET use a shared technology identity.

    This allows concepts such as:

        ESCO JavaScript <-> O*NET JavaScript
        ESCO TypeScript <-> O*NET TypeScript
        ESCO Node.js    <-> O*NET Node.js
    """

    # ----------------------------------------------------
    # 1. Cross-source technology identity
    # ----------------------------------------------------
    #
    # Check the readable technology/label before assigning
    # the source-specific ESCO or O*NET identity.
    #
    possible_labels = [
        concept.get("technology"),
        concept.get("preferred_label"),
        concept.get("matched_label"),
        concept.get("element_name")
    ]

    for label in possible_labels:

        normalized_label = normalize_concept_label(
            label
        )

        if normalized_label in CROSS_SOURCE_TECHNOLOGIES:

            return (
                "technology",
                normalized_label
            )

    # ----------------------------------------------------
    # 2. ESCO concept
    # ----------------------------------------------------

    if concept.get("concept_uri"):

        return (
            "esco",
            concept["concept_uri"]
        )

    # ----------------------------------------------------
    # 3. O*NET concept
    # ----------------------------------------------------

    if concept.get("technology"):

        matched_term = concept.get(
            "matched_term"
        )

        match_source = concept.get(
            "match_source"
        )

        # ------------------------------------------------
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
        # ------------------------------------------------

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

        # ------------------------------------------------
        # Normal O*NET technology identity
        # ------------------------------------------------

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
    4. Cross-source technology match = 100%
    5. No match = 0%

    ESCO concepts normally use their concept URI.

    O*NET concepts normally use their technology identity.

    Shared technologies such as JavaScript, TypeScript,
    and Node.js use a common cross-source identity.
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

    if broader_relations:

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

        # ------------------------------------------------
        # Direct lookup of relationships for each
        # resume ESCO concept.
        # ------------------------------------------------

        for specific_uri in resume_esco_uris:

            for (
                relation_specific_uri,
                broader_uri
            ) in broader_relations:

                if (
                    relation_specific_uri
                    != specific_uri
                ):
                    continue

                if (
                    broader_uri
                    not in job_esco_uris
                ):
                    continue

                if (
                    broader_uri
                    in exact_esco_uris
                ):
                    continue

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