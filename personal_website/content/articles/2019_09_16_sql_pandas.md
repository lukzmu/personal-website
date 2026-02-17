Title: Reading a database into Pandas
Date: 2019-09-16 10:00

Lately I had to connect to a Windows Server database quickly to perform some fast data analysis. I don’t know any faster way to do that but in Python and run it through Pandas. Today I will share how to connect to a database (in my case using `pymssql`) and read the data you want into a Pandas DataFrame. Enjoy!

First of all, we need to install `pymssql`. This can be done as easily as `pip install pymssql` when using pip or `conda install pymssql` when using Anaconda Python packages. If you want to use any other database package, you must know that Pandas supports SQLAlchemy connectable and DBAPI2 connections.

Once we imported our module, we can now use it in code!

```python
# Import data
import pymssql
import pandas as pd
```

We can throw our database strings into variables. Mind that the best way would be to read those from `ENV` variables, but for the purpose of this blog post, that would be an overkill.

```python
# Database access
DB_HOST       = 'Input database location'
DB_PASSWORD   = 'Input user password'
DB_USER       = 'Input user name'
```

Now, let’s create a connection to our database using the variables:

```python
conn = pymssql.connect(
    DB_HOST,
    DB_USER,
    DB_PASSWORD,
)
```

Now its the time to do some `SQL` work. You need to write whatever you want to get out of the database. In my case I’ll do a lazy example on getting all info about a `Note` from the database (Don’t try that at home… actually anywhere).

```python
sql = 'SELECT * FROM Notes'
```

Last step! Getting the data into a Pandas DataFrame. This is as simple as:

```python
result_df = pd.read_sql(sql , conn)
```

And voilla! You have your data exactly where you want it. But wait… there is more! What if you have a shitty server and you can’t just get a couple of million records in one go? Let’s try breaking this into chunks!

```python
chunksize = 500  # Make it as big as you want
chunks = []  # A list to store chunk DataFrames

# Mind the chunksize parameter
for chunk in pd.read_sql(sql , conn, chunksize=chunksize):
    chunks.append(chunk)

# Connect the chunks
full_df = pd.concat(chunks)
```

Good job, now you know how to connect to a database and read the data straight into Pandas!
