import re


SECTION_ALIASES = {
    "summary": [
        "summary",
        "professional summary",
        "career summary",
        "profile",
        "objective",
        "career objective",
    ],

    "education": [
        "education",
        "academic background",
        "academic qualification",
        "qualifications",
    ],

    "experience": [
        "experience",
        "work experience",
        "professional experience",
        "employment",
        "work history",
    ],

    "projects": [
        "projects",
        "personal projects",
        "academic projects",
        "project experience",
    ],

    "skills": [
        "skills",
        "technical skills",
        "core skills",
        "technical expertise",
        "technologies",
    ],
}


def normalize_heading(text):
    """
    Normalize a heading so section detection is
    consistent with the existing section detector.
    """

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


def extract_section_content(text, section):
    """
    Extract the approximate text belonging to one
    resume section.

    The actual section detection is handled by
    section_detector.py.
    """

    if not text or section not in SECTION_ALIASES:
        return ""

    lines = text.splitlines()

    aliases = {
        normalize_heading(alias)
        for alias in SECTION_ALIASES[section]
    }

    start_index = None

    for index, line in enumerate(lines):

        normalized_line = normalize_heading(line)

        if normalized_line in aliases:

            start_index = index + 1
            break

    if start_index is None:
        return ""

    next_section_aliases = set()

    for alias_list in SECTION_ALIASES.values():

        for alias in alias_list:

            next_section_aliases.add(
                normalize_heading(alias)
            )

    section_lines = []

    for line in lines[start_index:]:

        normalized_line = normalize_heading(line)

        if normalized_line in next_section_aliases:
            break

        section_lines.append(line)

    return "\n".join(section_lines).strip()


def count_section_words(text, section):
    """
    Count words inside one detected resume section.
    """

    section_content = extract_section_content(
        text,
        section
    )

    if not section_content:
        return 0

    return len(section_content.split())


def calculate_content_length_score(word_count):
    """
    Score the amount of resume content.

    The goal is not to reward verbosity.
    The score rewards a reasonable amount of
    substantive resume content.

    Maximum: 15
    """

    if 300 <= word_count <= 900:
        return 15

    if 200 <= word_count < 300:
        return 12

    if 901 <= word_count <= 1100:
        return 12

    if 150 <= word_count < 200:
        return 8

    if 1101 <= word_count <= 1200:
        return 8

    if 100 <= word_count < 150:
        return 4

    if 1201 <= word_count <= 1400:
        return 4

    return 0


def calculate_structure_score(
    sections,
    section_word_counts
):
    """
    Evaluate whether important resume sections exist
    and contain meaningful content.

    Maximum: 20
    """

    important_sections = [
        "summary",
        "education",
        "experience",
        "projects",
        "skills",
    ]

    score = 0

    for section in important_sections:

        if not sections.get(section):
            continue

        word_count = section_word_counts.get(
            section,
            0
        )

        if word_count >= 15:
            score += 4

        elif word_count > 0:
            score += 2

    return min(score, 20)


