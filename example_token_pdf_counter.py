import base64
import anthropic

from constants import ANTHROPIC_API_KEY, MODEL_VER

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

with open("document.pdf", "rb") as pdf_file:
    pdf_base64 = base64.standard_b64encode(pdf_file.read()).decode("utf-8")

response = client.messages.count_tokens(
    model=MODEL_VER,
    messages=[{
        "role": "user",
        "content": [
            {
                "type": "document",
                "source": {
                    "type": "base64",
                    "media_type": "application/pdf",
                    "data": pdf_base64
                }
            },
            {
                "type": "text",
                "text": "Please summarize this document."
            }
        ]
    }]
)

# PASSING PDF AS A URL 
  #  messages=[
  #          {
  #              "role": "user",
  #              "content": [
  #                  {
  #                      "type": "document",
  #                      "source": {
  #                          "type": "url",
  #                          "url": "https://assets.anthropic.com/m/1cd9d098ac3e6467/original/Claude-3-Model-Card-October-Addendum.pdf"
  #                      }
  #                  },
  #                  {
  #                      "type": "text",
  #                      "text": "What are the key findings in this document?"
  #                  }
  #              ]
  #          }
  #      ],

print(response.json())

