import re
from operator import itemgetter


def flip(value: str):
    """Flip Y/N values for vital <-> deceased"""
    if str(value).upper() == 'Y':
        return 'N'
    elif str(value).upper() == 'N':
        return 'Y'
    else:
        return 'Unknown'


def combine(first: str, second: str) -> str:
    out = str(first) + '\n' + '\n'.join(line for line in second.splitlines() if line.strip() not in first)
    return out.replace('NULL', '', 1).strip()


def highlight(excerpt, highlight_term, case_sensitive=False, substrings=True):
    """highlight instances of term found in excerpt by using ANSI escape code
    https://en.wikipedia.org/wiki/ANSI_escape_code"""

    import re

    green = "\033[1;32;40m"
    escape = "\033[0m"

    if highlight_term is None:
        return green + excerpt + escape

    any_letters = "[a-zA-Z]*" * substrings
    search_term = any_letters + highlight_term.rstrip() + any_letters

    re_iter = re.finditer(search_term, excerpt, re.IGNORECASE * (not case_sensitive))
    match = next(re_iter, None)

    if match:
        start, end = match.span()
        return excerpt[:start] + green + excerpt[start:end] + escape + highlight(excerpt[end:], highlight_term,
                                                                                 case_sensitive=case_sensitive,
                                                                                 substrings=substrings)
    else:
        return excerpt


def find_words(excerpt, term, case_sensitive=False):
    import re
    matches = []
    any_letters = "[a-zA-Z]*"
    search_term = any_letters + term.rstrip() + any_letters

    matches = re.findall(search_term, excerpt, re.IGNORECASE * (not case_sensitive))
    matches = [i.lower() for i in matches]
    return list(set(matches))


def single_space(input: str):
    """
    Replace consecutive spaces, \n with single space to increase readability
    """
    temp = input.replace('\n', ' ').replace('\r', ' ')
    return re.sub(' [ ]+', ' ', temp)


def get_range(value: str, debug=False):
    """Given a textual range (e.g. '3.0-5.0') attempt to return a list of values ['3.0', '5.0']"""
    value = value.replace('<=', '0.0-')
    value = value.replace('<', '0.0-')
    values = value.replace(' ', '').split('-')

    if len(values) > 2:
        values.remove('')
    if len(values) > 2:
        raise Exception("error parsing value")

    if debug:
        print(f"{value} --> {values}")
    return values


def UNL(value: str, debug=False):
    return get_range(value, debug)[1]


def LNL(value: str, debug=False):
    return get_range(value, debug)[0]


def resection_extent(value: str):
    value = value.lower()
    if 'biopsy of' in value:
        return 'Biopsy'
    if 'polypectomy of' in value:
        return 'Polypectomy'
    if 'excision of' in value:
        return 'Excision'
    if 'colectomy' in value:
        return 'Colectomy'
    if 'resection of' in value:
        return 'Resection'
    return 'Unknown'


def surgery_type(value: str):
    temp = value.lower()

    if 'open approach' in temp:
        return 'Open Approach'
    if 'endoscop' in temp or 'laparoscop' in temp:
        return 'Laparoscopy'
    return 'Unknown'


def unbreak(line, seperators=['\t', '\n', '\r'], unspaced=False):
    """remove seperators from line"""
    for sep in seperators:
        line = line.replace(sep, " ")
    if unspaced:
        return single_space(line)
    return line


def countNULL(df):
    num_entries = dict()
    for column in df.columns:
        non_zeros = len(df) - len(df[df[column] == "NULL"])
        num_entries[column] = non_zeros

    num_entries = dict(sorted(num_entries.items(), key=itemgetter(1), reverse=True))
    print(num_entries)

    for key, value in num_entries.items():
        print(f'{key:40s} {value:4d}')


