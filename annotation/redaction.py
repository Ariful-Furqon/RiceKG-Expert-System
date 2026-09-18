"""
Redaction of disease and pathogen names from case texts shown to annotators.

Annotators must diagnose from the described signs, so every string that names a disease, a
causal organism or a disease abbreviation is replaced by REDACTED. Signs, vectors and the host
are kept: "smut ball" becomes "[disamarkan] ball", "green leafhopper" stays.

The patterns are deliberately broad; a coordinator still reviews every redacted text (the packet
builder writes a redaction report for this) before the packet is sent.
"""

import re

REDACTED = "[disamarkan]"

# Longest, most specific patterns first.
PATTERNS = [
    # Viruses, phytoplasmas and their abbreviations
    r"southern (rice )?black[- ]streaked dwarf virus", r"rice ragged stunt virus", r"rice grassy stunt( virus| tenuivirus)?",
    r"rice tungro (bacilliform|spherical) virus(es)?", r"rice tungro( disease| virus(es)?)?", r"tungro[- ]?like", r"tungro( viruses| virus| disease)?",
    r"rice yellow mottle( virus)?", r"rice yellow stunt", r"rice orange leaf phytoplasma", r"orange leaf phytoplasma", r"phytoplasma",
    r"grassy stunt", r"stunt disease",
    r"\bRGSV\d?\b", r"\bRTBV\b", r"\bRTSV\b", r"\bRTD\b", r"\bRYMV\b", r"\bRRSV\b", r"\bSRBSDV\b", r"\bROLP\b", r"\bRYS\b",
    # Bacterial and fungal diseases
    r"bacterial (leaf )?blight", r"bacterial leaf streak", r"bacterial panicle blight", r"panicle blight", r"sheath blight",
    r"sheath rot", r"stem rot", r"leaf streak", r"\bBLB\b", r"\bBLS\b", r"\bBPB\b", r"\bBB\b", r"\bRFS\b", r"\bkresek\b",
    r"(rice |leaf |neck |panicle |node )?blast", r"\bblas\b", r"false smut", r"smut",
    r"root[- ]knot nematodes?", r"root[- ]galls?", r"cyst nematodes?", r"white tip", r"nematodes?",
    # Organisms (genus, binomial, abbreviated binomial, pathovar)
    r"(Pyricularia|Magnaporthe|Xanthomonas|Ustilaginoidea|Villosiclava|Meloidogyne|Hirschmanniella|Heterodera|"
    r"Aphelenchoides|Sarocladium|Burkholderia|Pantoea|Rhizoctonia|Cochliobolus|Bipolaris|Fusarium)( [a-z]+)?( pv\. [a-z]+)?( Cav\.)?",
    r"\b[PMXU]\. (oryzae|grisea|graminicola|virens)( pv\. [a-z]+)?", r"\bpv\. oryz(ae|icola)",
]
_RX = [re.compile(p, re.IGNORECASE) for p in PATTERNS]


def redact(text):
    """Return (redacted text, list of removed strings)."""
    removed = []
    for rx in _RX:
        def _sub(m):
            removed.append(m.group(0))
            return REDACTED
        text = rx.sub(_sub, text)
    # Collapse runs such as "[disamarkan] [disamarkan]" or "[disamarkan] ([disamarkan])".
    text = re.sub(r"\[disamarkan\](\W{0,3}\[disamarkan\]\)?)+", REDACTED, text)
    return text, removed
