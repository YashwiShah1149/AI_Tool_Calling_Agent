import pandas as pd


# ---------------- FILTER ---------------- #

def filter_data(data, column, condition, value):

    filtered = []

    for row in data:

        try:

            cell_value = row[column]

            # TRY NUMERIC COMPARISON
            try:

                cell_value = float(cell_value)

                value_num = float(value)

            except:

                value_num = value

            # CONDITIONS
            if condition == ">" and cell_value > value_num:

                filtered.append(row)

            elif condition == "<" and cell_value < value_num:

                filtered.append(row)

            elif condition == ">=" and cell_value >= value_num:

                filtered.append(row)

            elif condition == "<=" and cell_value <= value_num:

                filtered.append(row)

            elif condition == "==" and str(cell_value).lower() == str(value).lower():

                filtered.append(row)

            elif condition == "!=" and str(cell_value).lower() != str(value).lower():

                filtered.append(row)

        except:

            pass

    return filtered

# ---------------- COUNT ---------------- #

def count_data(data):

    return len(data)


# ---------------- SORT ---------------- #

def sort_data(data, column, order="ascending"):

    df = pd.DataFrame(data)

    ascending = True

    if order.lower() == "descending":

        ascending = False

    result = df.sort_values(
        by=column,
        ascending=ascending
    )

    return result.to_dict(orient="records")


# ---------------- MAX ---------------- #

def max_data(data, column):

    df = pd.DataFrame(data)

    result = df.loc[df[column].idxmax()]

    return result.to_dict()


# ---------------- MIN ---------------- #

def min_data(data, column):

    df = pd.DataFrame(data)

    result = df.loc[df[column].idxmin()]

    return result.to_dict()


# ---------------- AVERAGE ---------------- #

def average_data(data, column):

    df = pd.DataFrame(data)

    return df[column].mean()


# ---------------- UNIQUE VALUES ---------------- #

def unique_values(data, column):

    df = pd.DataFrame(data)

    return df[column].unique().tolist()