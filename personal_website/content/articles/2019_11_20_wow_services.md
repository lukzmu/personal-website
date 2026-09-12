Title: Data gathering service using Flask: Services and Scheduling
Date: 2019-11-20 10:00

As a big fan of World of Warcraft, I always wanted to do a little side-project about auction house price predictions. When searching the web for data, I didn’t find any useful data source tho, so I decided to create one myself. With the help of TradeSkillMaster API and some Flask code, I started gathering the data I need in a MySQL database… and today I will show you how to do something similar for your own needs.

This blog post, due to the amount of information, comes in a series:

- [Data gathering service using Flask: Structure and Data]({filename}2019_11_18_wow_data.md)
- Data gathering service using Flask: Services and Scheduling
- [Data gathering service using Flask: Heroku deployment]({filename}2019_11_22_wow_heroku.md)

## Building our services

Now that we have our application structure and database model created, we can jump into the core functionality of our data gathering service. Let’s start by updating the following line in our `__init__.py` file to import some services in:

```python
# Was like this
from app import routes, models  # noqa

# Change to this
from app import routes, models, services  # noqa
```

Ok great. So the next obvious step is to actually create the service! Create a new file called `services.py` and add the following imports:

```python
from datetime import datetime
import requests
from .models import TSMData  # or whatever you called this
```

Let’s create a new function called `gather_tsm_data(app, db)`. We want to pass our Flask app and the database connection as parameters, to make things easier. This function will do three things step by step:

- Gather data from the TSM API,
- Filter the data based on our `ITEMS_FILTER` (check previous blog post),
- Save the data into our database.

### Gathering the data

We are using the `requests` library for getting data over http. This is one of the most popular pieces of code out there, so you might already be familiar with it. We will get our API key from the config file (by accessing `app.config`), send a GET request to the API, while passing two parameters (`format` and `apiKey`) and then get the data into json format. Moreover, you can notice the `raise_for_status()` function - this will give us the option to throw exceptions when the status code isn’t `200`.

```python
api_key = app.config['TSM_API']
response = requests.get(
    f'http://api.tradeskillmaster.com/v1/item/EU/Tarren-Mill',
    params={
        'format': 'json',
        'apiKey': api_key,
    },
)
response.raise_for_status()
data = response.json()
```

### Filtering

As for filtering, in my case the step is quite simple. You can do more complicated things, depending on your models and your API, but for gathering Warcraft information this will suffice:

```python
item_ids = app.config['ITEMS_FILTER']
data = [item for item in data if item['Id'] in item_ids]
```

### Saving data

For each item we want to save, we want to add this to the session - will always be better to save them in bulk. To do this, we use the `db.sessions.add` function in a for loop, adding the created database object as a parameter. Then, once we added everything we want to the session, we can just run `db.session.commit()` to save everything in one go.

```python
for item in data:
    tsm_object = TSMData(
        item_name=item['Name'],
        item_subclass=item['SubClass'],
        item_vendor_buy=item['VendorBuy'],
        item_vendor_sell=item['VendorSell'],
        item_market_value=item['MarketValue'],
        item_min_buyout=item['MinBuyout'],
        item_quantity=item['Quantity'],
        item_num_auctions=item['NumAuctions'],
    )
    db.session.add(tsm_object)
db.session.commit()
```

### Final saving service

The code for the service should look somewhat like this:

```python
def save_tsm_data(app, db):
    try:
        # Get data from TSM
        api_key = app.config['TSM_API']
        response = requests.get(
            f'http://api.tradeskillmaster.com/v1/item/EU/Tarren-Mill',
            params={
                'format': 'json',
                'apiKey': api_key,
            },
        )
        response.raise_for_status()
        data = response.json()

        # Filter for items of interest
        item_ids = app.config['ITEMS_FILTER']
        data = [item for item in data if item['Id'] in item_ids]

        # Save items to the database
        for item in data:
            tsm_object = TSMData(
                item_name=item['Name'],
                item_subclass=item['SubClass'],
                item_vendor_buy=item['VendorBuy'],
                item_vendor_sell=item['VendorSell'],
                item_market_value=item['MarketValue'],
                item_min_buyout=item['MinBuyout'],
                item_quantity=item['Quantity'],
                item_num_auctions=item['NumAuctions'],
            )
            db.session.add(tsm_object)
        db.session.commit()
        app.logger.info(f'🤩  Added TSM data at {datetime.now()}')
    except Exception as ex:
        app.logger.error(f'🤬  Error occured: {ex}')
```

### Small hacky function for Heroku

We want to build one more function in `services.py`, just because we want to host our app on a free Heroku dyno. The purpose of this request, will be to ping our service, to keep Heroku from shutting down, for being idle. Just copy-paste this, and enter the host of your Heroku service:

```python
def self_ping():
    # To prevent Heroku for going idle
    requests.get(
        'https://wow-data-gather.herokuapp.com/',
    )
```

## Scheduling requests

To make scheduling happen, we will use the well-known library `APScheduler`. To implement the functions we need to go back to the `__init__.py` file of our service. We already imported the `BackgroundScheduler`, so we can create the functionality (add it at the end of the file):

```python
scheduler = BackgroundScheduler({
    'apscheduler.timezone': 'UTC',
})
```

It is good practice to use `UTC` time for anything date related for such projects, to be localization invariant. Now that we have our scheduler, we only need to start the jobs!

```python
scheduler.add_job(
    services.save_tsm_data,
    args=[app, db],
    trigger='interval',
    hours=1,
    id='save_tsm_data',
    replace_existing=True,
)
```

There are a few things worth noticing. We need to pass a `trigger` for it to run every hour. This also means that the first time it runs will be 1 hour (becasue `hours=1`) from when you start the server. We also need to add both the `id` and `replace_existing=True`, so that you won’t get duplicate schedules.

Let’s add the scheduler for the *“Heroku problem”* as well:

```python
scheduler.add_job(
    services.self_ping,
    trigger='interval',
    minutes=1,
    id='self_ping',
    replace_existing=True,
)
```

Once we have that done, we can start the scheduler as follows:

```python
scheduler.start()
```

When having this in `__init__.py` this will start every time the server is run. That’s really neat.
