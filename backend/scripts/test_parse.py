"""Directly exercise the parser agent on the messy "Arjun" resume.

Run from backend/:  uv run python -m scripts.test_parse
"""
from __future__ import annotations

import asyncio

from app.agents.parser_agent import parse_resume
from app.agents.runtime import configure_groq
from app.services.document import extract_resume

ARJUN = """ARJUN KUMAR
SDE | 3.8+ years exp | Bangalore
+91-9876543210 | arjunkumar.dev@gmail.com
linkedin.com/in/arjunkumar | github.com/arjun-k

"Looking for SDE role in product company or good startup. Good WLB important. Currently serving notice - 60 days. Expected CTC 22 LPA"

EXPERIENCE
Infosys (Client: Major Retail Bank) - Systems Engineer (Full Stack)
Jan 2023 - Present
- Developed microservices in Spring Boot for transaction module (handled ~10k req/day)
- Angular frontend + REST integration
- Query optimization -> 40% latency reduction
- Mentored 2 junior developers

TCS - Java Developer (Insurance Domain)
2021 - 2022 (approx)
Bug fixes, small enhancements on Java 8 + Oracle. No major metrics.

[6-month break Mar-Aug 2022 - family health reasons / personal]

PROJECTS
E-commerce Platform (Personal)
MERN stack, JWT auth, Razorpay integration, deployed Vercel + Railway. 45 GitHub stars.

College: Smart Attendance using OpenCV face recognition (basic)

SKILLS
Java, Spring Boot, Angular, Node.js (some), Python (basic), MySQL, MongoDB, Redis, AWS (EC2/S3/Lambda basic), Docker, Git, Jira
Soft skills: Good communication, team player, problem solving

EDUCATION
B.Tech CS, VTU | 2017-2021 | 7.2 CGPA

CERTS
Oracle Java SE 8, Google Cloud Associate (in progress)
"""


async def main() -> None:
    if not configure_groq():
        raise SystemExit("GROQ_API_KEY not set in backend/.env")
    content = extract_resume("arjun.txt", ARJUN.encode())
    profile = await parse_resume(content)
    print(profile.model_dump_json(indent=2))
    print("\n--- SUMMARY ---")
    print("name:", profile.name, "| exp:", profile.total_experience_years)
    print("experiences:", len(profile.experiences), "| skills:", len(profile.skills))
    print("notice:", profile.preferences.notice_period, "| expected CTC:", profile.preferences.expected_ctc)
    print("gaps:", profile.career_gaps)
    print("uncertainty flags:", len(profile.uncertainty_flags))
    for f in profile.uncertainty_flags:
        print(f"  - [{f.confidence}] {f.field}: {f.reason}")


if __name__ == "__main__":
    asyncio.run(main())
