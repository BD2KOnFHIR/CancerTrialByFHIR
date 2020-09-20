from pathlib import Path
import pandas as pd
from eval.Eval import ratios, load_dfs
from NLP.str_functions import resection_extent
import os
from eval.CalculateAnnotatorKappa import EXCLUDE_ANNOTATORS


DEBUG = False


IGNORED_Q = ('Eval.UDP', 'Eval.syn', 'PCN', 'Annotator', 'Q42: Residual adjacent adenoma', 'Q39: number of stools', 'Q40: Multiple primary malignant tumors', 'Q41: Deposits type')

work_dir = Path.home() / "Desktop/Cancer Project/CRF_Evaluation"

machine_crf_file = work_dir / 'Cancer_CRF_machine.tsv'
out_dir = work_dir / "results"
os.makedirs(out_dir, exist_ok=True)

ann_to_df = {}

gold = load_dfs(work_dir/'tsv')

machine = pd.read_csv(machine_crf_file, sep='\t', index_col=0, header=0, dtype=str,
                                                 keep_default_na=False)


machine.loc[:, 'Q16: Extent of resection'] = [resection_extent(i) for i in machine.loc[:, 'Q16: Extent of resection']]

machine.to_csv(str(machine_crf_file) + '.new', sep='\t', na_rep="NULL")



# evaluation columns
questions = [item for item in gold.columns if item not in IGNORED_Q]
patients = [int(p) for p in gold.index]

print(questions)
print(patients)


print('\t'.join("F1 precision recall TP FN FP TN question".split()))
for question in questions:
    # match only correct annotators for this question
    if question in EXCLUDE_ANNOTATORS:
        indexes = gold[gold["Annotator"].isin(EXCLUDE_ANNOTATORS[question]) == False].index
    else:
        indexes = gold.index
    if DEBUG:
        print('-'*20 + question + '-'*20)

    subpatients = list(gold.loc[indexes, 'PCN'])
    annotators = list(gold.loc[indexes, 'Annotator'])
    subpatients = [int(i) for i in subpatients]


    g1 = gold.loc[indexes, question]
    m1 = machine.loc[subpatients, question]

    if DEBUG:
        for ann, g, m in zip(annotators, g1, m1):
            (TP, FN, FP, TN) = ratios(gold_list=[g], machine_list=[m])
            if FN or FP:
                print('*'*20 + ' FP '*FP + ' FN '* FN +  '*'*20)


                print("Annotator:", ann)
                print("Response:", g)
                print("Prefilled:", m)


    (TP, FN, FP, TN) = ratios(gold_list=g1, machine_list=m1)


    try:
        recall = TP / (TP + FN)
        precision = TP / (TP + FP)
        F1 = 2.0 * precision * recall/ (precision + recall)

        print("\t".join([str(i) for i in [F1, precision, recall, TP, FN, FP, TN, question]]))
    except ZeroDivisionError:
        print("\t".join([str(i) for i in ["-", "-", "-", TP, FN, FP, TN, question]]))




