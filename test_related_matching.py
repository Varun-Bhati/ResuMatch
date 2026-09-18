import os
import pandas as pd

from backend.services.matching_service import (
    match_resume_to_job
)


ESCO_SKILLS_FILE = os.path.join(
    "data",
    "esco",
    "skills_en.csv"
)

ESCO_RELATIONS_FILE = os.path.join(
    "data",
    "esco",
    "broaderRelationsSkillPillar_en.csv"
)


print("=" * 80)
print("RESUMATCH ESCO RELATED MATCHING DIAGNOSTIC")
print("=" * 80)


# ============================================================
# 1. Load ESCO concepts
# ============================================================

skills_df = pd.read_csv(
    ESCO_SKILLS_FILE
)

skills_df = skills_df[
    skills_df["skillType"].isin(
        [
            "skill/competence",
            "knowledge"
        ]
    )
].copy()

skills_df = skills_df.dropna(
    subset=[
        "conceptUri",
        "preferredLabel"
    ]
)


# ============================================================
# 2. Load ESCO relationships
# ============================================================

relations_df = pd.read_csv(
    ESCO_RELATIONS_FILE
)

required_columns = {
    "conceptUri",
    "broaderUri"
}

if not required_columns.issubset(
    set(relations_df.columns)
):
    print()
    print("ERROR: Required ESCO relationship columns not found.")
    raise SystemExit


relations_df = relations_df[
    [
        "conceptUri",
        "broaderUri"
    ]
].dropna().drop_duplicates()


# ============================================================
# 3. Build concept lookup
# ============================================================

concept_lookup = {}

for _, row in skills_df.iterrows():

    concept_lookup[
        row["conceptUri"]
    ] = {
        "concept_uri":
            row["conceptUri"],

        "preferred_label":
            row["preferredLabel"],

        "matched_label":
            row["preferredLabel"],

        "skill_type":
            row["skillType"],

        "match_type":
            "preferred"
    }


# ============================================================
# 4. Find a usable direct relationship
# ============================================================

test_relation = None

for _, row in relations_df.iterrows():

    specific_uri = row[
        "conceptUri"
    ]

    broader_uri = row[
        "broaderUri"
    ]

    if (
        specific_uri in concept_lookup
        and
        broader_uri in concept_lookup
    ):

        test_relation = (
            specific_uri,
            broader_uri
        )

        break


if test_relation is None:

    print()
    print("ERROR: No usable ESCO relationship was found.")
    raise SystemExit


specific_uri, broader_uri = test_relation


specific_concept = concept_lookup[
    specific_uri
]

broader_concept = concept_lookup[
    broader_uri
]


# ============================================================
# 5. Display selected relationship
# ============================================================

print()
print("=" * 80)
print("TEST RELATION")
print("=" * 80)

print()
print(
    "Resume concept:"
)

print(
    f"  {specific_concept['preferred_label']}"
)

print()
print(
    "Job concept:"
)

print(
    f"  {broader_concept['preferred_label']}"
)

print()
print(
    "Specific URI:"
)

print(
    f"  {specific_uri}"
)

print()
print(
    "Broader URI:"
)

print(
    f"  {broader_uri}"
)


# ============================================================
# 6. Run the actual matcher
# ============================================================

resume_matches = [
    specific_concept
]

job_matches = [
    broader_concept
]


result = match_resume_to_job(
    resume_matches,
    job_matches
)


# ============================================================
# 7. Display result
# ============================================================

print()
print("=" * 80)
print("MATCHING RESULT")
print("=" * 80)

print()
print(
    "Match percentage:"
)

print(
    result.get(
        "match_percentage"
    )
)

print()
print(
    "Matched count:"
)

print(
    result.get(
        "matched_count"
    )
)

print()
print(
    "Related count:"
)

print(
    result.get(
        "related_count"
    )
)

print()
print(
    "Missing count:"
)

print(
    result.get(
        "missing_count"
    )
)


print()
print(
    "Related matches:"
)

for item in result.get(
    "related",
    []
):

    resume_concept = item.get(
        "resume_concept",
        {}
    )

    job_concept = item.get(
        "job_concept",
        {}
    )

    print(
        f"  - "
        f"{resume_concept.get('preferred_label')}"
        f" -> "
        f"{job_concept.get('preferred_label')}"
    )

    print(
        f"    match_type: "
        f"{item.get('match_type')}"
    )

    print(
        f"    match_weight: "
        f"{item.get('match_weight')}"
    )


print()
print(
    "Missing matches:"
)

for concept in result.get(
    "missing",
    []
):

    print(
        f"  - "
        f"{concept.get('preferred_label')}"
    )


print()
print("=" * 80)
print("RELATED MATCHING DIAGNOSTIC COMPLETE")
print("=" * 80)