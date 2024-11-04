import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import numpy as np


file_path = 'methane-entropy-RACS-features.csv'  
df = pd.read_csv(file_path)
print(df)
print(df.columns)

#X = df.loc[:, df.columns.str.startswith("entropy_feature_")]

X=df.drop(columns=['Name','DB_num','order_f-lig','bool_f-lig','order_mc',
'bool_mc','order_func', 'bool_func', 'order_lc','bool_lc', 'mmol/g_uptake'])

#X = X.drop(columns=X.columns[X.columns.str.startswith("image_feature_")])

print(X.columns)

y = df['mmol/g_uptake']  

# Perform train/test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Initialize and train a Decision Tree regressor model
model = DecisionTreeRegressor(random_state=42)
model.fit(X_train, y_train)

# Make predictions on the test set
y_pred = model.predict(X_test)

# Evaluate the model
rmse = np.sqrt(mean_squared_error(y_test, y_pred))
mae = mean_absolute_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)

# Output results
print("Decision Tree Regression Model Evaluation:")
print("Root Mean Squared Error (RMSE):", rmse)
print("Mean Absolute Error (MAE):", mae)
print("R^2 Score:", r2)
