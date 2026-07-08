import json


def read_json(file_path):

    try:

        with open(file_path, "r", encoding="utf-8") as file:

            data = json.load(file)

        return data

    except FileNotFoundError:

        return "JSON Error: File not found."

    except json.JSONDecodeError:

        return "JSON Error: Invalid JSON format."

    except Exception as e:

        return f"JSON Error: {str(e)}"