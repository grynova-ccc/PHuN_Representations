import numpy as np
import pandas as pd
from sklearn.manifold import TSNE
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

# Load the dataset
csv_file = 'methane-stats-features.csv'
df = pd.read_csv(csv_file)
print(df.columns)

image_features_df=df.drop(columns=['Name', 'process', 'mmol/g_uptake', 'mmol/g_working_capacity',
       'v/v_uptake', 'v/v_working_capacity', 'wt%_uptake',
       'wt%_working_capacity', 'selectivity', 'purity', 'ssp', 'afm',
       'filename', 'Crystalnet', 'likely topology'])

# Filter for top 5 most frequent 'likely topology' categories
top_categories = df['likely topology'].value_counts().nlargest(10).index
filtered_df = df[df['likely topology'].isin(top_categories)]

# Load image features
#image_features = np.load('image_features-methane-storage-datase_SingleNodes.npy')
filtered_image_features_df = image_features_df.loc[filtered_df.index]

# Filter image features to match the filtered DataFrame
# Ensure the order matches between `filtered_df` and `image_features` rows
#filtered_image_features = image_features[filtered_df.index]

# Ensure we have the same number of image features and labels after filtering
#if len(filtered_image_features) != len(filtered_df):
  #  raise ValueError("Mismatch between filtered image features and labels.")

# Encode labels as numeric for the filtered data
unique_labels = filtered_df['likely topology'].unique()
label_to_numeric = {label: idx for idx, label in enumerate(unique_labels)}
numeric_labels = [label_to_numeric[label] for label in filtered_df['likely topology']]

# Compute t-SNE
tsne = TSNE(n_components=2, perplexity=30, random_state=0)
tsne_results = tsne.fit_transform(filtered_image_features_df)

# Plotting
distinct_cmap = plt.get_cmap('tab20')
plt.figure(figsize=(8, 6))
scatter = plt.scatter(tsne_results[:, 0], tsne_results[:, 1], c=numeric_labels, cmap=distinct_cmap, marker='o')

# Legend
legend_labels = [mpatches.Patch(color=scatter.cmap(scatter.norm(label_to_numeric[label])), label=label) for label in unique_labels]
plt.legend(handles=legend_labels, title="Classes", bbox_to_anchor=(1.05, 1), loc='upper left')

# Titles and labels
plt.title('t-SNE Visualization (Top 10 Categories)')
plt.xlabel('t-SNE component 1')
plt.ylabel('t-SNE component 2')

# Save and display plot
plt.savefig('tsne_top10-p30_stats.png', bbox_inches='tight')
plt.show()

