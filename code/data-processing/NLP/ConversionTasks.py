from NLP.NLP_Functions import *
import re

class Conversion:
    """ Abstract class that defines a simple NLP tasks to perform on
         the defined self.name data element using
         self.function() based on data from self.name and self.reference
    """

    name = None  # data element
    reference = None  # reference data element to aid in NLP task
    debug = True
    delim = 60  # char width for debug print output
    DEBUG_COUNT = 20  # number of cases to print out per conversion class

    def __init__(self):
        self.count = 0
        pass

    def get_name(self):
        return self.name

    def get_ref(self):
        return self.reference or self.name

    def function(self, text: str):
        "To implement"
        return text

    def num_args(self):
        return 1 + bool(self.reference)

    def __str__(self):
        return f"Conversion for {self.name}"

    def __call__(self, *args, **kwargs):
        if len(args) > 0 and args[0] == "NULL":
            return "NULL"

        result = self.function(*args[:self.num_args()], **kwargs)

        if self.debug and self.count <= self.DEBUG_COUNT:
            print(
                f"<Input: {'[' + ', '.join(args[:self.num_args()]) + ']>':{self.delim}s} ------ <Result: {result}>".replace(
                    '\n', ''))
            self.count += 1

        if result is None:
            return "NULL"
        return result

    def set_debug_delim(self, delim):
        self.delim = int(delim)


class VitalStatus(Conversion):
    name = "Colorectal.subject.vitalStatus"

    def function(self, text: str):
        return {"Y": 'Yes', "N": "No"}.get(text.upper())


class Hgb(Conversion):
    name = "Colorectal.laboratoryTest.Hgb.value"

    def function(self, text: str):
        try:
            if float(text) >= 9.0:
                return "Yes"
        except ValueError:
            pass
        return "No"


class absoluteNeutrophilCount(Conversion):
    name = "Colorectal.laboratoryTest.absoluteNeutrophilCount.value"
    reference = "Colorectal.laboratoryTest.absoluteNeutrophilCount.LNL"

    def function(self, text: str, ref: str):
        try:
            if float(text) >= float(ref):
                return "Yes"
        except ValueError:
            pass
        return "No"


class Creatinine(Conversion):
    name = "Colorectal.laboratoryTest.creatinine.value"
    reference = "Colorectal.laboratoryTest.creatinine.UNL"

    def function(self, text: str, ref):
        try:
            if float(text) <= 1.5 * float(ref):
                return "Yes"
        except ValueError:
            pass
        return "No"


class Platelet(Conversion):
    name = "Colorectal.laboratoryTest.plateletCount.value"

    def function(self, text: str):
        try:
            if float(text) >= 100:
                return "Yes"
        except ValueError:
            pass
        return "No"


class Bilirubin(Conversion):
    name = "Colorectal.laboratoryTest.bilirubin.value"
    reference = "Colorectal.laboratoryTest.bilirubin.UNL"

    def function(self, text: str, ref: str):
        try:
            if float(text) <= 1.5 * float(ref):
                return "Yes"
        except ValueError:
            pass
        return "No"


class NegativeSerumPregnancyTestDate(Conversion):
    name = "Colorectal.laboratoryTest.serumPregnancy.date"

    def function(self, text):
        return to_date_str(text)


class AssignedTreatmentMedication(Conversion):
    name = "Colorectal.medication.treatment.code"

    def function(self, text: str):
        text = text.lower()
        meds = []

        if "oxaliplatin" in text or "eloxatin" in text:
            meds += ["Oxaliplatin"]
        if "fluorouracil" in text or "efudex" in text:
            meds += ["Fluorouracil"]
        if "leucovorin" in text:
            meds += ["Leucovorin"]
        if "cetuximab" in text:
            meds += ["Cetuximab"]

        return '/'.join(meds) or "NULL"


class QuestionNum13(Conversion):
    name = "Colorectal.macro.polyps"

    def function(self, text: str):
        text = text.lower()
        if "polyposis" in text:
            return "Yes"

        return "No"


class QuestionNum14(Conversion):
    name = "Colorectal.preAnalytic.clinicalAssessmentDate"

    def function(self, text: str):
        return to_date_str(text)


class QuestionNum15(Conversion):
    name = "Colorectal.micro.colonoscopyAssessmentDate"

    def function(self, text: str):
        return to_date_str(text)


class QuestionNum16(Conversion):
    """TODO: Need to validate"""
    name = "Colorectal.surgery.resectionExtent"

    def function(self, text: str):
        return lookup(text, {'Biopsy': 'Biopsy', 'Polypectomy': 'Polypectomy', 'resection': 'Bowel resection',
                             'excision': 'Local excision'}, 'Indeterminate')


class QuestionNum17(Conversion):
    name = "Colorectal.surgery.type"

    def function(self, text: str):
        return lookup(text, {'open approach ': 'Open approach', 'Laparoscop': 'Laparoscopic', 'endoscop': 'Laparoscopic'}, 'NULL')


class QuestionNum18(Conversion):
    name = "Colorectal.surgery.date"

    def function(self, text: str):
        return to_date_str(text)


class QuestionNum19(Conversion):
    name = "Colorectal.macro.invasion"
    reference = "Colorectal.micro.maxDegreeLocalInvasion/Colorectal.synthesisOverview.tumourStageT"
    ref_required_re = re.compile(r'pT4\w*', re.IGNORECASE)

    def function(self, text: str, ref: str):
        if not self.ref_required_re.findall(ref):
            return "NULL"
        return multiple_lookup_list(text,
                                    ['Bladder', 'Prostate', 'Vagina', 'Liver', 'Seminal vesicles', 'Ovary', 'Ureter',
                                     'Peritoneum', 'Uterus'])


