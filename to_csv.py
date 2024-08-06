import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

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

# Create the vector store
vector_store = client.beta.vector_stores.create(name="Leads")
file_streams = [open(file, "rb") for file in pdf_files]
file_batch = client.beta.vector_stores.file_batches.upload_and_poll(
    vector_store_id=vector_store.id, files=file_streams
)
print(file_batch.status)
print(file_batch.file_counts)

# Update assistant to use the vector store
assistant = client.beta.assistants.update(
    assistant_id=assistant.id,
    tool_resources={"file_search": {"vector_store_ids": [vector_store.id]}},
)

# Create a thread
thread = client.beta.threads.create()
message = client.beta.threads.messages.create(
    thread_id=thread.id,
    role="user",
    content="Parse the leads from the PDF files into a json list.",
)

# Run the assistant
run = client.beta.threads.runs.poll(
    thread_id=thread.id,
    assistant_id=assistant.id,
    instructions="Parse the leads from the PDF files into a json list.",
)

if run.status == "completed":
    messages = client.beta.threads.messages.list(thread_id=thread.id)
    for message in messages:
        print(message.content)
