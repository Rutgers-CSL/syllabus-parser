import json
import base64
import re

from typing import Any
from os import path
from pprint import pprint
from anthropic import Anthropic

from constants import ANTHROPIC_API_KEY, MODEL_VER

# Simple template that creates a personalized learning message using variables
prompt_template = """Analyze the provided PDF text and identify which topics are present: {}. The topics may be referenced directly or through related concepts. For each topic, provide:
    Topic Name: [Name]
    Presence: [Yes/No]
    Context: [Brief description if present]"""

# Initialize Anthropic client
client = Anthropic(api_key=ANTHROPIC_API_KEY)

# Open relevant PDF
with open("document.pdf", "rb") as pdf_file:
    pdf_data = base64.standard_b64encode(pdf_file.read()).decode("utf-8")

# Get the course keyword requirements
course_req = None
base_path = path.dirname(__file__)
course_req_path = base_path + '/course_reqs.json'

try:
    with open(course_req_path, 'r') as file:
        course_req = json.load(file)

except FileNotFoundError:
        print(f"Error: File not found'")

# Populate prompt template with keywords
prompt_final = prompt_template.format(course_req["CS111"]["key_topics"])


def parse_textblock(textblock: Any) -> str:
    """
    Convert a TextBlock response into a human-readable format.

    Args:
        textblock (Any): The TextBlock object containing text.

    Returns:
        str: A formatted, human-readable string.
    """
    # Extract the text from the TextBlock
    raw_text = textblock.text if hasattr(textblock, 'text') else str(textblock)

    # Define formatting rules
    topic_pattern = r"Topic Name: (.*?)\nPresence: (.*?)\nContext: (.*?)(?=\nTopic Name:|$)"
    matches = re.findall(topic_pattern, raw_text, re.DOTALL)

    formatted_output = []
    formatted_output.append("Analysis of Requested Topics:\n")

    for topic, presence, context in matches:
        formatted_output.append(f"\n📌 **{topic}** (Present: {presence})")
        formatted_output.append(f"    Context: {context.strip()}\n")

    return '\n'.join(formatted_output).strip()


# Send to Claude using base64 encoding
message = client.messages.create(
    model=MODEL_VER,
    max_tokens=4000,
    messages=[
        {
            "role": "user",
            "content": [
                {
                    "type": "document",
                    "source": {
                        "type": "base64",
                        "media_type": "application/pdf",
                        "data": pdf_data
                    }
                },
                {
                    "type": "text",
                    "text": prompt_final
                }
            ]
        }
    ],
)


formatted_output = parse_textblock(message.content[0])
pprint(formatted_output)