class QuestionNum20(Conversion):
    name = "Colorectal.preAnalytic.newPrimary"

    def function(self, text: str):
        if "new" in text.lower():
            return "Yes"
        return "No"


class QuestionNum21(Conversion):
    name = "Colorectal.preAnalytic.newPrimaryDate"
    reference = "Colorectal.preAnalytic.newPrimary"

    def function(self, text: str, ref: str):
        if ref and ref != "NULL":
            return to_date_str(text)
        return "NULL"


class QuestionNum22(Conversion):
    name = "Colorectal.preAnalytic.recurrence"

    def function(self, text: str):
        if "recurren" in text.lower():
            return "Yes"
        return "No"


class QuestionNum23(Conversion):
    name = "Colorectal.preAnalytic.recurrenceDate"
    reference = "Colorectal.preAnalytic.recurrence"

    def function(self, text: str, ref: str):
        if ref and ref != "NULL":
            return to_date_str(text)
        return "NULL"


class QuestionNum24(Conversion):
    """TODO: I added rectum need to validate"""
    name = "Colorectal.preAnalytic.tumourLocation/Colorectal.macro.tumourSite"

    def function(self, text: str):
        return lookup_list(text, ['Cecum', 'Transverse colon', 'Sigmoid colon', 'Ascending colon', 'Splenic flexure',
                                  'Hepatic flexure', 'Descending colon', 'Rectum'])


class QuestionNum26(Conversion):
    name = "Colorectal.macro.tumourPerforation"

    def function(self, text: str):
        return lookup(text, {'Present': 'Yes', 'Not id': 'No', 'No id': 'No', 'Absen': 'No', 'Cannot be assess': 'NULL',
                             'no': 'No'}, not_found_result="NULL")


class QuestionNum27(Conversion):
    name = "Colorectal.micro.tumourType"

    def function(self, text: str):
        return lookup_list(text.replace('-', ' '), ['Signet ring cell adenocarcinoma', 'Signet ring cell carcinoma',
                                                    'High grade neuroendocrine carcinoma', 'Mucinous adenocarcinoma',
                                                    'No residual carcinoma', 'Adenocarcinoma', 'Medullary carcinoma',
                                                    'Squamous cell carcinoma'])


class QuestionNum28(Conversion):
    # TODO: require further validation (have some Intermediate grade)
    name = "Colorectal.micro.histologicalGrade"

    def function(self, text: str):
        return lookup(text.replace('-', ' '),
                      {'High': 'High', 'Low': 'Low', 'poor': 'High', 'undifferent': 'High', 'moderat': 'Low',
                       'well': 'Low'})


class QuestionNum30(Conversion):
    name = "Colorectal.preAnalytic.adherence"

    def function(self, text: str):
        if "adherent" in text:
            return "Yes"
        return "No"


class QuestionNum31(Conversion):
    name = "Colorectal.macro.depositNumber"

    def function(self, text: str):
        results = re.findall('\d+', text)
        if results:
            return results[0]


class QuestionNum32(Conversion):
    name = "Colorectal.micro.maxDegreeLocalInvasion/Colorectal.synthesisOverview.tumourStageT"
    pT_re = re.compile(r'(?:T)(\d[ab]?|x|X|is)')

    def function(self, text: str):
        match = self.pT_re.findall(text)
        if match:
            return 'pT' + match[0].replace('is', '0')


class QuestionNum33(Conversion):
    name = "Colorectal.synthesisOverview.tumourStageN"
    pN_re = re.compile(r'(?:p?N)(\d[ab]?|x)', flags=re.IGNORECASE)

    def function(self, text: str):
        match = self.pN_re.findall(text)
        if match:
            return 'pN' + match[0]


class QuestionNum34(Conversion):
    name = "Colorectal.micro.lymphNodesDetails.numExamined"
    num_re = re.compile(r'\d+')

    def function(self, text: str):
        match = self.num_re.findall(text)
        if match:
            return match[0]


class QuestionNum35(Conversion):
    name = "Colorectal.micro.lymphNodesDetails.numPos"
    num_re = re.compile(r'\d+')

    def function(self, text: str):
        match = self.num_re.findall(text)
        if match:
            if int(match[0]) > 0:
                return "Present"
            else:
                return "Absent"


class QuestionNum35(Conversion):
    name = "Colorectal.macro.distNonperitonCircumMargin"

    def function(self, text: str):
        return find_matching_sentences(text=text, term="margin", case_sensitive=False)


class QuestionNum37(Conversion):
    name = "Colorectal.preAnalytic.clinicalObstruction"

    def function(self, text: str):
        if 'obstruct' in text.lower():
            return "Present"


class QuestionNum39(Conversion):
    # TODO: can not find anything...
    name = "Colorectal.preAnalytic.stool"


class QuestionNum40(Conversion):
    # TODO: can not find anything...
    name = "Colorectal.macro.maligantTumorNumber"


class QuestionNum41(Conversion):
    # TODO: can not find anything...
    name = "Colorectal.macro.depositType"


class QuestionNum42(Conversion):
    # TODO: can not find anything...
    name = "Colorectal.macro.residualAdjacentAdenoma"


class QuestionNum42(Conversion):
    # TODO: unclear of correct answer
    name = "Colorectal.micro.hostLymphoidResponse"

    def function(self, text: str):
        return find_matching_sentences(text=text, term=r'lymph ?(?:\w+\s+)*(?:negative|positive)', case_sensitive=False)
