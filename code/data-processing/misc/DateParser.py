# Parse date

from datetime import datetime

# date example = "1900-01-30T12:30:00.000-0600"
DATE_FMT = "%Y-%m-%dT%H:%M"

def get_date(dt_str, date_format = DATE_FMT):
    return datetime.strptime(dt_str[:16], date_format)

def get_date_from_int(int_val):
    try:
        int_val = int(int_val)
        year = int_val // 10000
        month = ( int_val % 10000) // 100
        day = int_val % 100
        return datetime(year=year, month=month, day=day)
    except BaseException:
        print("Error parsing date: ", int_val)
        return datetime(year=1, month=1, day=1)


def date_to_int(dt:datetime):
    return dt.year * 10000 + dt.month * 100 + dt.day


def get_date_dict(file):
    """Get patient date records from file"""
    with open(file, "r") as fp:
        patient_lines = fp.read().strip().split('\n')
    date_dict = {}
    for line in patient_lines:
        seperated = line.strip().split('\t')
        id = int(seperated[0])
        dates = seperated[1:]

        for date in dates:
            date_dict[id] = get_date(date)

    return date_dict


