import ollama
import logging
import os
import pandas as pd
import json
import re

from tools.calculator import calculate
from tools.datetime_tool import *
from tools.txt_reader import read_txt
from tools.json_reader import read_json
from tools.csv_lookup import read_csv
from tools.dataframe_operation import *



# LOGGING
#Stores all the execution part 
#Useful for debugging and tracking system

logging.basicConfig(
    filename="AI_assistant/logs/assistant.log",
    level=logging.INFO,
    format="%(asctime)s - %(message)s"
)


# TOOL REGISTRY
#This list tells LLM:- which tool exist
#                    - What each tool does
# LLm read this during the planning

TOOLS = [

    {
        "name": "filter_data",
        "description": "Filters rows in structured data using column, condition and value"
    },

    {
        "name": "count_data",
        "description": "Counts total rows in structured data"
    },

    {
        "name": "sort_data",
        "description": "Sorts structured data using a column and order"
    },

    {
        "name": "max_data",
        "description": "Finds row with maximum value in a column"
    },

    {
        "name": "min_data",
        "description": "Finds row with minimum value in a column"
    },

    {
        "name": "average_data",
        "description": "Calculates average value of numeric column"
    },

    {
        "name": "unique_values",
        "description": "Finds unique values from a column"
    },

    {
        "name": "calculate",
        "description": "Performs mathematical calculations"
    },

    {
        "name": "read_txt",
        "description": "Reads TXT files"
    },

    {
        "name": "read_json",
        "description": "Reads JSON files"
    },

    {
        "name": "read_csv",
        "description": "Reads CSV files"
    },

    {
        "name": "get_current_datetime",
        "description": "Returns current datetime"
    },

    {
        "name": "get_current_date",
        "description": "Returns current date"
    }
]



# TOOL FUNCTION MAPPING
# LLM only generates tool names as TEXT.
# Example:
# "tool": "count_data"
# Python cannot execute text directly.
# So this mapping connects:
# "count_data" -> actual count_data() function
# This is used by the execution engine.


TOOL_FUNCTIONS = {

    "filter_data": filter_data,

    "count_data": count_data,

    "sort_data": sort_data,

    "max_data": max_data,

    "min_data": min_data,

    "average_data": average_data,

    "unique_values": unique_values,

    "calculate": calculate,

    "read_txt": read_txt,

    "read_json": read_json,

    "read_csv": read_csv,

    "get_current_datetime": get_current_datetime,

    "get_current_date": get_current_date
}


# RESOURCE REGISTRY
# Finds all available files inside data folder.
# Example:
# employees.csv
# policy.txt
# employee.json

DATA_FOLDER = "AI_assistant/data"

RESOURCES = os.listdir(DATA_FOLDER)


# METADATA GENERATION
# Metadata helps the LLM understand:
# - What data exists
# - What columns exist
# - What fields exist
# This improves tool selection accuracy.

def generate_metadata():

    metadata = {}

    for file_name in RESOURCES:

        file_path = f"{DATA_FOLDER}/{file_name}"

        
        # CSV FILES
        # Extract column names from CSV files
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

        
        # JSON FILES
        # Extract:- top-level keys
        #         - nested fields
        
        elif file_name.endswith(".json"):

            try:

                with open(file_path, "r", encoding="utf-8") as file:

                    data = json.load(file)

                    metadata[file_name] = {}

                    metadata[file_name]["top_level_keys"] = list(data.keys())

                    fields = []

                    for key, value in data.items():

                        if isinstance(value, list) and len(value) > 0:

                            first = value[0]

                            if isinstance(first, dict):

                                fields.extend(first.keys())

                    metadata[file_name]["record_fields"] = list(set(fields))

            except:

                metadata[file_name] = {
                    "top_level_keys": [],
                    "record_fields": []
                }

        
        # TXT FILES
        # Stores first 5 lines as preview.
        # Helps LLM understand text content.

        elif file_name.endswith(".txt"):

            try:

                with open(file_path, "r", encoding="utf-8") as file:

                    content = file.readlines()

                    metadata[file_name] = {
                        "preview": content[:5]
                    }

            except:

                metadata[file_name] = {
                    "preview": []
                }

    return metadata


METADATA = generate_metadata()


# USER QUERY

user_query = input("Ask Your Question: ")


# PLANNING PROMPT
# This prompt tells the LLM:
# - You are a planning system
# - Break tasks into steps
# - Use tools only
# - Return JSON only

# The LLM uses:
# - tools
# - metadata
# - examples
# to generate a multi-step execution plan.

