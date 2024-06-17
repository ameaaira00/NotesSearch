"""
This script processes Markdown files in a specified directory, extracting sections and optionally formatting code blocks,
then stores the extracted data into a JSON file.
"""

import os
import glob
import re
import json


def preprocess_notes(notes_directory):
    """
    Extracts sections from Markdown files in the specified directory.
    Each section is processed to handle code blocks and then stored in a JSON format.

    Args:
        notes_directory (str): Directory path containing Markdown files.

    Returns:
        None
    """
    notes = []

    # List all Markdown files in the directory
    md_files = glob.glob(os.path.join(notes_directory, "*.md"))

    for file_path in md_files:
        with open(file_path, "r", encoding="utf-8") as file:
            content = file.read()

            # Split content by ## for sections
            sections = re.split(r"(?<=\n)##\s", content)

            # Remove leading whitespace from the first section if any
            if sections and sections[0].strip() == "":
                sections = sections[1:]

            # Process each section
            for section in sections:
                # Check if the section contains a code block (``` ... ```)
                if "```" in section:
                    # Split the section into non-code and code parts
                    parts = re.split(r"(```[^`]+```)", section)
                    processed_section = ""
                    for part in parts:
                        if part.startswith("```"):
                            processed_section += (
                                f"<pre><code>{part.strip('`')}</code></pre>"
                            )
                        else:
                            processed_section += part
                else:
                    processed_section = section.strip()

                # Store sections along with file information
                file_name = os.path.basename(file_path)
                notes.append({"file": file_name, "section": processed_section.strip()})

    # Write processed notes to a JSON file
    with open("processed_notes.json", "w", encoding="utf-8") as output_file:
        json.dump(notes, output_file, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    notes_directory = "./Notes"
    preprocess_notes(notes_directory)
