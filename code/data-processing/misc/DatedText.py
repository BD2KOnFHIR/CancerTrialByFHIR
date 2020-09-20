from datetime import datetime

class DatedText:
    """Class for keeping track of only most recent text entry
    if date is same, then text will be concatenated unless already present"""
    def __init__(self, text:str='NULL', date:datetime = datetime(year=1, month=1, day=1)):
        self.date = date
        self.text = text

    def __add__(self, update_data):
        text, date = update_data
        if date == self.date and text not in self.text:
            # TODO improve text already present checking
            self.text = self.text + ':' + text
        elif date > self.date:
            self.date = date
            self.text = text
        else:
            pass
        return DatedText(self.text, self.date)

    def __str__(self):
        return self.text

    def __repr__(self):
        return 'DatedText(' + self.text + ', ' + str(self.date) + ')'

    def get_date(self):
        return self.date

