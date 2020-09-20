# Code for parsing synaptic reports

import string
from datetime import datetime
from misc.DatedText import DatedText
from misc.DateParser import get_date, date_to_int

with open('Accepted_Syn_Labels.txt', 'r', encoding='utf8') as f:
    ACCEPTED_SYN_LABELS = f.read().splitlines()

SINGLE_ENTRY_FIELDS = ['Regional lymph nodes']  # do not append other sub fields to this

addendum = "ADDENDUM"


def tag_spliter(line, verified_labels=True):
    indent = 0
    for char in line:
        if char in string.whitespace:
            indent += 1
        else:
            break

    if ':' in line:
        index = line.find(':')
        # label = line.split(':')[0].strip()
        # text = line.split(':')[1]
        label = line[:index].strip()
        text = line[index + 1:].strip()
        if verified_labels and label not in ACCEPTED_SYN_LABELS:
            label = None
            text = line
    else:
        label = None
        text = line

    return indent, label, text


class Synaptic_Parser(dict):
    """read in synaptic sections.
    save the indentation in self.stack and add indented lines to previous less indented entries"""

    def __init__(self):
        super().__init__()
        self.stack = {}
        self.date = datetime(year=1, month=1, day=1)
        self.labels = []

    def add(self, indent, label, value):
        if indent < 2:
            indent = 10  # sometimes first entry not indented
        if label is None:
            self.update_higher(1000, label, value)
        else:
            self[label] = ""
            self.update_stack(indent, label)
            self.update_higher(indent, label, value)

    def update_stack(self, indent, label):
        """ remove items from stack with lower indentation """
        self.stack[indent] = label
        greater = [key for key in self.stack.keys() if key > indent]
        for key in greater:
            self.stack.pop(key)

    def update_higher(self, indent, label, value):
        value = value.rstrip()
        for key, key_label in self.stack.items():
            if value in self.get(key, ""):  # try to prevent adding duplicate lines
                continue
            if label is None:
                self[self.stack[key]] += "\r\n" + value
            elif label == key_label:
                self[self.stack[key]] += value
            elif self.stack[key] not in SINGLE_ENTRY_FIELDS:
                self[self.stack[key]] += ("\r\n" + " " * (indent - key) + label + ":" + value)

    def set_doc_date(self, document_date):
        """set the current document date for use when add() entries"""
        self.date = get_date(document_date)
        self["NOTE_DATE"] = str(date_to_int(self.date))

    def get_date(self):
        return self.date

    def read_section(self, section):
        id = section['id']
        name = section['name']
        body = section['body']
        body: str

        self._append_to("ALL_TEXT", body)

        if name == "SYNOPTIC REPORT":
            self._append_to(name, body)
            for line in body.split("\r\n"):
                indent, label, text = tag_spliter(line)
                self.labels.append(label)
                self.add(indent, label, text)
            self.stack = {}

        # very monkey patch fix to get only addendum from footer in our data
        if name == "SYNAPTIC REPORT - FOOTER":
            self._append_to(name, body)
            temp = self.get(addendum, "")  # copy multiple addendum sections
            for line in body.split("\r\n"):
                indent, label, text = tag_spliter(line)
                if temp != "" and text in temp:
                    continue
                self.labels.append(label)
                self.add(indent, label, text)
            if addendum in self and self[addendum] not in temp:
                self[addendum] += temp
            self.stack = {}


        elif name == "DIAGNOSIS COMMENT" or name == "COMMENT":
            self._append_to("COMMENT", body)
        elif name == "GROSS DESCRIPTION":
            self._append_to("GROSS DESCRIPTION", body)
            if "BLOCK SUMMARY:" in body:
                text_ = body.split("BLOCK SUMMARY:")[1]  # quick and dirty method
                self._append_to("BLOCK SUMMARY", text_)

    def remove_breaks(self, seperators=["\t"], replacement=" "):
        for key, value in self.items():
            for sep in seperators:
                if sep in value:
                    value = value.replace(sep, replacement)
                    self[key] = value

    def _append_to(self, key, text: str):
        # add text to full sections while checking for redundant lines
        if key not in self:
            self[key] = ""
        for line in text.splitlines():
            if line not in self[key]:
                self[key] = self[key] + line + '\n'

    def strip_all(self):
        for key in self.keys():
            self[key] = self[key].strip()

    def get_labels_found(self):
        return self.labels

    def print(self):
        for key, value in self.items():
            max_len = max(len(key) for key in self)
            print(f" {key:{max_len}s} --> {value}")

    def set_refs_to_addendum(self):
        """if value refers to addendum then overwrite the key with that of addendum if it exists"""
        if addendum in self:
            for label, value in self.items():
                if label.isupper() or len(value) > 100:
                    continue
                if "addendum" in value.lower():
                    self[label] += " " + addendum + ": " + self[addendum]


class Synaptic_only_Parser(Synaptic_Parser):
    def read_section(self, section):
        id = section['id']
        name = section['name']
        body = section['body']
        body: str

        if "GROSS" in name:
            self._append_to(name, body)
            for line in body.split("\r\n"):
                indent, label, text = tag_spliter(line, verified_labels=False)
                self.labels.append(label)
                self.add(indent, label, text)
            self.stack = {}
