import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
import joblib
print("starting program wahoo")
#Load the data
data = pd.read_csv("asl_dataset.csv", header=None)

#First column = labels, rest = features
X = data.iloc[:, 1:].values
y = data.iloc[:, 0].values

#Split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

#Train
clf = RandomForestClassifier(n_estimators=200, random_state=42)
clf.fit(X_train, y_train)

print("Model trained. Accuracy:", clf.score(X_test, y_test))

#Save ya model
joblib.dump(clf, "asl_letter_model.pkl")
