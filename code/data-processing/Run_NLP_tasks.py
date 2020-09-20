import pandas as pd
from numpy import percentile
from NLP import ConversionTasks
import inspect

# get NLP conversion tasks
members = inspect.getmembers(ConversionTasks, inspect.isclass)
tasks = [cls_() for (name_, cls_) in members if name_ != "Conversion"]
print(f"{tasks=}")

# load data and create copy for output
df = pd.read_csv("cancer_CRF.tsv", sep='\t', index_col=0, header=0, dtype=str, keep_default_na=False)
df_out = df.__deepcopy__()

# drop columns
del df_out['Eval.syn']
del df_out['Eval.UDP']


for task in tasks:
    col, ref = task.get_name(), task.get_ref()

    if task.num_args() == 1:
        debug_print_len = percentile([len(i) for i in df[col]], 95)
    else:
        debug_print_len = percentile([len(i) + len(j) for i, j in zip(df[col], df[ref])], 95)
    task.set_debug_delim(debug_print_len + 3)

    # run task
    print(task)
    df_out[col] = [task(input_, ref_) for (input_, ref_) in zip(df[col], df[ref])]


df_out.to_csv("cancer_CRF_NLP_output.tsv", sep='\t', na_rep="NULL")


