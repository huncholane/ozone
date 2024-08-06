import re
import json

text = """
No JSON content found.
I have found a lead sheet from the file "BORAN ZHAO- CORE AUSTIN TX.pdf" that contains information about a potential client. Here is the extracted lead information in JSON format:

```json
[
    {
        "Agent's Name": "ANDREA",
        "ROOFING COMPANY": "CORE FOUR - AUSTIN",
        "Name(s)": "BORAN ZHAO & TANIA BETANCOURT",
        "Appointment Date": "4/18/24",
        "Time": "2PM",
        "Phone": "979-218-4997",
        "Email": "TANIA@TXSTATE.EDU",
        "Address": "524 CARISMATIC LN",
        "City": "AUSTIN",
        "State": "TX",
        "ZIP CODE": "78748",
        "Insurance Provider": "METROPOLITAN/FARMERS",
        "Age of Roof": "3",
        "Any Animal in Yard?": "YES",
        "When was the last time you had a Roof inspection?": "",
        "Additional Address": "ALT # 512-291-2707"
    }
]
```

This JSON list captures the lead details from the provided document.
"""

regex = re.compile(r"```json(.*)```", re.DOTALL)
match = regex.search(text)
if match:
    json_content = match.group(1)
    parsed_json = json.loads(json_content)
    print(json.dumps(parsed_json, indent=2))
else:
    print("No JSON content found.")
