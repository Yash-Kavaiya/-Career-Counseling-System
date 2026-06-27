"""Compact text rendering of a CandidateProfile for agent prompts.

Shared by discovery, assessment, job-match, interview and roadmap agents so they
all reason from the same grounded summary.
"""
from __future__ import annotations

from ..schemas.profile import CandidateProfile


def profile_summary(p: CandidateProfile) -> str:
    lines: list[str] = []
    header = " | ".join(
        x
        for x in [
            p.name,
            p.headline,
            f"{p.total_experience_years}y total" if p.total_experience_years else None,
            p.location,
        ]
        if x
    )
    if header:
        lines.append(header)
    if p.summary:
        lines.append(f"Summary: {p.summary}")

    if p.experiences:
        lines.append("Experience:")
        for e in p.experiences:
            head = f"- {e.role} at {e.company}"
            if e.client:
                head += f" (client: {e.client})"
            dates = "-".join(x for x in [e.start, e.end] if x)
            if dates:
                head += f", {dates}"
            if e.is_current:
                head += " [current]"
            lines.append(head)
            if e.tech:
                lines.append(f"    tech: {', '.join(e.tech)}")
            if e.achievements:
                ach = "; ".join(
                    a.description + (f" ({a.metric})" if a.metric else "")
                    for a in e.achievements
                )
                lines.append(f"    achievements: {ach}")

    if p.skills:
        lines.append(
            "Skills: "
            + ", ".join(
                s.name + (f" ({s.proficiency})" if s.proficiency else "") for s in p.skills
            )
        )
    if p.projects:
        lines.append(
            "Projects: "
            + "; ".join(
                pr.name + (f" [{', '.join(pr.tech)}]" if pr.tech else "") for pr in p.projects
            )
        )
    if p.education:
        lines.append(
            "Education: "
            + "; ".join(
                ", ".join(x for x in [ed.degree, ed.institution, ed.year, ed.score] if x)
                for ed in p.education
            )
        )
    if p.certifications:
        lines.append(
            "Certifications: "
            + ", ".join(
                c.name + (f" ({c.status})" if c.status else "") for c in p.certifications
            )
        )

    pref = p.preferences
    prefs = []
    if pref.notice_period:
        prefs.append(f"notice {pref.notice_period}")
    if pref.current_ctc:
        prefs.append(f"current CTC {pref.current_ctc}")
    if pref.expected_ctc:
        prefs.append(f"expected CTC {pref.expected_ctc}")
    if pref.locations:
        prefs.append("locations: " + ", ".join(pref.locations))
    if pref.remote_preference:
        prefs.append(f"remote: {pref.remote_preference}")
    if pref.company_types:
        prefs.append("company types: " + ", ".join(pref.company_types))
    if pref.target_roles:
        prefs.append("target roles: " + ", ".join(pref.target_roles))
    if pref.priorities:
        prefs.append("priorities: " + ", ".join(pref.priorities))
    if prefs:
        lines.append("Preferences: " + "; ".join(prefs))

    if p.career_gaps:
        gaps = []
        for g in p.career_gaps:
            parts = [g.dates, f"({g.reason})" if g.reason else None]
            if g.activities:
                parts.append(f"[did: {g.activities}]")
            gaps.append(" ".join(x for x in parts if x))
        lines.append("Career gaps: " + "; ".join(g for g in gaps if g))

    return "\n".join(lines)
