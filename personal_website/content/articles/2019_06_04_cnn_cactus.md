Title: CNN aerial cactus classification
Date: 2019-06-04 10:00

Not long ago I decided to actually put my Kaggle account to use and have fun with one of the competitions that are posted there. My choice went to the Cactus Identification as an extension to a research project from Mexico. The description of the competition as taken from the competition website:

> To assess the impact of climate change on Earth’s flora and fauna, it is vital to quantify how human activities such as logging, mining, and agriculture are impacting our protected natural areas. Researchers in Mexico have created the VIGIA project, which aims to build a system for autonomous surveillance of protected areas. A first step in such an effort is the ability to recognize the vegetation inside the protected areas. In this competition, you are tasked with creation of an algorithm that can identify a specific type of cactus in aerial imagery.

The goal was to create a classifier capable of predicting whether an images contains a cactus. To tackle this problem I decided to use a Convolutional Neural Network (CNN) built with PyTorch. Let’s go through the steps that got me a score of 0.9996 in the leaderboard, while building my network from scratch. The network can probably be tweaked to receive higher scores, but ain’t nobody got time for that.

## Python imports

To make our project work, we need the following packages. I divided them into multiple sections, so that you know what package is imported for what purpose. This project is done in Python 3.7 under the Anaconda distribution.

```python
# Python imports
import os
from datetime import datetime

# Math imports
import numpy as np

# Data and plots imports
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import seaborn as sns

# Machine Learning imports
import torch
import torch.optim as optim
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import DataLoader, Dataset
import torchvision
import torchvision.transforms as transforms
from sklearn.model_selection import train_test_split
```

## Data investigation

The dataset contains a large number of `32 x 32` thumbnail images containing aerial photos of a columnar cactus (Neobuxbaumia tetetzo). Kaggle has resized the images from the original dataset to make them uniform in size. The file name of an image corresponds to its id, the labeling is `[0,1]` and describes, if a cactus is present in the given image. Project structure:

- `train/` - the training set images,
- `test/` - the test set images (for prediction),
- `train.csv` - the training set labels, indicates whether the image has a cactus,
- `sample_submission.csv` - a sample submission file in the correct format.

First I started with creating path variables and create the training DataFrame:

```python
test_path = '../input/test/test/'
train_path = '../input/train/train/'
train_df = pd.read_csv('../input/train.csv')

# Display head of the data
train_df.head()
```

| id | has_cactus |
| :-- | :-- |
| 0004be2cfeaba1c0361d39e2b000257b.jpg | 1 |
| 000c8a36845c0208e833c79c1bffedd1.jpg | 1 |
| 000d1e9a533f62e55c289303b072733d.jpg | 1 |
| 0011485b40695e9138e92d0b3fb55128.jpg | 1 |
| 0014d7a11e90b62848904c1418fc8cf2.jpg | 1 |


We can also see what are the values of the `has_cactus` column, so basically how many cactus are there in a cactus dataset. If you look below you can see that we have 13136 images with a cactus present… and 4364 without.

```bash
train_df['has_cactus'].value_counts()
----------
1    13136
0     4364
Name: has_cactus, dtype: int64
```

And what, if we want to see how our imageset actually looks like? Well no problem!

Let’s grab the first five images for science.

```python
# Create a list of images to display
images = [mpimg.imread(
    os.path.join(train_path, train_df.iloc[i,0])
) for i in range(0,5)]

# Display the images in 5 columns
plt.figure(figsize=(10,10))
columns = 5
for i, image in enumerate(images):
    plt.subplot(len(images) / columns + 1, columns, i + 1)
    plt.imshow(image)
```

## Preparing the data for use

To use our data for training, we need to prepare it first. We need to divide our image set into training and validation data. The validation data usally takes 20% of the whole set. This can be easily done with the `train_test_split` function `from sklearn.model_selection`.

```python
train, valid = train_test_split(
    train_df,
    stratify=train_df['has_cactus'],
    test_size=0.2
)
```

We will also apply some simple transforms. Nothing fancy. With the dataset we have, rotating, flipping or skewing images might not help at all.

```python
train_tf = transforms.Compose([
    transforms.ToPILImage(),
    transforms.ToTensor(),
])
valid_tf = transforms.Compose([
    transforms.ToPILImage(),
    transforms.ToTensor(),
])
```

We will be extending the `Dataset` class from pytorch utility classes. We need to override the `init`, `len` and `getitem` funtions. We want to pass in some labels, the data directory (to read images from) and a possible transform. Mind that we will only apply the transform, if there is one passed in the parameter.

```python
class CactusDataset(Dataset):
    def __init__(self, labels, data_dir, transform=None):
        super().__init__()
        self.labels = labels.values
        self.data_dir = data_dir
        self.transform = transform
    
    def __len__(self):
        return len(self.labels)
    
    def __getitem__(self, index):
        name, label = self.labels[index]
        img_path = os.path.join(self.data_dir, name)
        img = mpimg.imread(img_path)
        
        if self.transform is not None:
            img = self.transform(img)
        return img, label
```

Now we should put our newly created `CactusDataset` to work! Let’s create training and validations datasets, and pass the labels, paths and transforms.

```python
train_data = CactusDataset(
    labels=train,
    data_dir=train_path,
    transform=train_tf,
)
valid_data = CactusDataset(
    labels=valid,
    data_dir=train_path,
    transform=valid_tf,
)
```

