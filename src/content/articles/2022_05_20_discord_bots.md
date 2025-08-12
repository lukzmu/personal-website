Title: Discord bots in Python
Date: 2021-05-20 10:00
Status: draft

In the last couple of years, we have experienced a shift in the way people work and study. We can see this movement on the job market - many offers related to IT are tagged 100% remote, allowing people to work with peers from all around the world. This is why such applications as Slack, Microsoft Teams, or Discord increased in popularity and are used by many people on a daily basis. Today we will focus on Discord - a means of communication that rose from a gaming tool to a platform that is used by professionals, educators, and communities.

The more co-workers use your tool, the bigger responsibility you have to keep everything in line. You can either hire more and more moderators... or you could use the tech knowledge your developer team has to create bots that will do the dirty work for you. In this blog post, I will go through the necessary knowledge to create and run a Discord bot that will communicate with external APIs to provide information on demand.

After reading through this tutorial, you will learn a few tactics useful for having more effective online communications in Discord:

- How to create a Discord bot,
- How to access information about the server,
- How to contact external services using commands,
- How to create Embeds.

## Requirements

To get the most out of this tutorial, I encourage you to complete the following steps:

1. Python 3.10 (you can use a lower version, if you want to skip match-case),
2. [Create a Discord account](https://discord.com/register),
3. [Create a test server](https://support.discord.com/hc/en-us/articles/204849977-How-do-I-create-a-server-),
4. Get ready for a coding adventure!

## Understanding the connection

Before we start coding, let's take a minute to understand how the communication works between your team server, Discord, your bot, and any other services you want to use.

Everything starts with your team server - this is how people interact with each other and artificial entities like bots. Each interaction can trigger the bot to do something - it can be done by special commands or an event sent by the server. Sample events can include:

- Sending a message by a user,
- New member joining the server,
- Creating a new channel,
- and many... many more!

If a bot is connected to your team server, it will try to handle events that are of interest to it.

**Each bot needs to have a running Discord Client instance. This is how the bot contacts Discord servers and APIs to answer the team server requests.**

It is worth mentioning that a single bot can be connected to multiple servers. You can select, if you want that feature in the Discord bots’ settings (more about that later on).

Once the bot processes information sent by the team server, it can contact multiple external services for example:

- Your application Rest API,
- Machine Learning algorithms,
- Your company ERP system,
- and anything else that comes to mind!

Lastly, the information can be sent by the bot to the Discord API, so that the users are notified back on the event progress.

## Getting started

We will start by creating a Discord Application. This step is needed to enable Discord to verify your bot with the servers through a token you will acquire in the process. As a bonus, you will get a chance to customize your bot's appearance.

Go to your [Discord Developer dashboard](https://discord.com/login?redirect_to=%2Fdevelopers%2Fapplications) and click **New Application**.

![Create an application]({attach}../images/2025_05_20_discord_bots/creating-a-new-discord-application.png)

Congratulations! You created your first Discord Application 🥳. You will be welcomed by a screen that will allow you some customization. You can play around with the settings, but it isn't required for this tutorial.

In the menu section, you should see a button named **Bot**, please navigate to that section, once there, press **Add Bot** and agree to the prompt.

Turn on the following privileged gateway intents and click **Save**:

- Presence intent,
- Server members intent,
- Message content intent.


Now that you created the bot, please go to the OAuth2 section and select URL Generator:

- Set the bot scope,
- Set the Administrator permission.
- Copy the Generated URL.

![Bot scope]({attach}../images/2025_05_20_discord_bots/setting-the-bot-scope-and-administrator-permissions-in-discord.png)

Follow the copied url in a browser and add the bot to your server. We are ready to build our own piece of software now!

## And then there was code…

In this section, we will go through the steps of installing dependencies, configuring the project and writing the actual code. Please start your IDE of choice and create a new project.

### Installing dependencies

We will need the following packages to create our Discord bot:

- `discord.py` - the main package needed to communicate with Discord,
- `requests` - this will allow us to contact the sample API,
- `dotenv` - to load environment variables from a file.

First, create a new virtual environment to be used in this tutorial (if you don't know what virtual environments are, be sure to check out [Python documentation for creating virtual environments](https://docs.python.org/3/library/venv.html)):

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Now we are ready to install the dependencies:

```bash
pip install discord.py
pip install requests
pip install python-dotenv
```

### Project settings

We will start by creating an `.env` file (notice the "dot" at the start) in our project directory. We will make use of the token you copied from the Discord Developers site and the name of the server you created in the requirements for this tutorial.

```
DISCORD_TOKEN = your_token_goes_here
DISCORD_GUILD = your_server_name
```

Looks good! We are ready for the next step.

### Connecting the Discord client

Create a `main.py` file in the project directory and add the necessary imports that we will be using in this tutorial at the top:

```python
import os
from typing import Any
import discord
import requests
from dotenv import load_dotenv
```

Now, we will read the environment variables we added in the configuration file:

```python
load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
DISCORD_GUILD = os.getenv("DISCORD_GUILD")
```

The next step is to create the Discord client. We will make it fairly simple for now:

```python
class Client(discord.Client):
   def __init__(self, token: str, guild_name: str) -> None:
       super().init()

    self._token = token
    self._guild_name = guild_name

    def run(self, *args: Any, **kwargs: Any) -> None:
        super().run(self._token)
        client = Client(DISCORD_TOKEN, DISCORD_GUILD)
        client.run()
```

The code we just added gave us three outcomes:

- We created a `Client` class that inherits from the `discord.Client`,
- We stored the settings in the class parameters,
- We started our client using the run function.

If you run the `main.py` file, you should see the bot online on your server.

![Bot online]({attach}../images/2025_05_20_discord_bots/bot-on-the-server-upon-running-the-mainpy-file.png)

## Gathering basic information

The `discord.py` package gives us quite a few possibilities out of the box. We will start by creating an action when the bot goes online. Let's create a new function in the `Client` class:

```python
async def on_ready(self) -> None:
   self._guild = discord.utils.get(self.guilds, name=self._guild_name)
   await self._guild.text_channels[0].send("Hello World!")
```

We used the discord utils to get the guild by the name and sent a message to the main text channel. The next time you start your Python file, you should get an output like this:

![Bot online]({attach}../images/2025_05_20_discord_bots/python-file-output-message.png)

## Gathering information for the user

A command is a special message that the user can send to perform various bot tasks. We will start by creating a command that lists users that are currently online.

If you want to gather information about the users, we need to update the `__init__` function a bit. Be sure to add the following intent to the `Client` constructor:

```python
intents = discord.Intents.default()
intents.members = True
super().init(intents=intents)
```

We will override the default on_message to make it easier. If you want to go advanced, you can read about the [bot commands framework](https://discordpy.readthedocs.io/en/latest/ext/commands/index.html).

```python
async def on_message(self, message: discord.Message) -> None:
   match message.content:
       case "!members":
           members = [member.name for member in self._guild.members]
           await message.channel.send(f"Members: {members}")
```

Please notice that instead of displaying *"Łukasz"* the bot responded with *"Divinebanana"*. While confusing, the reason is that Łukasz is a nickname specific to this server. If you want to obtain the server user nickname instead, you should use `member.nick` instead of `member.name`.

## Connecting to external services

The greatest thing about Discord bots is that you are only limited to the programming language capabilities. I will show you how to contact a REST API through a bot command and then display the information in an embed, making it pretty.

First of all, let's add a new command to our `match` in `on_message` function:

```python
match message.content:
   case "!members":
       ....

   case "!highground":
       await self.high_ground()
```

Now, we just need to create the `high_ground` function in our `Client`:

```python
async def high_ground(self) -> None:
   try:
       response = requests.get("https://swapi.dev/api/people/10/")
       response.raise_for_status()
       data = response.json()
   except requests.HTTPError:
       return

    embed = discord.Embed(
    title=data.get("name"),
    description=data.get("url"),
    )
    embed.add_field(name="Height", value=data.get("height"))
    embed.add_field(name="Mass", value=data.get("mass"))
    embed.add_field(name="Hair Color", value=data.get("hair_color"))
    embed.add_field(name="Birth Year", value=data.get("birth_year"))
    embed.add_field(name="Eye Color", value=data.get("eye_color"))
    embed.add_field(name="Gender", value=data.get("gender"))
    await self._guild.text_channels[0].send(embed=embed)
```

We contacted the [Star Wars API](https://swapi.dev/) to gather information about Obi-Wan Kenobi, a Jedi Master and one of the greatest Jedi Generals during the Clone Wars. We also used another cool feature of Discord - Embeds. You can see the result of our operations below.

![Embed]({attach}../images/2025_05_20_discord_bots/creating-embeds-in-discord.png)

Embeds allow you to create rich objects that can contain media and data condensed in a structured fashion. Feel free to read more about Embeds in the [official Discord documentation](https://discord.com/developers/docs/resources/channel#embed-object).

## Summary

With the increased usage of online communication  tools like bots can increase your productivity for small and large-scale communities, whether it is work, education or hobby-related. As you could see, building such applications is not hard and can power up your server for you and your users.

If you want to learn more, be sure to check the links below:

- [Discord documentation](https://discord.com/developers/docs/intro) - all things related to the Discord Developer API,
- [discord.py code repository](https://github.com/Rapptz/discord.py) with the code repository for the package,
- [discord.py documentation](https://discordpy.readthedocs.io/en/latest/) - the documentation for the package.Thanks for reading!

Thanks for reading!