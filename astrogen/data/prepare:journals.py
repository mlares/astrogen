
# %%

fileD = '../../data/interim/SJR/Qs_saved_ordered2020.csv'
jname = []
jq = []
with open(fileD, newline='') as csvfile:
    s = csv.reader(csvfile, delimiter=';')
    for row in s:
        jn = row[1].lower()
        word_tokens = word_tokenize(jn)
        fname = [w for w in word_tokens if w not in stop_words]
        journalname = ' '.join(fname)

        cond = len(journalname)<40

        jname.append(journalname)
        jq.append(int(row[0]))

# %%

JNS = []

for i in tqdm(range(N)):
    x = D.iloc[i]
    p = get_papers_from_df(x)
    auth_Q = []
    cita_N = []

    for ip in p:
        jn = ip.pub.lower()
        word_tokens = word_tokenize(jn)
        fname = [w for w in word_tokens if w not in stop_words]
        sent1 = ' '.join(fname)
        journalname = sent1.replace('/', '')

        if journalname in q1_journals:
            Q = 1
        elif journalname in q2_journals:
            Q = 2
        elif journalname in q0_journals:
            Q = 0
        else:
            JNS.append(journalname)

# %%

print(len(JNS))
JNSs = set(JNS)
JNSl = list(JNSs)
len(JNSl)

# %%

# ver cuales estan

add_qs = []
add_jnames = []

for journalname in JNSl:
    print(journalname)
    s1m = 0
    s2m = 0
    assigned_journal = ''
    for j, q in zip(jname, jq):
        s1 = similar(j, journalname)
        s2 = jellyfish.jaro_winkler(j, journalname)
        if s1 > s1m and s2 > s2m:
            s1m, s2m = s1, s2
            Q = q
            assigned_journal = j
            if s1>0.99 and s2>0.99:
                break
    if s1m<0.92 or s2m<0.92:  # not close enough
        Q = 0

    add_jnames.append(journalname)
    add_qs.append(Q)

# %%

f = open('file.txt', 'w')

for q, n in zip(add_qs, add_jnames):
    f.write(f'{q}; {n}\n')
    

f.close()

