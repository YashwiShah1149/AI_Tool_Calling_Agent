def read_txt(file_path):

    try:

        with open(file_path, "r", encoding="utf-8") as file:

            content = file.read(3000)

            return content

    except FileNotFoundError:

        return "TXT Error: File not found."

    except Exception as e:

        return f"TXT Error: {str(e)}"