import re

from misc.DateParser import get_date_from_int
from NLP.str_functions import single_space


def to_date_str(text):
    if text.isnumeric():
        return get_date_from_int(int(text)).strftime("%Y/%m/%d")


def lookup(text, lookup_terms: dict, not_found_result=None):
    """ return result if term found in text
    given lookup_terms dict (term -> result) """

    for term, result in lookup_terms.items():
        if term.lower() in text.lower():
            return result
    return not_found_result


def lookup_list(text, terms, not_found_result=None):
    """ return matching result
    given list of terms"""

    return lookup(text, {term: term for term in terms}, not_found_result)


def multiple_lookup(text, lookup_terms: dict, not_found_result=None) -> str:
    text = text.lower()
    matched = []

    for term, result in lookup_terms.items():
        if term.lower() in text:
            matched += [result]

    if not matched:
        return not_found_result

    return '/'.join(matched)


def multiple_lookup_list(text, terms, not_found_result=None):
    return multiple_lookup(text, {term: term for term in terms}, not_found_result)


def find_matching_sentences(text, term, case_sensitive=False, partial_term_valid=True):
    matching = extract_sentences(text=text, find_term=term, case_sensitive=case_sensitive,
                                 partial_term_valid=partial_term_valid)
    if len(matching) > len(term):
        return matching
    else:
        return "NULL"


def extract_sentences(text, find_term, case_sensitive=False, partial_term_valid=True):
    """Find sentences in text that contain find_term, concatenate the matching sentences and return them"""

    text = re.sub(r':[ ]*\n', ': ', text)
    text = re.sub(r'[ ]?\r\n[ ]?', '\n', text)
    # from nltk.tokenize import sent_tokenize
    sent_re = re.compile(r'[.]([ ]|(\n))|\n\n|\n(?=T\d)')  # match sentences

    sentences = [sent.strip() for sent in sent_re.split(text) if sent is not None and sent.strip() != '']

    # for num, sent in enumerate(sentences):
    #     print(num, repr(sent))
    #
    # print("len: ", len(''.join(sentences)), len(text))

    any_letters = "[a-zA-Z]*" * partial_term_valid
    search_term = any_letters + find_term.rstrip() + any_letters

    term_re = re.compile(search_term, re.IGNORECASE * (not case_sensitive))

    matching_sentences = set(single_space(sent) + '.' for sent in sentences if term_re.findall(sent))

    output = ' \n'.join(matching_sentences)

    # if len(matching_sentences) > 1:
    #     print('*' * 40)
    #     print(matching_sentences)
    #     print('---')
    #     print(output)
    #     print('*'*40)

    return output