intent_prompt = f"""

You are an AI planning system.

Your job:
1. Understand the user query.
2. Break the task into MULTIPLE executable steps.
3. Return ONLY valid JSON.
4. Never explain.
5. Never use markdown.
6. Never hallucinate tools.
7. Use ONLY available tools.
8. Use save_as when future steps need previous outputs.
9. Use $variable_name when referencing previous outputs.
10. NEVER invent numbers manually.
11. ALWAYS use tools to get values.
12. NEVER invent unsupported tool arguments.
13. ALWAYS follow the exact supported arguments for each tool.


# IMPORTANT RULES


- NEVER generate SQL queries.
- NEVER use SELECT statements.
- NEVER write database syntax.
- ALWAYS solve tasks using available tools only.
- ALWAYS break complex tasks into sequential tool calls.
- NEVER place SQL inside calculator expressions.
- NEVER directly calculate counts mentally.
- ALL counts MUST come from count_data tool.
- NEVER invent values manually.
- NEVER generate fake variables.


# IMPORTANT MEMORY RULES


- If the output of a step is needed later,
  ALWAYS store it using save_as.

- NEVER use:
    $0
    $1
    previous_result

- ALWAYS use meaningful variable names.

GOOD VARIABLE NAMES:
    finance_count
    hr_avg_salary
    top_employee
    engineering_employees

- Any value used later MUST first be stored in memory.

- When referencing previous outputs,
  ALWAYS use:
    $variable_name

GOOD:
    "$finance_count * $hr_count"

BAD:
    "$0 + 1000"


# TOOL ARGUMENT RULES


ONLY use these exact arguments.

DO NOT invent new arguments.

# filter_data

Supported arguments:
- column
- condition
- value

Example:
{{
    "tool": "filter_data",

    "args": {{
        "column": "department",
        "condition": "==",
        "value": "HR"
    }}
}}

# count_data

Supported arguments:
- no arguments

Example:
{{
    "tool": "count_data",

    "args": {{}}
}}

# average_data

Supported arguments:
- column

Example:
{{
    "tool": "average_data",

    "args": {{
        "column": "salary"
    }}
}}

# max_data

Supported arguments:
- column

# min_data

Supported arguments:
- column

# sort_data

Supported arguments:
- column
- order

# calculate

Supported arguments:
- expression

Example:
{{
    "tool": "calculate",

    "args": {{
        "expression": "$finance_count * $hr_count"
    }}
}}

# IMPORTANT

- NEVER pass:
    resource
    data
    dataset
    rows

unless explicitly supported by the tool.

- average_data automatically uses current_data.
- count_data automatically uses current_data.
- max_data automatically uses current_data.
- min_data automatically uses current_data.


# AVAILABLE RESOURCES


Available Resources:
{RESOURCES}

Metadata:
{METADATA}

Available Tools:
{TOOLS}


# EXAMPLE 1


Query:
Multiply the number of employees in Finance with the number of employees in HR

Response:

{{
    "resource": "employees.csv",

    "plan": [

        {{
            "tool": "filter_data",

            "args": {{
                "column": "department",
                "condition": "==",
                "value": "Finance"
            }}
        }},

        {{
            "tool": "count_data",

            "args": {{}},

            "save_as": "finance_count"
        }},

        {{
            "tool": "filter_data",

            "args": {{
                "column": "department",
                "condition": "==",
                "value": "HR"
            }}
        }},

        {{
            "tool": "count_data",

            "args": {{}},

            "save_as": "hr_count"
        }},

        {{
            "tool": "calculate",

            "args": {{
                "expression": "$finance_count * $hr_count"
            }}
        }}
    ]
}}


# EXAMPLE 2

Query:
Find the average salary of HR employees and add 10000

Response:

{{
    "resource": "employees.csv",

    "plan": [

        {{
            "tool": "filter_data",

            "args": {{
                "column": "department",
                "condition": "==",
                "value": "HR"
            }}
        }},

        {{
            "tool": "average_data",

            "args": {{
                "column": "salary"
            }},

            "save_as": "hr_avg_salary"
        }},

        {{
            "tool": "calculate",

            "args": {{
                "expression": "$hr_avg_salary + 10000"
            }}
        }}
    ]
}}


# USER QUERY

User Query:
{user_query}

"""


# LLM PLANNING
# First LLM call.
# Generate multi-step execution plan.


response = ollama.chat(

    model="llama3:8b",

    messages=[
        {
            "role": "user",
            "content": intent_prompt
        }
    ],

    options={
        "temperature": 0
    }
)

intent_output = response["message"]["content"]

print("\nGenerated Plan:\n")

