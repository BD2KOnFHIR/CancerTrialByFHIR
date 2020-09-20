from fuzzywuzzy.fuzz import partial_ratio as pr, ratio
import operator
from pathlib2 import Path
import pandas as pd
from NLP.str_functions import unbreak



def similarity(prefilled: str, gold: str, required_ratio=50, required_pr=95, debug=False):
    if isinstance(prefilled, float) or isinstance(gold, float):
        return 100 * (prefilled == gold)
    prefilled, gold = unbreak(prefilled.strip(), unspaced=True), unbreak(gold.strip(), unspaced=True)
    this_pr = pr(prefilled, gold)
    this_ratio = ratio(prefilled, gold)
    if this_ratio >= required_ratio and this_pr >= required_pr:
        return this_pr
    if debug:
        print('-'*40)
        print(f"partial ratio: {this_pr}  simple ratio: {this_ratio}")
        print(f"prefilled: {prefilled} \ngold: {gold}")

    return 0




class Grouper:
    required_ratio = 50
    required_pr = 95

    def __init__(self):
        self.reset()

    def find(self, item:str):
        # find index if in system else add to system and return index
        # does not add similar item #2 just keeps using similar item #1

        try:
            item = float(item)
        except ValueError:
            pass


        index = self.get_index(item)
        if index >= 0:
            return index
        else:
            self.prior += [item]
            return len(self.prior) - 1


    def __contains__(self, item):
        return max(self.sim_gen(item)) >= self.required_pr

    def get_index(self, item):
        if item in self.prior:
            return self.prior.index(item)
        else:
            index, max_pr = max(enumerate(self.sim_gen(item)), key=operator.itemgetter(1))
            if max_pr >= self.required_pr:
                return index
        return -1

    def sim_gen(self, item):
        return (similarity(item, p, required_ratio=self.required_ratio, required_pr=self.required_pr) for p in self.prior)

    def reset(self):
        self.prior = ["NULL"] # set a default of null for no value


def ratios(gold_list, machine_list):
    """return tuple of numbers that correspond to the number of
     (TP, FN, FP, TN)
    """
    (TP, FN, FP, TN) = 0,0,0,0
    REQUIRED_PR = 95

    for g, m in zip(gold_list, machine_list):
        if g == "NULL":
            if m == "NULL":
                TN += 1
            else:
                FP += 1
        else:
            if m == "NULL" or similarity(m, g) < REQUIRED_PR:
                FN += 1
            else:
                TP += 1

    return (TP, FN, FP, TN)


def load_dfs(data_dir:Path) -> pd.DataFrame:
    df_list = []
    for annotator_file in data_dir.glob('*.tsv'):

        df_list.append(pd.read_csv(annotator_file, sep='\t', header=0, dtype=str,
                                   keep_default_na=False))
        # save name of annotator based on file name
        df_list[-1]["Annotator"] = str(annotator_file.stem)

        # add index col name
        df_list[-1].rename(columns={'Unnamed: 0': 'PCN'}, inplace=True)

    out_df = pd.concat(df_list, ignore_index=True)
    return out_df

def print_df(df):
    with pd.option_context('display.max_rows', None, 'display.max_columns', None, 'display.max_colwidth', 20, 'display.width', 2000):  # more options can be specified also
        print(df)

