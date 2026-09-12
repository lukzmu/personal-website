Title: Predicting World of Warcraft item buyout prices
Date: 2020-06-17 10:00

Not long ago I posted a blog entry about analyzing World of Warcraft auction house data. Today I will focus on predicting prices for various raid consumables using PyTorch and Sklearn.

## Importing packages

We will start by importing a couple packages that we will use in the prediction process:

```python
import torch
import torch.nn as nn 
import torch.autograd as autograd 
from torch.autograd import Variable
import numpy as np
from sklearn import preprocessing
from sklearn.model_selection import train_test_split
```

## Creating features and target

Let's recap what columns we had in our World of Warcraft dataframe:

```bash
<class 'pandas.core.frame.DataFrame'>
Int64Index: 44702 entries, 305 to 45163
Data columns (total 7 columns):
 # Column Non-Null Count Dtype         
-------- ------ -------------- -----         
 0 item_name 44702 non-null category      
 1 item_subclass 44702 non-null category      
 2 item_min_buyout 44702 non-null float64       
 3 item_quantity 44702 non-null int64         
 4 item_num_auctions 44702 non-null int64         
 5 created_at 44702 non-null datetime64[ns]
 6 days_after_new_raid 44702 non-null int64         
dtypes: category(2), datetime64[ns](1), float64(1), int64(3)
memory usage: 2.1 MB
```

The following columns will be our features:

- `item_name`
- `item_subclass`
- `item_num_auctions`
- `days_after_new_raid`

And we want to predict the buyout price of an item:

- `item_min_buyout`

Let's create the features and target variables then:

```python
features = ['item_name', 'item_subclass', 'item_num_auctions', 'days_after_new_raid']
wow_features = wow_other[features]

wow_target = wow_other[['item_min_buyout']]
```

We will perform one hot encoding on the string columns:

```python
wow_features = pd.get_dummies(
    wow_features,
    columns=['item_name', 'item_subclass'],
)
```

And scale the continuous values to make the prediction better:

```python
wow_features[['item_num_auctions']] = preprocessing.scale(
    wow_features[['item_num_auctions']]
)
wow_features[['days_after_new_raid']] = preprocessing.scale(
    wow_features[['days_after_new_raid']]
)
```

## Create training and test data

Using sklearn function `train_test_split` we will divide our dataset into training and test subsets. The dataset will be divided into `80%` training data and `20%` test data. We will also set a random state of `42` for reproductability.

```python
X_train, x_test, Y_train, y_test = train_test_split(
    wow_features,
    wow_target,
    test_size=0.2,
    random_state=42,
)
```

To make use of the data, we need to convert it into torch tensors.

```python
X_train_tr = torch.tensor(X_train.values, dtype=torch.float)
x_test_tr = torch.tensor(x_test.values, dtype=torch.float)
Y_train_tr = torch.tensor(Y_train.values, dtype=torch.float)
y_test_tr = torch.tensor(y_test.values, dtype=torch.float)

# And we can display the sizes
display('X train size:', X_train_tr.shape)
display('Y train size:', Y_train_tr.shape)


OUTPUT
-----------
'X train size:'
torch.Size([33880, 24])
'Y train size:'
torch.Size([33880, 1])
```

## Defining the model

We will start by creating some initial variables that will store the model parameters. We want to set the input and output sizes, number of hidden layers, what loss function we will use and the learning rate.

```python
input_size = X_train_tr.shape[1]
output_size = Y_train_tr.shape[1]
hidden_layers = 100
loss_function = torch.nn.MSELoss()
learning_rate = 0.0001
```

Using the parameters we can create a Sequential torch model. We will run it with Linear transformations and a sigmoid activation function.

```python
model = torch.nn.Sequential(
    torch.nn.Linear(input_size, hidden_layers),
    torch.nn.Sigmoid(),
    torch.nn.Linear(hidden_layers, output_size),
)
```

## Training the model

The training of the model was done in 10k epochs. You can preview the code below:

```python
for i in range(10000):
    y_pred = model(X_train_tr)
    loss = loss_function(y_pred, Y_train_tr)

    if i % 1000 == 0:
        print(i, loss.item())

    model.zero_grad()
    loss.backward()

    with torch.no_grad():
        for param in model.parameters():
            param -= learning_rate * param.grad
```

## Using the model for predictions

Now that our model is trained we can predict some things. Let's start with a single sample item. I took the `1410th` item of the test set. Why 1410? It's the first number that came into my head as it is the well known in Poland date of Battle of Grunwald.

```python
sample = x_test.iloc[1410]

# Convert to tensor
sample_tr = torch.tensor(sample.values, dtype=torch.float)

# Do predictions
y_pred = model(sample_tr)
print(f'Predicted price of item is: {int(y_pred.item())}')
print(f'Actual price of item is: {int(y_test.iloc[1410])}')


OUTPUT
-----------

Predicted price of item is: 13
Actual price of item is: 24
```

We can also do predictions for the entire dataset and display it nicely on a graph!

```python
# Predict prices for entire dataset
y_pred_tr = model(x_test_tr)
y_pred = y_pred_tr.detach().numpy()

# Show the result on a graph
plt.scatter(y_pred, y_test.values, s=1)
plt.xlabel("Actual Price")
plt.ylabel("Predicted price")
plt.title("Predicted prices vs Actual prices")
plt.show()
```

As we can see, most predictions are close to what we expected with a couple of variations. With such a dynamic environment and constant price changing due to undercutting, reselling and price bumping, this is quite a nice outcome!
