"""Offline Spectrum preview. Never imports storage, Gmail, Groq, or startup."""

import argparse
from spectrum_campaign import render_spectrum_email


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--step", type=int, choices=range(1, 9))
    parser.add_argument("--name", default="Alex")
    parser.add_argument("--organization", default="Example Care Facility")
    args = parser.parse_args()
    prospect = {"contact_name": args.name, "organization": args.organization, "email": "preview@example.invalid"}
    for step in ([args.step] if args.step else range(1, 9)):
        draft = render_spectrum_email(prospect, step)
        print(f"Step {step} of 8\nSubject: {draft['subject']}\n\n{draft['body']}\n")


if __name__ == "__main__":
    main()
