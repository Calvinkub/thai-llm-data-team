"""Spam and adult-content filter for Thai Foundation LLM preprocessing.

Detects gambling, lottery, adult, and other spam content in Thai/English text.
All blocked terms are stored in plain form internally but displayed censored
in logs/reports so this file is safe for public GitHub.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from urllib.parse import urlparse


# ---------------------------------------------------------------------------
# Blocked domain list  (displayed censored in logs)
# ---------------------------------------------------------------------------

# Format: (blocked_domain, censored_display)
_BLOCKED_DOMAINS: list[tuple[str, str]] = [
    # Adult sites
    ("pornhub.com",       "prxxxhub.com"),
    ("xvideos.com",       "xvixxxos.com"),
    ("xhamster.com",      "xhxxxster.com"),
    ("xnxx.com",          "xnxx.com"),          # already ambiguous enough
    ("redtube.com",       "rxxxube.com"),
    ("youporn.com",       "youxxxn.com"),
    ("sex.com",           "sxx.com"),
    ("livejasmin.com",    "livejxxxin.com"),
    ("chaturbate.com",    "chaxxxate.com"),
    ("onlyfans.com",      "onlyfxxx.com"),
    # Thai gambling / illegal betting
    ("gclub.com",         "gcxxx.com"),
    ("baccarat.in.th",    "bxxxarat.in.th"),
    ("betflix.co",        "bxtflix.co"),
    ("ufa.bet",           "uxxa.bet"),
    ("sagame.com",        "saxame.com"),
    ("vegus168.com",      "vexxx168.com"),
]

# Build fast lookup sets
_BLOCKED_DOMAIN_SET: set[str] = {d for d, _ in _BLOCKED_DOMAINS}
_DOMAIN_CENSOR_MAP: dict[str, str] = {d: c for d, c in _BLOCKED_DOMAINS}


# ---------------------------------------------------------------------------
# Thai keyword lists (displayed censored in logs via _censor_keyword)
# ---------------------------------------------------------------------------

# Thai gambling / spam keywords
_THAI_SPAM_KEYWORDS: list[str] = [
    "บาคาร่า",
    "บาคาร่าออนไลน์",
    "หวยออนไลน์",
    "หวยลาว",
    "หวยฮานอย",
    "แทงบอล",
    "แทงบอลออนไลน์",
    "พนันออนไลน์",
    "คาสิโนออนไลน์",
    "สล็อตออนไลน์",
    "สล็อตแตกง่าย",
    "โจ๊กเกอร์สล็อต",
    "เว็บพนัน",
    "โปรโมชั่นสล็อต",
    "ทดลองเล่นสล็อต",
    "สมัครสล็อต",
    "ฝากถอนไม่มีขั้นต่ำ",
    "รับโบนัส",
    "แจกเครดิตฟรี",
    "กดรับโบนัส",
    "แนะนำเพื่อนรับเงิน",
]

# English gambling / spam keywords (Thai context)
_EN_SPAM_KEYWORDS: list[str] = [
    "baccarat",
    "online casino",
    "online gambling",
    "slot online",
    "sports betting",
    "live casino",
    "free credit",
    "no deposit bonus",
    "seo spam",
]

# Combined set for fast membership check (lowercased for matching)
_ALL_SPAM_LOWER: set[str] = {k.lower() for k in _THAI_SPAM_KEYWORDS + _EN_SPAM_KEYWORDS}


def _censor_keyword(word: str) -> str:
    """Replace middle characters with 'x' for public display."""
    if len(word) <= 2:
        return word[0] + "x"
    mid = len(word) // 2
    return word[:1] + "x" * (len(word) - 2) + word[-1:]


# ---------------------------------------------------------------------------
# Compiled regex patterns
# ---------------------------------------------------------------------------

# Matches any spam keyword as a substring (case-insensitive, Unicode)
_SPAM_PATTERN: re.Pattern = re.compile(
    "|".join(re.escape(k) for k in _THAI_SPAM_KEYWORDS + _EN_SPAM_KEYWORDS),
    re.IGNORECASE | re.UNICODE,
)

# URL pattern to extract domains from text
_URL_PATTERN: re.Pattern = re.compile(
    r"https?://[^\s\"'<>]+",
    re.IGNORECASE,
)


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class SpamResult:
    is_spam: bool
    reasons: list[str] = field(default_factory=list)
    censored_matches: list[str] = field(default_factory=list)  # safe for logs


# ---------------------------------------------------------------------------
# Core filter functions
# ---------------------------------------------------------------------------

def _extract_domains(text: str) -> list[str]:
    """Extract hostnames from all URLs found in text."""
    domains = []
    for url in _URL_PATTERN.findall(text):
        try:
            host = urlparse(url).netloc.lower().lstrip("www.")
            if host:
                domains.append(host)
        except Exception:
            continue
    return domains


def check_spam(text: str, url: str = "") -> SpamResult:
    """Check a document for spam/adult content.

    Args:
        text: Document text content.
        url:  Source URL of the document (optional, checked separately).

    Returns:
        SpamResult with is_spam flag, reasons, and censored match list for logs.
    """
    reasons: list[str] = []
    censored: list[str] = []

    # 1. Check source URL domain
    if url:
        try:
            source_domain = urlparse(url).netloc.lower().lstrip("www.")
            if source_domain in _BLOCKED_DOMAIN_SET:
                display = _DOMAIN_CENSOR_MAP.get(source_domain, _censor_keyword(source_domain))
                reasons.append("blocked_source_domain")
                censored.append(f"domain:{display}")
        except Exception:
            pass

    # 2. Check domains mentioned inside the text
    for domain in _extract_domains(text):
        if domain in _BLOCKED_DOMAIN_SET:
            display = _DOMAIN_CENSOR_MAP.get(domain, _censor_keyword(domain))
            reasons.append("blocked_domain_in_text")
            censored.append(f"domain:{display}")
            break  # one is enough to flag

    # 3. Check for spam keyword matches
    matches = _SPAM_PATTERN.findall(text)
    if matches:
        # Deduplicate and censor for display
        seen: set[str] = set()
        for m in matches:
            key = m.lower()
            if key not in seen:
                seen.add(key)
                censored.append(f"kw:{_censor_keyword(m)}")
        # Flag as spam only if keyword density is high enough
        keyword_density = len(matches) / max(len(text.split()), 1)
        if keyword_density >= 0.05 or len(seen) >= 3:
            reasons.append("spam_keywords")

    return SpamResult(
        is_spam=len(reasons) > 0,
        reasons=reasons,
        censored_matches=censored[:10],  # cap at 10 for log brevity
    )


def is_spam(text: str, url: str = "") -> bool:
    """Convenience wrapper returning just the boolean flag."""
    return check_spam(text, url).is_spam


# ---------------------------------------------------------------------------
# Batch helper for the preprocessing pipeline
# ---------------------------------------------------------------------------

def filter_batch(
    docs: list[dict],
    text_field: str = "text",
    url_field: str = "url",
    flag_field: str = "quality_flags",
) -> tuple[list[dict], list[dict]]:
    """Split a list of schema docs into (clean, spam) lists.

    Spam docs are NOT dropped silently; they are returned separately so
    pipeline code can log them. Each spam doc gets 'spam_filter' appended
    to its quality_flags list.
    """
    clean: list[dict] = []
    spam: list[dict] = []

    for doc in docs:
        text = doc.get(text_field, "")
        url = doc.get(url_field, "")
        result = check_spam(text, url)
        if result.is_spam:
            doc = dict(doc)
            flags = list(doc.get(flag_field, []))
            flags.append("spam_filter")
            doc[flag_field] = flags
            doc["_spam_reasons"] = result.reasons
            doc["_spam_matches"] = result.censored_matches  # already censored
            spam.append(doc)
        else:
            clean.append(doc)

    return clean, spam
