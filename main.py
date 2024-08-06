import json
import os
import re

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
JSON_REGEX = re.compile(r"```json(.*)```", re.DOTALL)

# Get the pdf filenames
pdf_files = []
file_streams = []
for root, dirs, files in os.walk(".data/leads"):
    for file in files:
        if file.endswith(".pdf"):
            pdf_files.append(os.path.join(root, file))
            file_streams.append(open(os.path.join(root, file), "rb"))

# Create the assistant
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
assistant = client.beta.assistants.create(
    name="Lead Parser",
    description="Parse leads from PDF files",
    model="gpt-3.5-turbo",
    tools=[{"type": "file_search"}],
)

# Ask for the leads
file = file_streams[0]
message_file = client.files.create(file=file, purpose="assistants")
content = """
Parse the leads from the PDF files into a json list in the following format.
[
  {
    "todays_date": "",
    "agent_name": "ANDREA",
    "roofing_company": "CORE FOUR - AUSTIN",
    "names": "BORAN ZHAO & TANIA BETANCOURT",
    "appointment_date": "4/18/24",
    "time": "2PM",
    "phone": "979-218-4997",
    "email": "TANIA@TXSTATE.EDU",
    "address": "524 CARISMATIC LN",
    "city": "AUSTIN",
    "state": "TX",
    "zip_code": "78748",
    "additional_address": "",
    "insurance_provider": "METROPOLITAN/FARMERS",
    "age_of_roof": "3 years",
    "animals_in_yard": "Yes",
    "last_roof_inspection": "",
    "notes": "",
    "contact_number": "303-908-3193"
  }
]
"""
thread = client.beta.threads.create(
    messages=[
        {
            "role": "user",
            "content": content,
            "attachments": [
                {"file_id": message_file.id, "tools": [{"type": "file_search"}]}
            ],
        }
    ]
)
run = client.beta.threads.runs.create_and_poll(
    thread_id=thread.id, assistant_id=assistant.id
)
messages = list(client.beta.threads.messages.list(thread_id=thread.id, run_id=run.id))
message_content = messages[0].content[0].text.value
json_match = JSON_REGEX.search(message_content)
if json_match:
    json_content = json_match.group(1)
    parsed_json = json.loads(json_content)
    print(json.dumps(parsed_json, indent=2))
else:
    print("No JSON content found.")
    print(message_content)
