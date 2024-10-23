import numpy as np
import scipy as sp
import matplotlib.pyplot as plt
from matplotlib import cm
import pandas as pd
from sklearn.manifold import TSNE
import matplotlib.patches as mpatches
from matplotlib.colors import ListedColormap
import os

folder="smaller-dataset/"
directory = os.fsencode(folder)

clustering='SingleNodes'

image_features = np.load('image_features-SingleNodes.npy')

files=[]
for file in os.listdir(directory):
 filename = os.fsdecode(file)
 if filename.endswith(".cif"):
  files.append(filename)

print(files)

csv_file = 'all_topology_lists.csv'
df = pd.read_csv(csv_file)
print(df)
name_to_label = dict(zip(df['Name'], df['Crystalnet']))

labels = [name_to_label.get(file) for file in files]

unique_labels = list(set(labels))
print(unique_labels)

label_to_numeric = {label: idx for idx, label in enumerate(unique_labels)}

numeric_labels = [label_to_numeric.get(label, -1) for label in labels]  

tsne = TSNE(n_components=2, perplexity=1, random_state=0)  
tsne_results = tsne.fit_transform(image_features)

distinct_cmap = plt.get_cmap('tab20')  

plt.figure(figsize=(8, 6))
scatter = plt.scatter(tsne_results[:, 0], tsne_results[:, 1], c=numeric_labels, cmap=distinct_cmap, marker='o')

legend_labels = [mpatches.Patch(color=scatter.cmap(scatter.norm(label_to_numeric[label])), label=label) for label in unique_labels]
plt.legend(handles=legend_labels, title="Classes", bbox_to_anchor=(1.05, 1), loc='upper left')

plt.title('t-SNE Visualization')
plt.xlabel('t-SNE component 1')
plt.ylabel('t-SNE component 2')


plt.savefig(f'tsne_{clustering}.png', bbox_inches='tight')

plt.show()

