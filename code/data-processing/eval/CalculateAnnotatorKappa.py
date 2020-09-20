from sklearn.metrics import cohen_kappa_score
from pathlib import Path
import pandas as pd
from eval.Eval import Grouper
from statistics import mean
import os

# output 0: show kappa scores
# output 1: show differences
OUTPUT = 0

ANNOTATORS = {'Nansu', 'Daniel', 'Yue', 'Ming', 'Deepak', 'Sijia', 'Andrew'}

#
EXCLUDE_ANNOTATORS = {'Q16: Extent of resection': {'Nansu', 'Deepak', 'Yue', 'Sijia'},
                      'Q19: Site of pathologically Confirmed invasion': {'Andrew', 'Ming', 'Yue', 'Deepak', 'Sijia'},
                      'Q31: Number of deposits': {'Andrew'},
                      'Q32: Disease extent': {'Nansu'},
                      'Q43: Host lymphoid response': {'Nansu', 'Daniel', 'Andrew', 'Ming', 'Sijia'}}

# ensure all people listed in IGNORE are in ANNOTATORS
listed_annotators = set(i for q in EXCLUDE_ANNOTATORS.values() for i in q)  # join the sets
assert listed_annotators <= ANNOTATORS


def main():
    work_dir = Path.home() / 'Desktop/Cancer Project/CRF_Evaluation'
    data_dir = work_dir / 'tsv'
    patients_eval = work_dir / 'same_patients.txt'
    out_dir = work_dir / "results"
    os.makedirs(out_dir, exist_ok=True)

    ann_to_df = {}

    with open(patients_eval, 'r') as fp:
        patients = fp.read().splitlines()
        patients = [int(p) for p in patients]  # convert to ints
    print(patients)

    for annotator_file in data_dir.glob('*.tsv'):
        ann_to_df[annotator_file.stem] = pd.read_csv(annotator_file, sep='\t', index_col=0, header=0, dtype=str,
                                                     keep_default_na=False)

    # evaluation columns
    questions = [item for item in tuple(ann_to_df.values())[0] if item not in ('Eval.UDP', 'Eval.syn')]
    print(questions)

    results_matrices = {}
    for question in questions + ["averages"]:
        results_matrices[question] = pd.DataFrame(index=ann_to_df.keys(), columns=ann_to_df.keys())

    count = 1

    for question in questions[0:]:
        print('\n' + '*' * 40)
        print(question)
        print('*' * 40)

        g = Grouper()
        for ann1 in ann_to_df:
            for ann2 in ann_to_df:

                # # check if already answer:
                # if not pd.isnull(results_matrices[question].loc[ann2, ann1]):
                #     results_matrices[question].loc[ann1, ann2] = results_matrices[question].loc[ann2, ann1]
                #     continue

                # ignore if same person or either is in group of annotators to ignore for a question
                if question in EXCLUDE_ANNOTATORS and EXCLUDE_ANNOTATORS[question].intersection({ann1, ann2}) \
                        or ann1 == ann2:
                    results_matrices[question].loc[ann1, ann2] = '-'
                    continue

                resp1 = tuple(ann_to_df[ann1].loc[patients, question])
                resp2 = tuple(ann_to_df[ann2].loc[patients, question])
                labels = list(set(resp1) | set(resp2) | set(["NULL"]))

                # group proximal responses using similarity score
                resp1g = [g.find(item) for item in resp1]
                resp2g = [g.find(item) for item in resp2]

                # print(resp1)
                # print(resp1g)
                # print(resp2)
                # print(resp2g)
                # print(resp1== resp2, resp1g == resp2g)

                if OUTPUT == 1:
                    if resp1g != resp2g:
                        for a1, n1, a2, n2 in zip(resp1, resp1g, resp2, resp2g):
                            if n1 != n2:
                                print(f"{ann1:10s}: {repr(a1)}\n{ann2:10s}: {repr(a2)}")
                                print("")

                if set(resp1g) == set(resp2g):  # only 1 result and they are the same
                    results_matrices[question].loc[ann1, ann2] = 1
                else:
                    try:
                        kappa = cohen_kappa_score(resp1g, resp2g)
                        results_matrices[question].loc[ann1, ann2] = kappa
                        # print(kappa)
                    except Exception:
                        results_matrices[question].loc[ann1, ann2] = -1

        if OUTPUT == 0:
            print(results_matrices[question])

        results_matrices[question].to_csv(out_dir / f"{count}.tsv", sep='\t')
        count += 1

    # panel = pd.Panel(results_matrices)
    # print(f'Averages:\n{panel.mean(axis=0)}')

    # for k, v in results_matrices.items():
    #     print(v)

    for ann1 in ann_to_df:
        for ann2 in ann_to_df:
            matrix = [results_matrices[question].loc[ann1, ann2] for question in questions if
                      results_matrices[question].loc[ann1, ann2] != '-']

            try:
                avg = mean(matrix)
            except Exception:
                avg = '-'

            results_matrices["averages"].loc[ann1, ann2] = avg

    print("Averages")
    print(results_matrices["averages"])

    results_matrices["averages"].to_csv(out_dir / f"averages.tsv", sep='\t')


if __name__ == "__main__":
    main()
