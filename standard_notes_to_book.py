#!/usr/bin/env python3

import json
import subprocess
from collections import defaultdict
from pathlib import Path

BACKUP_FILE = "Standard Notes Backup and Import File.txt"

OUTPUT_MD = "standard_notes_archive.md"
OUTPUT_PDF = "standard_notes_archive.pdf"

print("Loading backup...")

with open(BACKUP_FILE, "r", encoding="utf-8") as f:
    data = json.load(f)

items = data["items"]

notes = []
tags_by_note = defaultdict(list)

print("Processing tags...")

for item in items:
    if item.get("content_type") != "Tag":
        continue

    tag_name = item["content"].get("title", "Untitled Tag")

    for ref in item["content"].get("references", []):
        if ref.get("content_type") == "Note":
            tags_by_note[ref["uuid"]].append(tag_name)

print("Processing notes...")

for item in items:
    if item.get("content_type") != "Note":
        continue

    content = item.get("content", {})

    notes.append({
        "uuid": item.get("uuid"),
        "title": content.get("title", "Untitled"),
        "text": content.get("text", ""),
        "created_at": item.get("created_at", ""),
        "updated_at": item.get("updated_at", ""),
        "tags": sorted(tags_by_note.get(item.get("uuid"), []))
    })

notes.sort(key=lambda n: n["created_at"])

print(f"Found {len(notes)} notes")

with open(OUTPUT_MD, "w", encoding="utf-8") as out:

    out.write("# Standard Notes Archive\n\n")

    out.write(
        f"Generated from {len(notes)} notes.\n\n"
    )

    out.write("\\newpage\n\n")

    for note in notes:

        title = note["title"].strip()

        if not title:
            title = "Untitled"

        out.write(f"# {title}\n\n")

        out.write(
            f"**Created:** {note['created_at']}  \n"
        )

        out.write(
            f"**Modified:** {note['updated_at']}  \n"
        )

        if note["tags"]:
            out.write(
                f"**Tags:** {', '.join(note['tags'])}\n\n"
            )
        else:
            out.write(
                "**Tags:** None\n\n"
            )

        text = note["text"]

        if text.strip():
            out.write("```text\n")
            out.write(text)
            out.write("\n```\n\n")
            out.write("\n\n")
        else:
            out.write("*Empty note*\n\n")

        out.write("\\newpage\n\n")

print("Generating DOCX...")

subprocess.run([
    "pandoc",
    OUTPUT_MD,
    "-o",
    "standard_notes_archive.docx",
    "--toc"
], check=True)

print("Done: standard_notes_archive.docx")
