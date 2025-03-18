import numpy as np
import pandas as pd
from sklearn import linear_model

reg = linear_model.LogisticRegression(penalty='l2', solver='liblinear')
df = pd.read_csv("lebron_draft_data.csv")
input = df.iloc[:, np.r_[6:31, 33]]
output = df.iloc[:, 35]

reg.fit(input, output)
r2 = reg.score(input, output)
print(r2)