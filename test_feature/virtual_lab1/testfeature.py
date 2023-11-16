import cv2
import numpy as np
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
import pandas as pd

# INPUT DATA
Input_RGB_Image = cv2.imread("C:\\Users\\carl1\\OneDrive\\Bureau\\CESI\\stage\\web\\v0.3\\testpy\\6-12mm_Red_Samsung_Perso_12MP.png")[..., ::-1]
Input_BW_Image = Input_RGB_Image[:, :, 0]
n_Colors = 2

colors = [
    [0, 0, 0],
    [0, 0, 1],
    [0, 1, 1],
    [0, 1, 0],
    [1, 1, 0],
    [1, 0, 0],
    [1, 1, 1],
    [1, 0, 1]
]

X, Y, _ = Input_RGB_Image.shape

# VARIABLES
Stack = np.zeros((X, Y, 4), dtype=np.float32)
Surface_Area = np.zeros(n_Colors)
Cluster_Name = [""] * n_Colors

# CALCULATIONS
Edge_BSE_Image = cv2.Canny(Input_BW_Image, 100, 200) / 255.0
Edge_Smoothed_BSE_Image = cv2.GaussianBlur(Edge_BSE_Image, (0, 0), 1)

Transformed_RGB_Image = Input_RGB_Image / 255.0

Stack[:, :, :3] = Transformed_RGB_Image
Stack[:, :, 3] = Edge_BSE_Image

pixels = Transformed_RGB_Image.reshape((-1, 3))
kmeans = KMeans(n_clusters=n_Colors, n_init=3).fit(pixels)
pixel_labels = kmeans.labels_.reshape(X, Y)

masks = [pixel_labels == i for i in range(n_Colors)]
clusters = [Input_RGB_Image * mask[:, :, np.newaxis] for mask in masks]
areas = [np.mean(mask) for mask in masks]

for i, area in enumerate(areas):
    Surface_Area[i] = 100 * area
    Cluster_Name[i] = f"Cluster {i+1}"

Matrix = np.zeros((X, Y, 3, n_Colors))

for s in range(3):
    for i in range(n_Colors):
        Matrix[:, :, s, i] = masks[i] * colors[i][s]

RGB_Clusters = np.sum(Matrix, axis=3)

# Create table using pandas
T = pd.DataFrame({
    'Cluster_Name': Cluster_Name,
    'Surface_Area': Surface_Area
})

print(T)

# FIGURES
plt.figure(1)
plt.imshow(Input_RGB_Image)
plt.title('Input RGB Image')

plt.figure(2)
plt.imshow(Input_BW_Image, cmap='gray')
plt.title('Input BW Image')

plt.figure(3)
plt.imshow(RGB_Clusters)
plt.title('RGB Clusterized image')

plt.figure(4)
plt.imshow(Edge_BSE_Image, cmap='gray')
plt.title('Edge Detection')

plt.figure(5)
plt.imshow(Edge_Smoothed_BSE_Image, cmap='gray')
plt.title('Smoothed Edge Detection')

plt.show()