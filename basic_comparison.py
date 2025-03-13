import json
import base64
import re

from typing import Any
from os import path
from pprint import pprint
from anthropic import Anthropic

from constants import ANTHROPIC_API_KEY, MODEL_VER, PROMPT_TEMPLATE


def get_pdf_data(pdf_path=None, pdf_url=None):
    """
    Get the PDF data of the given PDF in file or URL form

    Args:
        pdf_path (str): The full of the desired PDF to open.
        pdf_url (str): The URL of the desired PDF to open.

    Returns:
        byte object: Encoded binary data to a base64-encoded bytes object.
    """
    with open(pdf_path, "rb") as pdf_file:
        return base64.standard_b64encode(pdf_file.read()).decode("utf-8")

    # TODO - implement URL functionality


def get_course_req(target_course=None):
    """
    Get a dict of all course requirements or pass in a specific course arg for
    a specific course's requirements.

    Args:
        target_course (str): Optional to return the requirements of a specific course.
        Returns all courses requirements if left empty.

    Returns:
        dict: Returns all or a specific course content from course_reqs.json
    """
    course_req = None
    base_path = path.dirname(__file__)
    course_req_path = base_path + "/course_reqs.json"

    try:
        with open(course_req_path, "r") as file:
            course_req = json.load(file)
    except FileNotFoundError:
        print(f"Error: File not found'")

    if target_course:
        course_req = course_req[target_course]
    return course_req


def parse_textblock(textblock: Any) -> str:
    """
    Convert a TextBlock response into a human-readable format.

    Args:
        textblock (Any): The TextBlock object containing text.

    Returns:
        str: A formatted, human-readable string.
    """
    # Extract the text from the TextBlock
    raw_text = textblock.text if hasattr(textblock, "text") else str(textblock)

    # Define formatting rules
    topic_pattern = (
        r"Topic Name: (.*?)\nPresence: (.*?)\nContext: (.*?)(?=\nTopic Name:|$)"
    )
    matches = re.findall(topic_pattern, raw_text, re.DOTALL)

    formatted_output = []
    formatted_output.append("Analysis of Requested Topics:\n")

    for topic, presence, context in matches:
        formatted_output.append(f"\n📌 **{topic}** (Present: {presence})")
        formatted_output.append(f"    Context: {context.strip()}\n")

    return "\n".join(formatted_output).strip()


def compile_messages(prompt=None, pdf_data=None):
    messages = [
        {
            "role": "user",
            "content": [
                {
                    "type": "document",
                    "source": {
                        "type": "base64",
                        "media_type": "application/pdf",
                        "data": pdf_data,
                    },
                },
                {"type": "text", "text": prompt},
            ],
        }
    ]

    return messages


def send_claude_message(client, input_messages=None):
    # Send to Claude using base64 encoding
    message = client.messages.create(
        model=MODEL_VER,
        max_tokens=1024,
        messages=input_messages,
    )
    return message


def get_template_formatted(course_req_data=None):
    return PROMPT_TEMPLATE.format(course_req_data["key_topics"])


def claude_token_counter_response(client, pdf_data):
    response = client.messages.count_tokens(
        model=MODEL_VER,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "document",
                        "source": {
                            "type": "base64",
                            "media_type": "application/pdf",
                            "data": pdf_data,
                        },
                    },
                    {"type": "text", "text": "Please summarize this document."},
                ],
            }
        ],
    )
    return response


def main():
    # Get required local information
    pdf_data = get_pdf_data(pdf_path="document.pdf")
    CS111_course_req_data = get_course_req(target_course="CS111")

    # Pre-reqs to send Anthropic outbound message
    messages = compile_messages(
        prompt=get_template_formatted(CS111_course_req_data), pdf_data=pdf_data
    )
    # pprint(messages)
    client = Anthropic(api_key=ANTHROPIC_API_KEY)
    # pprint(claude_token_counter_response(client, pdf_data))

    # Send outbound message to Anthropic client
    res = send_claude_message(client=client, input_messages=messages)
    pprint(res)

    # Format message reply
    formatted_output = parse_textblock(res.content[0])
    pprint(formatted_output)


if __name__ == "__main__":
    main()
