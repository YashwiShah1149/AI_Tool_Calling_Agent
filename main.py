import ollama
import logging
import os
import pandas as pd
import json

from tools.calculator import calculate
from tools.datetime_tool import *
from tools.txt_reader import read_txt
from tools.json_reader import read_json
from tools.csv_lookup import read_csv



# ---------------- LOGGING ---------------- #

logging.basicConfig(
    filename="AI_assistant/logs/assistant.log",
    level=logging.INFO,
    format="%(asctime)s - %(message)s"
)

# ---------------- TOOL REGISTRY ---------------- #
# To tell llm which type of tools we have right now and for it exectution which tool it can use

TOOLS = [
    {
        "name": "calculator",
        "description": "Performs mathematical calculations"
    },

    {
        "name": "datetime_tool",
        "description": "Handles date and time operations"
    },

    {
        "name": "txt_reader",
        "description": "Reads and retrieves information from text files"
    },

    {
        "name": "json_reader",
        "description": "Reads and searches JSON files"
    },

    {
        "name": "csv_lookup",
        "description": "Reads and filters CSV files"
    }
]

# ---------------- RESOURCE REGISTRY ---------------- #
#Telling where excatly all the data is

DATA_FOLDER = "AI_assistant/data"

RESOURCES = os.listdir(DATA_FOLDER)

# ---------------- METADATA LAYER ---------------- #
#for each file need to tell that this type of data is there for which made function so it can extract on it own not done mannually
#for .csv we are extracting the column name
#for .txt first will try to find the title and subtitle into the whole txt file the will read the start of that pragraph and from that only it will summarize
#for .json extracting the key then the subkeys into it

def generate_metadata():

    metadata = {}

    for file_name in RESOURCES:

        file_path = f"{DATA_FOLDER}/{file_name}"

        # ---------------- CSV Metadata ---------------- #
        if file_name.endswith(".csv"):

            try:

                df = pd.read_csv(file_path)

                metadata[file_name] = {
                    "columns": df.columns.tolist()
                }

            except:

                metadata[file_name] = {
                    "columns": []
                }

        # ---------------- JSON Metadata ---------------- #
        elif file_name.endswith(".json"):

            try:

                with open(file_path, "r", encoding="utf-8") as file:

                    data = json.load(file)

                    metadata[file_name] = {}

                    # Top-level keys
                    metadata[file_name]["top_level_keys"] = list(data.keys())

                    # Extract nested fields
                    record_fields = []

                    for key, value in data.items():

                        if isinstance(value, list) and len(value) > 0:

                            first_record = value[0]

                            if isinstance(first_record, dict):

                                record_fields.extend(first_record.keys())

                    metadata[file_name]["record_fields"] = list(set(record_fields))

            except:

                metadata[file_name] = {
                    "top_level_keys": [],
                    "record_fields": []
                }

        # ---------------- TXT Metadata ---------------- #
        elif file_name.endswith(".txt"):

            try:

                with open(file_path, "r", encoding="utf-8") as file:

                    content = file.readlines()

                    sections = []

                    current_title = None
                    current_content = []

                    for line in content:

                        line = line.strip()

                        # Heuristic heading detection
                        is_heading = (
                            len(line.split()) <= 6
                            and (
                                line.isupper()
                                or line.istitle()
                                or line.endswith(":")
                            )
                            and not line.endswith(".")
                        )

                        # If heading detected
                        if is_heading:

                            # Save previous section
                            if current_title:

                                summary = " ".join(current_content[:2])

                                sections.append({
                                    "title": current_title,
                                    "summary": summary
                                })

                            # Start new section
                            current_title = line

                            current_content = []

                        else:

                            if line:

                                current_content.append(line)

                    # Save last section
                    if current_title:

                        summary = " ".join(current_content[:2])

                        sections.append({
                            "title": current_title,
                            "summary": summary
                        })

                    metadata[file_name] = {
                        "sections": sections
                    }

            except:

                metadata[file_name] = {
                    "sections": []
                }

    return metadata


METADATA = generate_metadata()

# ---------------- USER QUERY ---------------- #

user_query = input("Ask Your Question: ")


# ---------------- TOOL SELECTION PROMPT ---------------- #
# here tool llm to understand the user quesry and according to that use the tools to answer the user query

