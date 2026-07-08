from datetime import datetime

# 1. Current Date & Time
def get_current_datetime():

    try:

        now = datetime.now()

        return now.strftime("%Y-%m-%d %H:%M:%S")

    except Exception as e:

        return f"Datetime Error: {str(e)}"


# 2. Current Date
def get_current_date():

    try:

        today = datetime.now()

        return today.strftime("%Y-%m-%d")

    except Exception as e:

        return f"Datetime Error: {str(e)}"


# 3. Time Difference
def calculate_days_difference(past_date):

    try:

        past = datetime.strptime(past_date, "%Y-%m-%d")

        today = datetime.now()

        difference = today - past

        return f"{difference.days} days ago"

    except Exception as e:

        return f"Datetime Error: {str(e)}"


# 4. Employee Work Duration
def employee_work_duration(join_date):

    try:

        join = datetime.strptime(join_date, "%Y-%m-%d")

        today = datetime.now()

        duration = today - join

        return f"Employee has worked for {duration.days} days"

    except Exception as e:

        return f"Datetime Error: {str(e)}"


# 5. Timestamp Generator
def generate_dispatch_timestamp():

    try:

        dispatch_time = datetime.now()

        return f"Product dispatched at {dispatch_time.strftime('%Y-%m-%d %H:%M:%S')}"

    except Exception as e:

        return f"Datetime Error: {str(e)}"