print(intent_output)


# PARSE JSON
# LLM output comes as TEXT.
# This section:
# - extracts JSON
# - cleans response
# - converts text -> Python dictionary

try:

    start = intent_output.find("{")

    cleaned_output = intent_output[start:]

    if not cleaned_output.strip().endswith("}"):

        cleaned_output += "}"

    intent = json.loads(cleaned_output)

except Exception as e:

    print(f"\nJSON Parsing Error: {str(e)}")

    exit()



# EXTRACT PLAN
# Extract:
# - resource
# - execution plan
# from parsed JSON.

resource = intent.get("resource")

plan = intent.get("plan", [])

current_data = None

current_output = None

original_data = None




# VARIABLE RESOLVER
# Replaces variables like:
# $finance_count
# with actual memory values:
# 20
# This enables memory-based reasoning.

def resolve_variables(obj, memory):

    
    # STRING
   

    if isinstance(obj, str):

        variables = re.findall(
            r"\$([a-zA-Z_][a-zA-Z0-9_]*)",
            obj
        )

        for variable in variables:

            if variable in memory:

                obj = obj.replace(
                    f"${variable}",
                    str(memory[variable])
                )

        return obj

    # LIST

    elif isinstance(obj, list):

        return [
            resolve_variables(item, memory)
            for item in obj
        ]

    
    # DICTIONARY

    elif isinstance(obj, dict):

        return {
            key: resolve_variables(value, memory)
            for key, value in obj.items()
        }

    return obj



# EXECUTION ENGINE
# This section executes the multi-step plan
# generated by the LLM.
# It:
# - reads each step
# - selects the correct tool
# - executes the tool
# - stores outputs in memory
# - passes outputs to future steps

memory = {}

print("\nExecuting Plan...\n")

try:

    for step_number, step in enumerate(plan, start=1):

        tool_name = step["tool"]

        args = step.get("args", {})

        print(f"\nStep {step_number}: {tool_name}")

        print(f"Original Args: {args}")

        
        # RESOLVE VARIABLES
        resolved_args = resolve_variables(
            args,
            memory
        )

        print(f"Resolved Args: {resolved_args}")

        
        # VALIDATE TOOL

        if tool_name not in TOOL_FUNCTIONS:

            raise Exception(
                f"Invalid tool: {tool_name}"
            )

        tool_function = TOOL_FUNCTIONS[tool_name]

        
        # FILTER TOOL

        if tool_name == "filter_data":

            # RESET TO ORIGINAL DATA

            current_data = original_data

            output = tool_function(
                current_data,
                **resolved_args
            )

            current_data = output

        
        # SORT TOOL
        elif tool_name == "sort_data":

            output = tool_function(
                current_data,
                **resolved_args
            )

            current_data = output

        
        # AGGREGATION TOOLS

        elif tool_name in [

            "count_data",
            "max_data",
            "min_data",
            "average_data",
            "unique_values"

        ]:

            output = tool_function(
                current_data,
                **resolved_args
            )

        
        # CALCULATOR

        elif tool_name == "calculate":

            output = tool_function(
                resolved_args["expression"]
            )

       
        # DATETIME TOOLS
        
        elif tool_name in [

            "get_current_datetime",
            "get_current_date"

        ]:

            output = tool_function()

        
        # FILE READERS
        
        elif tool_name in [

            "read_txt",
            "read_json",
            "read_csv"

        ]:

            output = tool_function(
                resolved_args["file_path"]
            )

        else:

            output = None

        
        # STORE OUTPUT IN MEMORY
        
        save_as = step.get("save_as")

        if save_as:

            memory[save_as] = output

            print(f"\nStored In Memory: {save_as}")

        
        # UPDATE CURRENT OUTPUT

        current_output = output

        print(f"\nOutput:\n{output}")

        print(f"\nCurrent Memory:\n{memory}")

except Exception as e:

    current_output = f"Execution Error: {str(e)}"



# LOGGING

logging.info(f"User Query: {user_query}")

logging.info(f"Generated Plan: {intent}")

logging.info(f"Final Result: {current_output}")



# FINAL RESPONSE PROMPT
# Creates second LLM prompt.
# Purpose:
# Convert raw execution output into
# professional natural language response.

final_prompt = f"""

User Query:
{user_query}

Execution Result:
{current_output}

Generate a short professional response.

"""


# FINAL RESPONSE

final_response = ollama.chat(

    model="llama3:8b",

    messages=[
        {
            "role": "user",
            "content": final_prompt
        }
    ]
)

print("\nFinal Response:\n")

print(final_response["message"]["content"])