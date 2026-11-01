import html
import re
import unicodedata

# These sections usually occur at the end of an article and are not prose.
BACK_MATTER = {
    "references", "reference", "sources", "source", "external links",
    "other websites", "further reading", "bibliography", "related pages",
    "see also", "notes", "footnotes", "citations",
}

# Confirmed plain-text headings from the sample articles. Add new entries
# only after inspecting them in the original dataset.
BODY_HEADINGS = {
    "the month", "april in poetry", "events in april", "fixed events",
    "moveable events", "selection of historical events", "trivia",
    "types of art", "plastic art", "performing art", "practical art",
    'what "art" means', "history of art", "roles of art", "functions of art",
    "early life and family", "education", "career", "private life",
    "death", "history", "release history", "where it came from",
    "using the letter", "use in mathematics", "about her life",
}

WIKI_HEADING = re.compile(r"^={2,6}\s*(.+?)\s*={2,6}$")
MARKDOWN_HEADING = re.compile(r"^#{1,6}\s+(.+)$")
CITATION = re.compile(r"\[(?:\d+(?:\s*[,;–-]\s*\d+)*|citation needed|source needed)\]", re.I)
WIKI_LINK = re.compile(r"\[\[([^\[\]]+)\]\]")
STANDALONE_URL = re.compile(r"https?://\S+", re.I)
LEFTOVER_MARKUP = re.compile(r"\[\[|\]\]|\{\{|\}\}|<ref\b", re.I)
REF_TAG = re.compile(
    r"<ref\b[^>]*>.*?</ref\s*>|<ref\b[^>]*/\s*>",
    re.I | re.S
)

MONTH_NUMBERS = {
    "january": "01",
    "february": "02",
    "march": "03",
    "april": "04",
    "may": "05",
    "june": "06",
    "july": "07",
    "august": "08",
    "september": "09",
    "october": "10",
    "november": "11",
    "december": "12",
}

def _heading_name(line):
    """Return a recognized heading label, or None for ordinary article text."""
    line = line.strip()
    wiki = WIKI_HEADING.fullmatch(line)
    markdown = MARKDOWN_HEADING.fullmatch(line)
    if wiki or markdown:
        return (wiki or markdown).group(1).strip().casefold()

    # We do NOT guess from capitalization or length: lists can look like headings.
    label = line.rstrip(":").strip().casefold()
    if label in BODY_HEADINGS or label in BACK_MATTER:
        return label
    return None


def _visible_link(match):
    """[[page|display]] -> display; [[page]] -> page."""
    raw = match.group(1)
    return raw.split("|")[-1].split("#")[0]


def clean_article(raw_text, title=""):
    """Return (cleaned_text, report) without modifying the original article."""
    original = unicodedata.normalize("NFC", str(raw_text or ""))
    original = original.replace("\r\n", "\n").replace("\r", "\n")
    kept = []
    removed_headings = []
    stopped_at = None
    skipping_back_matter = False

    for raw_line in REF_TAG.sub("", original).splitlines():
        line = html.unescape(raw_line).replace("\u00a0", " ").replace("\u200b", "")
        heading = _heading_name(line)

        # Start skipping references and other back-matter sections
        if heading in BACK_MATTER:
            if stopped_at is None:
                stopped_at = heading
            skipping_back_matter = True
            continue

        # Resume cleaning when a recognized body section begins
        if skipping_back_matter:
            if heading in BODY_HEADINGS:
                skipping_back_matter = False
                removed_headings.append(heading)
            continue

        # Remove headings but preserve the following text
        if heading is not None:
            removed_headings.append(heading)
            continue

        # Clean citations and Wikipedia links
        line = CITATION.sub("", line)
        line = WIKI_LINK.sub(_visible_link, line)
        line = re.sub(r"[ \t]+", " ", line).strip()

        if STANDALONE_URL.fullmatch(line):
            continue

        # Preserve normal text and paragraph boundaries
        if line:
            kept.append(line)
        elif kept and kept[-1] != "":
            kept.append("")

    # Remove an exact duplicate title only when it appears at the start.
    if title:
        first_nonempty = next((i for i, line in enumerate(kept) if line), None)
        if first_nonempty is not None and kept[first_nonempty].casefold() == title.strip().casefold():
            kept.pop(first_nonempty)
        # Remove trailing month-number metadata only
        # when it matches the article's month.
        month_number = MONTH_NUMBERS.get(title.strip().casefold())

        if month_number:
            while kept and kept[-1] == "":
                kept.pop()

            if kept and kept[-1] == month_number:
                kept.pop()
    cleaned = re.sub(r"\n{3,}", "\n\n", "\n".join(kept)).strip()
    original_chars = len(original)
    report = {
        "original_chars": original_chars,
        "cleaned_chars": len(cleaned),
        "removed_pct": round(100 * (original_chars - len(cleaned)) / original_chars, 2)
        if original_chars else 0.0,
        "word_count": len(cleaned.split()),
        "removed_headings": removed_headings,
        "stopped_at_back_matter": stopped_at,
    }
    return cleaned, report


def validate_article(cleaned, report):
    """Return flags for human review. Never auto-delete flagged articles."""
    flags = []

    if not cleaned:
        flags.append("empty_after_cleaning")
    elif report["word_count"] < 25:
        flags.append("very_short")

    if report["original_chars"] >= 200 and report["removed_pct"] > 40:
        flags.append("large_text_removal")

    if LEFTOVER_MARKUP.search(cleaned):
        flags.append("leftover_wiki_markup")

    # Flag trailing numeric metadata
    if cleaned and re.fullmatch(r"\d{1,3}", cleaned.splitlines()[-1].strip()):
        flags.append("possible_trailing_metadata")

    # Flag possible trailing Wikipedia categories
    lines = cleaned.splitlines()

    if len(lines) >= 2:
        last_line = lines[-1].strip()

        previous_text = next(
            (line.strip() for line in reversed(lines[:-1])
             if line.strip()),
            ""
        )

        blank_before = not lines[-2].strip()

        previous_ends_sentence = previous_text.endswith(
            (".", "!", "?")
        )

        category_like = re.fullmatch(
            r"[A-Z][A-Za-z]*(?:[ -][A-Za-z]+){0,3}",
            last_line
        )

        if category_like and (
                blank_before or previous_ends_sentence
        ):
            flags.append("possible_trailing_category")

    # Flag potentially damaged text
    if re.search(r"\(\s*\)", cleaned):
        flags.append("empty_parentheses")

    return flags