## Network structure

To create our network we will extend the `nn.Module` class from PyTorch. The network is built from 3 convolutional, 2 pooling and 2 linear layers. The activation function that is used is `RELU`. All convolutions use a kernel size of `3`, while stride and padding is set at `1`. Pooling layers use a technique called MaxPooling meaning only the highest values will be passed as output (if you want to learn more about pooling, theres a lot of articles about that on google… don’t want to repeat all that). The convolution results are flattened and passed to 512 features, that are then assigned into one of two classes. Below you can see an image of the network and the code needed to replicate it.

```python
class Net(nn.Module):
    def __init__(self):
        super(Net, self).__init__()
        self.pool = nn.MaxPool2d(2, 2)
        self.conv1 = nn.Conv2d(
            in_channels=3,
            out_channels=16,
            kernel_size=3,
            stride=1,
            padding=1
        )
        self.conv2 = nn.Conv2d(
            in_channels=16,
            out_channels=32,
            kernel_size=3,
            stride=1,
            padding=1
        )
        self.conv3 = nn.Conv2d(
            in_channels=32,
            out_channels=64,
            kernel_size=3,
            stride=1,
            padding=1
        )
        self.lin1 = nn.Linear(64 * 8 * 8, 512)
        self.output = nn.Linear(512, 2)
    
    def forward(self, x):
        x = F.relu(self.conv1(x))
        x = self.pool(F.relu(self.conv2(x)))
        x = self.pool(F.relu(self.conv3(x)))
        x = x.view(-1, 64 * 8 * 8)
        x = F.relu(self.lin1(x))
        x = self.output(x)
        return x
```

## Training the model

Now this is where all the magic will happen. We will set out parameters, pick optimizers, create data loaders and run the training. Oh this is so exciting! We will begin by setting the hyperparameters. We will have `2` classes (because we can have a cactus in the picture or not), `20` epochs (my guess it will be enough) with a learning rate of `0.001`. We will also check if CUDA is available and select an appropriate device. I selected a batch size of `50`, since I think that the device should handle 50 images of training per batch.

```python
device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
n_epochs = 20
n_classes = 2
batch_size = 50
learning_rate = 0.001
```

Now we need to startup the model, add some criterion and pick an optimizer. We will use the Adam optimizer, since its a popular pick for such projects. I tried using other optimizers, but the results were weaker (adagrad, sgd). So let’s stick to that.

```python
model = Net().to(device)
criterion = nn.CrossEntropyLoss()
optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)
```

We need to create some data loaders for training and validation data we split earlier. We will shuffle the data for taining.

```python
train_loader = DataLoader(
    dataset=train_data,
    batch_size=batch_size,
    shuffle=True,
)
valid_loader = DataLoader(
    dataset=valid_data,
    batch_size=batch_size,
    shuffle=False,
)
```

And now comes the training part. It’s pretty standard. But since it is a longer piece of code, I placed comments on what is happening inside. We will run an iteration over the number of epochs, go through the images and labels and then evaluate the model at the end for each epoch. Once the training is done, we will have a list of results for display purposes and a great model.

```python
steps = len(train_loader)
results = []

for epoch in range(n_epochs):
    t_start = datetime.now()
    model.train()
    epoch_loss = 0
    
    for i, (images, labels) in enumerate(train_loader):
        images = images.to(device)
        labels = labels.to(device)
        
        # Forward pass
        outputs = model(images)
        loss = criterion(outputs, labels)
        
        # Backward and optimize
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        
        # Pass loss to outer loop
        epoch_loss += loss.item()
        
    epoch_loss = epoch_loss / len(train_loader)
    t_elapsed = datetime.now() - t_start
    
    # Model evaluation
    model.eval()
    correct = 0
    total = 0
    with torch.no_grad():        
        for images, labels in valid_loader:
            images = images.to(device)
            labels = labels.to(device)
            outputs = model(images)
            _, predicted = torch.max(outputs.data, 1)
            total += labels.size(0)
            correct += (predicted == labels).sum().item()
            
    # Calculate accuracy
    epoch_acc = correct / total
    
    # Save results for display
    results.append({'Epoch': epoch+1, 'Loss': epoch_loss, 'Accuracy': epoch_acc})
        
    # Print out epoch data
    print ('Epoch [{:0>2d}/{}], Loss: {:.4f}, Accuracy: {:.4f}, Epoch Time: {}'.format(
        epoch+1, n_epochs, epoch_loss, epoch_acc, t_elapsed,
    ))
```

## Conclusion

Let’s visualize the data we got from training. I will put the stuff into a pandas DataFrame (as I really like using them) and then display it using seaborn in a simple plot of Loss and Accuracy. As we can see below, the training went quite well. I’m quite sure we can still tweak the hyperparameters or other aspects of the network for better results, but what we got here is quite good. In general using CNN for such projects gives great results, as we can dig deeper into the features of the images for better classification. Why don’t you try out building a CNN network using PyTorch yourself on Kaggle so we can compare results!

```python
# Store validation results in a DataFrame
results_df = pd.DataFrame(results)
results_df.set_index('Epoch', inplace=True)
results_df.head()

# Display validation results on graph
fig, ax =plt.subplots(2,1)
sns.lineplot(data=results_df, x=results_df.index, y='Loss', ax=ax[0])
sns.lineplot(data=results_df, x=results_df.index, y='Accuracy', ax=ax[1])
fig.show()
```
