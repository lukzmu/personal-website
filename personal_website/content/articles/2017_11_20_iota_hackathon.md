Title: IOTA Hackathon
Date: 2017-11-20 10:00

This weekend was an adventure! I went to Gdańsk to participate in the **IOTA Hackathon** – 2 days of intense Internet of Things + Blockchain (but not really) hacking action with a team of great and creative people from all over Europe. The event was sponsored by a couple of companies: IOTA, Baltic Data Science, Datarella, Crowdstart Capital and Bright Inventions. But what is IOTA and how it actually works? How did the event go? What we created? Let’s find out!

If you want more news about the event, check the `#iotahack` on social media.

## So do tell me… what is IOTA?

> As the Internet-of-Things keep expanding, the need for interoperability and sharing of resources become a necessity. IOTA enables companies to explore new business-2-business models by making every technological resource a potential service to be traded on an open market in real time, with no fees.

~ Taken from IOTA website

IOTA is taking the blockchain technology to the next level with introducing the Tangle. In theory it allows you to send fast micro-transactions between users, while keeping a secure environment. Allowing value 0 transactions makes it perfect for P2P messaging and makes it a great way to communicate between IoT devices.  I’m not an expert on the subject, so I won’t go into technical details, but here are some main features of IOTA:

- Micro-transactions
- Data transfer
- Voting
- Masked messaging
- Everything as a Service
- Scalable Ledger

If you are interested in the subject of “how it works” you might want to see the IOTA Whitepaper.

## PlugInBaby – Hackathon first place

I was part of the **PlugInBaby** team that won the Hackathon. After 24h we provided a working solution for a distributed electric car charging system using the IOTA tangle. My main task was to connect our system with the python IOTA APIs, which worked out quite well thanks to the great support of IOTA people on Slack (that were there for us for the whole weekend).

**PlugInBaby** allows vendors to add their charging stations to our system with a specified name, location and charging cost. The payments they receive are done by IOTA tangle transactions and depend on how long the client was charging their car.

The client on the other hand gets a mobile app, that shows him the positions of nearby charging stations. Each station is marked green or orange, depending on their curent status: Free or Occupied. Once he selects which price fits him the best, he moves to the charging station and plugs the car in. Once he approves the charging request, the action begins and goes until canceled or battery is fully charged. Then the payment is issued and he can move on.

## How it works?

As I said before, I was responsible for the backend. I’ll show you how accessing the tangle works and some of the methods that were used to create this application. You can view the full code on Github. We were doing everything on the test network, so if you want to get your adress, seed and test IOTA tokens, please go visit the generator site. You can also use the Tangle Explorer to see, if your transactions are actually working. The code I post here will be simplified, so you need to catch exceptions and stick it into functions yourself (or check our Github repo).

On how to install IOTA lib for python go to the official IOTA python repo.

### Testnet nodes:

- http://p103.iotaledger.net:14700
- https://testnet140.tangle.works:443
- http://p101.iotaledger.net:14700

### Testing the connection

First of all, we need to create an Iota object and pass it one of the Testnet nodes and our generated seed. Then we can use the `get_node_info()` function to read some data about the node we connected to – hash, neighbours etc.

```python
api = Iota(url, seed)
node_info = api.get_node_info()
logger.info("Node information: {info}".format(info=node_info))
```

### Transactions

To send a transaction (doesn’t matter if it will be free or paid), we need to use the `send_transfer()` function. Here is a short description of the variables:

- `depth` –  how deep to go in the Tangle
- `transfers` – the transactions you want to send:
     - `address` – address of your recepient,
     - `value` – how many IOTAs you want to send,
     - `message` – message you want to attach,
     - `tag` – well… a tag. Helps you find your transactions.
- `inputs` – your data and options:
    - `key_index` – we actually couldn’t figure that out, but 0 always worked,
    - `security_level` – at least 2 if you want to send value > 0.

```python
api.send_transfer(
    depth=3,
    min_weight_magnitude=16,
    transfers=[
        ProposedTransaction(
            address=Address("RECEPIENTSADDRESS"),
            value=0,
            message=TryteString.from_string("Hello world!"),
            tag=TryteString.from_string("MyTag")
        )
    ],
    inputs=[Address("YOURADDRESS", key_index=0, security_level=2)]
)
```

## Get your balance

To display the wallet we used the `get_balances()` function. You just need to pass the address.

```python
response = self.__api.get_balances([Address(address)])
logger.info(
   "Wallet balance: {balance}".format(balance=response["balances"][0])
)
```