def normalize_concept_label(label):
    """
    Normalize a detected technical concept label
    for deduplication.
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


def get_concept_label(concept):
    """
    Get the user-facing label from either ESCO
    or O*NET concept data.
    """

    if not isinstance(concept, dict):
        return ""

    if concept.get("preferred_label"):
        return concept["preferred_label"]

    if concept.get("matched_label"):
        return concept["matched_label"]

    if concept.get("technology"):
        return concept["technology"]

    if concept.get("element_name"):
        return concept["element_name"]

    return ""


def count_unique_technical_concepts(
    skills,
    knowledge,
    technologies
):
    """
    Count unique recognized technical concepts.

    ESCO knowledge is included because ESCO can classify
    legitimate technical areas such as Python and SQL
    as knowledge.

    O*NET technologies are also included.

    Duplicate labels are counted only once.
    """

    labels = set()

    for concept_group in [
        skills,
        knowledge,
        technologies,
    ]:

        for concept in concept_group:

            label = get_concept_label(
                concept
            )

            normalized = normalize_concept_label(
                label
            )

            if normalized:
                labels.add(normalized)

    return len(labels)


def calculate_skills_knowledge_score(
    skills,
    knowledge,
    technologies
):
    """
    Evaluate the breadth of the technical profile.

    Maximum: 20

    ESCO skillType is not treated as a quality judgment.
    Recognized ESCO knowledge and O*NET technologies also
    contribute because they represent useful technical
    concepts found in the resume.
    """

    unique_concept_count = (
        count_unique_technical_concepts(
            skills,
            knowledge,
            technologies
        )
    )

    if unique_concept_count >= 8:
        return 20

    if unique_concept_count >= 6:
        return 17

    if unique_concept_count >= 4:
        return 13

    if unique_concept_count >= 3:
        return 10

    if unique_concept_count >= 2:
        return 7

    if unique_concept_count == 1:
        return 4

    return 0


def calculate_section_content_score(
    section_word_count,
    maximum
):
    """
    Convert section content into a proportional score.

    Used for experience and projects.
    """

    if section_word_count >= 80:
        return maximum

    if section_word_count >= 50:
        return round(maximum * 0.8)

    if section_word_count >= 25:
        return round(maximum * 0.6)

    if section_word_count >= 10:
        return round(maximum * 0.3)

    if section_word_count > 0:
        return round(maximum * 0.15)

    return 0


def calculate_experience_projects_score(
    sections,
    section_word_counts
):
    """
    Evaluate experience and project content.

    Maximum: 20

    Experience: 10
    Projects: 10
    """

    experience_score = 0
    projects_score = 0

    if sections.get("experience"):

        experience_score = (
            calculate_section_content_score(
                section_word_counts.get(
                    "experience",
                    0
                ),
                10
            )
        )

    if sections.get("projects"):

        projects_score = (
            calculate_section_content_score(
                section_word_counts.get(
                    "projects",
                    0
                ),
                10
            )
        )

    return experience_score + projects_score


def detect_contact_signals(text):
    """
    Detect common professional contact signals.
    """

    if not text:
        return {
            "email_found": False,
            "phone_found": False,
            "professional_profile_found": False,
        }

    email_found = bool(
        re.search(
            r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b",
            text
        )
    )

    phone_found = bool(
        re.search(
            r"(?<!\d)(?:\+?\d[\d\s().-]{8,}\d)(?!\d)",
            text
        )
    )

    professional_profile_found = bool(
        re.search(
            r"\b(?:linkedin\.com|github\.com)\b",
            text,
            re.IGNORECASE
        )
    )

    return {
        "email_found": email_found,
        "phone_found": phone_found,
        "professional_profile_found": professional_profile_found,
    }


def calculate_contact_score(text):
    """
    Evaluate basic professional contact information.

    Maximum: 10
    """

    signals = detect_contact_signals(text)

    score = 0

    if signals["email_found"]:
        score += 4

    if signals["phone_found"]:
        score += 4

    if signals["professional_profile_found"]:
        score += 2

    return score, signals


def calculate_readability_score(
    text,
    word_count,
    sections,
    section_word_counts
):
    """
    Evaluate resume readability and text quality.

    Maximum: 15

    The analysis considers:

    1. Sentence length
    2. Text density
    3. Punctuation consistency
    4. Line structure
    5. Section balance
    6. Content sufficiency
    7. Bullet/list consistency

    Readability evaluates how clearly the extracted resume
    text is structured and written. It does not judge the
    candidate's qualifications.
    """

    if not text:
        return 0, {
            "sentence_length": "insufficient content",
            "text_density": "insufficient content",
            "punctuation": "insufficient content",
            "line_structure": "insufficient content",
            "section_balance": "insufficient content",
            "content_sufficiency": "insufficient content",
            "bullet_structure": "insufficient content"
        }

    # ---------------------------------------------------------
    # 1. Sentence length — 3 points
    # ---------------------------------------------------------

    sentences = re.split(
        r"[.!?]+",
        text
    )

    sentence_lengths = []

    for sentence in sentences:

        sentence_words = sentence.split()

        if sentence_words:
            sentence_lengths.append(
                len(sentence_words)
            )

    if sentence_lengths:

        average_sentence_length = (
            sum(sentence_lengths)
            / len(sentence_lengths)
        )

        long_sentence_count = sum(
            1
            for length in sentence_lengths
            if length > 35
        )

        if (
            average_sentence_length <= 22
            and long_sentence_count == 0
        ):
            sentence_score = 3
            sentence_signal = "good"

        elif average_sentence_length <= 30:
            sentence_score = 2
            sentence_signal = "moderate"

        else:
            sentence_score = 1
            sentence_signal = "long"

    else:

        sentence_score = 1
        sentence_signal = "limited sentence data"

    # ---------------------------------------------------------
    # 2. Text density — 2 points
    # ---------------------------------------------------------

    characters = len(text)

    if word_count == 0:

        density_score = 0
        density_signal = "insufficient content"

    else:

        characters_per_word = (
            characters / word_count
        )

        if 4.5 <= characters_per_word <= 7.5:

            density_score = 2
            density_signal = "balanced"

        elif 3.5 <= characters_per_word <= 9:

            density_score = 1
            density_signal = "moderate"

        else:

            density_score = 0
            density_signal = "uneven"

    # ---------------------------------------------------------
    # 3. Punctuation consistency — 2 points
    # ---------------------------------------------------------

    excessive_punctuation = bool(
        re.search(
            r"[!?]{2,}|\.{4,}|,{2,}|;{2,}|:{2,}",
            text
        )
    )

    punctuation_score = 2

    if excessive_punctuation:

        punctuation_score -= 1
        punctuation_signal = "inconsistent"

    else:

        punctuation_signal = "clean"

    # ---------------------------------------------------------
    # 4. Line structure — 2 points
    # ---------------------------------------------------------

    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]

    if not lines:

        line_score = 0
        line_signal = "limited structure"

    else:

        very_long_lines = sum(
            1
            for line in lines
            if len(line) > 180
        )

        average_line_length = (
            sum(len(line) for line in lines)
            / len(lines)
        )

        if (
            len(lines) >= 6
            and very_long_lines == 0
            and average_line_length <= 120
        ):

            line_score = 2
            line_signal = "well structured"

        elif (
            len(lines) >= 4
            and very_long_lines <= 1
        ):

            line_score = 1
            line_signal = "moderately structured"

        else:

            line_score = 0
            line_signal = "limited structure"

    # ---------------------------------------------------------
    # 5. Section balance — 2 points
    # ---------------------------------------------------------

    active_section_counts = [
        count
        for section, count in section_word_counts.items()
        if sections.get(section) and count > 0
    ]

    if len(active_section_counts) >= 4:

        largest = max(active_section_counts)
        smallest = min(active_section_counts)

        if (
            smallest > 0
            and largest / smallest <= 6
        ):

            balance_score = 2
            balance_signal = "balanced"

        elif largest / smallest <= 12:

            balance_score = 1
            balance_signal = "somewhat uneven"

        else:

            balance_score = 0
            balance_signal = "uneven"

    elif len(active_section_counts) >= 2:

        balance_score = 1
        balance_signal = "moderately balanced"

    else:

        balance_score = 0
        balance_signal = "limited section content"

    # ---------------------------------------------------------
    # 6. Content sufficiency — 2 points
    # ---------------------------------------------------------

    if word_count >= 250:

        content_score = 2
        content_signal = "sufficient"

    elif word_count >= 150:

        content_score = 1
        content_signal = "limited"

    else:

        content_score = 0
        content_signal = "insufficient"

    # ---------------------------------------------------------
    # 7. Bullet / list structure — 2 points
    # ---------------------------------------------------------

    bullet_lines = [
        line
        for line in text.splitlines()
        if re.match(
            r"^\s*(?:[-•●▪*]|\d+[.)])\s+",
            line
        )
    ]

    if bullet_lines:

        bullet_count = len(bullet_lines)

        short_bullets = sum(
            1
            for line in bullet_lines
            if len(line.split()) <= 2
        )

        very_long_bullets = sum(
            1
            for line in bullet_lines
            if len(line.split()) > 45
        )

        if (
            bullet_count >= 2
            and short_bullets == 0
            and very_long_bullets == 0
        ):

            bullet_score = 2
            bullet_signal = "well structured"

        else:

            bullet_score = 1
            bullet_signal = "needs improvement"

    else:

        # A resume does not have to use bullets.
        # Therefore, absence of bullets is not automatically
        # treated as a readability failure.
        bullet_score = 1
        bullet_signal = "not detected"

    # ---------------------------------------------------------
    # Base readability score
    # ---------------------------------------------------------

    total_score = (
        sentence_score
        + density_score
        + punctuation_score
        + line_score
        + balance_score
        + content_score
        + bullet_score
    )

    # Maximum possible:
    # 3 + 2 + 2 + 2 + 2 + 2 + 2 = 15

    # ---------------------------------------------------------
    # Content-quality ceiling
    # ---------------------------------------------------------

    # A very short resume can still be cleanly formatted,
    # but it should not receive a near-perfect readability
    # and content-quality score.

    if word_count < 100:

        total_score = min(
            total_score,
            8
        )

    elif word_count < 150:

        total_score = min(
            total_score,
            10
        )

    elif word_count < 200:

        total_score = min(
            total_score,
            12
        )

    total_score = min(
        total_score,
        15
    )

    return total_score, {
        "sentence_length": sentence_signal,
        "text_density": density_signal,
        "punctuation": punctuation_signal,
        "line_structure": line_signal,
        "section_balance": balance_signal,
        "content_sufficiency": content_signal,
        "bullet_structure": bullet_signal
    }


def calculate_resume_score(
    text,
    word_count,
    sections,
    skills,
    knowledge,
    technologies
):
    """
    Calculate the overall ResuMatch resume score.

    Total: 100

    Breakdown:

    Content & length                15
    Resume structure               20
    Skills & knowledge             20
    Experience & projects          20
    Contact & professional profile 10
    Readability & content quality  15
    """

    # ---------------------------------------------------------
    # Section word counts
    # ---------------------------------------------------------

    important_sections = [
        "summary",
        "education",
        "experience",
        "projects",
        "skills",
    ]

    section_word_counts = {
        section: count_section_words(
            text,
            section
        )
        for section in important_sections
    }

    # ---------------------------------------------------------
    # Individual category scores
    # ---------------------------------------------------------

    content_score = (
        calculate_content_length_score(
            word_count
        )
    )

    structure_score = (
        calculate_structure_score(
            sections,
            section_word_counts
        )
    )

    skills_knowledge_score = (
        calculate_skills_knowledge_score(
            skills,
            knowledge,
            technologies
        )
    )

    experience_projects_score = (
        calculate_experience_projects_score(
            sections,
            section_word_counts
        )
    )

    contact_score, contact_signals = (
        calculate_contact_score(text)
    )

    readability_score, readability_signals = (
        calculate_readability_score(
            text,
            word_count,
            sections,
            section_word_counts
        )
    )

    # ---------------------------------------------------------
    # Overall score
    # ---------------------------------------------------------

    total_score = (
        content_score
        + structure_score
        + skills_knowledge_score
        + experience_projects_score
        + contact_score
        + readability_score
    )

    total_score = min(
        round(total_score),
        100
    )

    # ---------------------------------------------------------
    # User-facing breakdown
    # ---------------------------------------------------------

    breakdown = [
        {
            "category": "Content & length",
            "score": content_score,
            "max_score": 15,
            "description": (
                "Measures whether the resume contains "
                "a reasonable amount of relevant content "
                "without rewarding unnecessary length."
            ),
        },

        {
            "category": "Resume structure",
            "score": structure_score,
            "max_score": 20,
            "description": (
                "Measures the presence and substance "
                "of important resume sections."
            ),
        },

        {
            "category": "Skills & knowledge",
            "score": skills_knowledge_score,
            "max_score": 20,
            "description": (
                "Measures the breadth of recognized "
                "skills, knowledge areas, and technical concepts."
            ),
        },

        {
            "category": "Experience & projects",
            "score": experience_projects_score,
            "max_score": 20,
            "description": (
                "Measures whether experience and project "
                "sections contain meaningful supporting detail."
            ),
        },

        {
            "category": "Contact & professional profile",
            "score": contact_score,
            "max_score": 10,
            "description": (
                "Checks for professional contact information "
                "and useful profile links."
            ),
        },

        {
            "category": "Readability & content quality",
            "score": readability_score,
            "max_score": 15,
            "description": (
                "Measures sentence length, text density, "
                "punctuation, line structure, section balance, "
                "content sufficiency, and bullet structure."
            ),
        },
    ]

    # ---------------------------------------------------------
    # Final result
    # ---------------------------------------------------------

    return {
        "total_score": total_score,
        "max_score": 100,
        "breakdown": breakdown,
        "signals": {
            "contact": contact_signals,
            "section_word_counts": section_word_counts,
            "readability": readability_signals,
        },
    }