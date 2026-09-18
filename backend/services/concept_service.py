import re


def normalize_concept_label(label):
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


def get_onet_concept_identity(concept):
    """
    Determine the technology identity represented by
    an O*NET match.

    When O*NET matched an acronym directly, the acronym
    is used as the concept identity.

    Example:

        Amazon Web Services AWS software
        matched_term = AWS

    becomes:

        aws

    This allows different O*NET descriptions of the same
    technology to be represented as one concept.
    """

    matched_term = concept.get("matched_term")
    match_source = concept.get("match_source")

    if (
        match_source == "onet_acronym"
        and isinstance(matched_term, str)
    ):
        normalized_matched_term = (
            normalize_concept_label(
                matched_term
            )
        )

        if normalized_matched_term:
            return normalized_matched_term

    technology = concept.get("technology")

    return normalize_concept_label(
        technology
    )


def merge_concepts(esco_matches, onet_matches):
    """
    Create one unified concept list from ESCO and O*NET.

    ESCO is kept as the primary structured concept source.

    O*NET technologies are added only when they are not
    already represented by an ESCO label or another O*NET
    concept identity.

    O*NET acronym matches use the matched technology term
    as their identity.

    Example:

        Amazon Web Services AWS software
        Amazon Web Services AWS CloudFormation
        Amazon Web Services AWS SageMaker

    all contain the O*NET matched technology:

        AWS

    Therefore they are represented by one unified concept.

    The same principle applies to O*NET SQL entries.
    """

    unified_concepts = []

    seen_esco_uris = set()

    seen_onet_identities = set()

    # All official ESCO labels through which a concept
    # can be identified.
    esco_labels = set()

    # ========================================================
    # 1. ADD ESCO CONCEPTS
    # ========================================================

    for concept in esco_matches:

        concept_uri = concept.get(
            "concept_uri"
        )

        if concept_uri in seen_esco_uris:
            continue

        seen_esco_uris.add(
            concept_uri
        )

        # Preferred label
        preferred_label = (
            normalize_concept_label(
                concept.get(
                    "preferred_label"
                )
            )
        )

        if preferred_label:
            esco_labels.add(
                preferred_label
            )

        # Matched label
        matched_label = (
            normalize_concept_label(
                concept.get(
                    "matched_label"
                )
            )
        )

        if matched_label:
            esco_labels.add(
                matched_label
            )

        # Official ESCO alternative labels
        alternative_labels = concept.get(
            "alternative_labels",
            []
        )

        if isinstance(
            alternative_labels,
            list
        ):
            for alternative_label in alternative_labels:

                normalized_alternative = (
                    normalize_concept_label(
                        alternative_label
                    )
                )

                if normalized_alternative:
                    esco_labels.add(
                        normalized_alternative
                    )

        unified_concepts.append(
            concept
        )

    # ========================================================
    # 2. ADD O*NET CONCEPTS
    # ========================================================

    for concept in onet_matches:

        technology_identity = (
            get_onet_concept_identity(
                concept
            )
        )

        if not technology_identity:
            continue

        # ----------------------------------------------------
        # Already represented by ESCO
        # ----------------------------------------------------

        if technology_identity in esco_labels:
            continue

        # ----------------------------------------------------
        # Avoid duplicate O*NET technology identities
        # ----------------------------------------------------

        if technology_identity in seen_onet_identities:
            continue

        seen_onet_identities.add(
            technology_identity
        )

        unified_concepts.append(
            concept
        )

    return unified_concepts