tool_prompt = f"""
You are an AI assistant with access to external tools.

Available tools and functions:

1. calculator
- Use for mathematical calculations.
- Supports sqrt, abs, pow, round, sin, cos, tan, log.

2. datetime_tool

Functions inside datetime_tool:

- get_current_datetime
  Use for current date and current time.

- get_current_date
  Use for today's date only.

- calculate_days_difference
  Use for calculating how many days ago something happened.

- employee_work_duration
  Use for calculating how long an employee has worked.

- generate_dispatch_timestamp
  Use for generating current dispatch timestamp.

3. txt_reader
- Use for reading text file content.

4. json_reader
- Use for reading JSON files.

5. csv_lookup:
Reads structured CSV file data.
Input format:
employees.csv

Available Tools:
{TOOLS}

Available Resources:
{RESOURCES}

Metadata:
{METADATA}


Instructions:
- Analyze the user query carefully.
- Select the BEST tool/function.
- Extract the required input.

IMPORTANT:
- Do NOT explain anything.
- Do NOT add extra text.
- Return ONLY these two lines exactly:

Tool: <tool_name>
Input: <tool_input>

Examples:

Tool: calculator
Input: 3*3

Tool: get_current_date
Input: none

User: Read policy file
Tool: txt_reader
Input: policy.txt

User: Open employee JSON data
Tool: json_reader
Input: employee_data.json

User: Find employees earning more than 150000
Tool: csv_lookup
Input: employees.csv

User: What is Alice's salary?
Tool: csv_lookup
Input: employees.csv

User: Show all Engineering employees
Tool: csv_lookup
Input: employees.csv


User Query:
{user_query}
"""


# ---------------- SEND TO LLM ---------------- #

response = ollama.chat(
    model="llama3:8b",
    messages=[
        {
            "role": "user",
            "content": tool_prompt
        }
    ]
)


# ---------------- EXTRACT LLM OUTPUT ---------------- #

llm_output = response["message"]["content"]

print("\nLLM Output:")
print(llm_output)


lines = llm_output.split("\n")

tool_name = lines[0].replace("Tool:", "").strip()

tool_input = lines[1].replace("Input:", "").strip()


# ---------------- TOOL EXECUTION ---------------- #
#After here all the tools are executed

tool_output = "No output generated."


# Calculator
if tool_name == "calculator":

    tool_output = calculate(tool_input)


# Current Datetime
elif tool_name == "get_current_datetime":

    tool_output = get_current_datetime()


# Current Date
elif tool_name == "get_current_date":

    tool_output = get_current_date()


# Days Difference
elif tool_name == "calculate_days_difference":

    tool_output = calculate_days_difference(tool_input)


# Employee Work Duration
elif tool_name == "employee_work_duration":

    tool_output = employee_work_duration(tool_input)


# Dispatch Timestamp
elif tool_name == "generate_dispatch_timestamp":

    tool_output = generate_dispatch_timestamp()


# TXT Reader
elif tool_name == "txt_reader":

    try:

        file_name = tool_input.strip()

        file_path = f"AI_assistant/data/{file_name}"

        tool_output = read_txt(file_path)

    except Exception as e:

        tool_output = f"TXT Input Error: {str(e)}"

# JSON Reader
elif tool_name == "json_reader":

    try:

        file_name = tool_input.strip()

        file_path = f"AI_assistant/data/{file_name}"

        tool_output = read_json(file_path)

    except Exception as e:

        tool_output = f"JSON Input Error: {str(e)}"

# CSV Lookup
elif tool_name == "csv_lookup":

    try:

        file_name = tool_input.strip()

        file_path = f"AI_assistant/data/{file_name}"

        tool_output = read_csv(file_path)

    except Exception as e:

        tool_output = f"CSV Input Error: {str(e)}"
        
# ---------------- FINAL RESPONSE ---------------- #
#then after getting respose we need to have a professional reply so for which here took one more llm for it

final_prompt = f"""
User Query:
{user_query}

Tool Used:
{tool_name}

Tool Output:
{tool_output}

Generate a short and professional final response.

IMPORTANT:
- Use ONLY the tool output.
- Do NOT invent information.
- If no records found, clearly say so.
-Do not add extra explanations or conversational text.
"""


final_response_data = ollama.chat(
    model="llama3:8b",
    messages=[
        {
            "role": "user",
            "content": final_prompt
        }
    ]
)


final_response = final_response_data["message"]["content"]


# ---------------- OUTPUT ---------------- #

print("\nFinal Response:")
print(final_response)


# ---------------- LOGGING ---------------- #

logging.info(f"User Query: {user_query}")
logging.info(f"Selected Tool: {tool_name}")
logging.info(f"Tool Input: {tool_input}")
logging.info(f"Tool Output: {tool_output}")
logging.info(f"Final Response: {final_response}")