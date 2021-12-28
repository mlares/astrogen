from pipeline import *

with open('df4.pk', 'rb') as f:
    D = pickle.load(f)

# %%

source_dir_model = '../../data/interim/filters_model/'
source_dir_byeye = '../../data/interim/filters_byeye/'

# %%

TP, TN, FP, FN = 0, 0, 0, 0

for i in tqdm(D.index):
    auth = D.loc[i]
    p = get_papers_from_df(auth)
    N = len(p)
    fout_byeye = fnames(auth, source_dir_byeye, '.txt')
    fout_byidx = fnames(auth, source_dir_byeye, '.idx')
    fout_model = fnames(auth, source_dir_model, '.txt')

    nf = 0
    if isfile(fout_byeye):
        # read
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            # read filters from web pages
            f = open(fout_byeye, 'r')
            fltr_saved = [True if ll.strip()=='true' else False\
                          for ll in f.readlines()]
            # read sorting sequence
            idx = np.loadtxt(fout_byidx)
            idx = idx.astype(int32)

            # generate filter
            fltr = np.repeat(None, len(fltr_saved))
            for k, i in enumerate(idx):
                fltr[i] = fltr_saved[k]
            fltr_byeye = fltr

            nf += 1
    if isfile(fout_model):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            fltr_model = np.loadtxt(fout_model, dtype=bool)
            nf += 1

    if nf==2:

        tp = np.logical_and(fltr_byeye, fltr_model)
        tn = np.logical_and(np.logical_not(fltr_byeye),
                            np.logical_not(fltr_model))
        fp = np.logical_and(np.logical_not(fltr_byeye),
                            fltr_model)
        fn = np.logical_and(fltr_byeye,
                            np.logical_not(fltr_model))
        TP += sum(tp)
        TN += sum(tn)
        FP += sum(fp)
        FN += sum(fn)

        #print(auth.apellido)
        #for i, j, k in zip(fltr_model, fltr_byeye, fpl):
        #    print(f'{i:2}, {j:2}, {i and not j:2}, {k:2}')

        #print(len(fltr_model))
        #print(TP, TN, FP, FN)
        #print(tp, tn, fp, fn)
        #input()

# %% metricas

P = TP + FN    # real positives
N = TN + FP    # real negatives
PP = TP + FP   # predicted positives
PN = TN + FN   # predicted negatives

TPR = TP / (TP + FN)   # true positive rate, recall, sensitivity
ACC = (TP + TN)/(P+N)  # accuracy
FDR = FP / PP          # false discovery rate
FPR = FP / N           # false positive rate (false alarms)
F1 = 2*TP / (2*TP + FP + FN)

print(f'True Positive Rate: {TPR}')
print(f'Accuracy: {ACC}')
print(f'F1 score: {F1}\n')

print(f'False discovery rate, {FDR}')
print(f'False positive rate: {FPR}')


# %%
