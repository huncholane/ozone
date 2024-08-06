import json
import os
import re

import pandas as pd
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
JSON_REGEX = re.compile(r"```json(.*)```", re.DOTALL)
API_KEY = os.getenv("OPENAI_API_KEY", None)
if API_KEY is None:
    print("Please set the OPENAI_API_KEY environment variable.")
    exit(1)


def parse_lead_file(filename) -> str:
    """Uses the OpenAI API to parse the lead file and return raw content."""
    file = open(filename, "rb")
    message_file = client.files.create(file=file, purpose="assistants")
    content = """
    Parse the leads from the PDF files into a json list in the following format.
    [
    {
        "today_date": "",
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
    messages = list(
        client.beta.threads.messages.list(thread_id=thread.id, run_id=run.id)
    )
    return messages[0].content[0].text.value


def pdf_to_json(leads: list, filename: str, max_retries=3, attempt=0):
    """Parse the leads from a PDF file and append them to the leads list."""
    message = parse_lead_file(filename)
    json_match = JSON_REGEX.search(message)
    try:
        json_content = json_match.group(1)
        parsed_json = json.loads(json_content)
        leads.extend(parsed_json)
    except Exception as e:
        print(
            f"Error parsing JSON from {filename}:\n{e}\nCurrently on attempt {attempt + 1} of {max_retries}"
        )
        pdf_to_json(leads, filename, max_retries, attempt + 1)


# Get the pdf filenames
pdf_files = []
for root, dirs, files in os.walk(".data/leads"):
    for file in files:
        if file.endswith(".pdf"):
            pdf_files.append(os.path.join(root, file))

# Create the assistant
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
assistant = client.beta.assistants.create(
    name="Lead Parser",
    description="Parse leads from PDF files",
    model="gpt-3.5-turbo",
    tools=[{"type": "file_search"}],
)

# Ask for the leads
from threading import Thread

json_leads = []
threads = [
    Thread(target=pdf_to_json, args=(json_leads, filename), daemon=True)
    for filename in pdf_files
]
for thread in threads:
    thread.start()
for thread in threads:
    thread.join()


df = pd.DataFrame(json_leads)
df.to_csv(".data/leads.csv", index=False)
