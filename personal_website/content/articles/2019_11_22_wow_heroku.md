Title: Data gathering service using Flask: Heroku deployment
Date: 2019-11-22 10:00

As a big fan of World of Warcraft, I always wanted to do a little side-project about auction house price predictions. When searching the web for data, I didn't find any useful data source tho, so I decided to create one myself. With the help of TradeSkillMaster API and some Flask code, I started gathering the data I need in a MySQL database... and today I will show you how to do something similar for your own needs.

This blog post, due to the amount of information, comes in a series:

- [Data gathering service using Flask: Structure and Data]({filename}2019_11_18_wow_data.md)
- [Data gathering service using Flask: Services and Scheduling]({filename}2019_11_20_wow_services.md)
- Data gathering service using Flask: Heroku deployment

## Deploying on Heroku

Log into Heroku and press `Create New App`. You will see the below screen. Name your app the way you want and select a region that is closer to you (US and Europe are available). Additionally you can add a pipeline (although for a simple project like this, it isn't required).

You will be moved to the Application Dashboard. There select the `Settings tab`. Now look for the header Config Vars and press the corresponding button - `Reveal Config Vars`.

We need to add the following keys:

| Key | Value |
| :-- | :-- | 
| `SQLALCHEMY_DATABASE_URI` | In format: mysql://user:pass@host/db | 
| `TSM_API` | Your TSM API key, or any other API you are using | 
| `WEB_CONCURRENCY` | 1 |

The first two are obvious... but what the hell is `WEB_CONCURRENCY`? Well this is a solution to a problem that came on the way, while developing this flask service. Without this setting, the application was run twice, so we had twice the schedulers, so also duplicated database rows.

Once this is done, we can push our service to Heroku. We need to take the following steps:

1. Download and install Heroku CLI for your system,
2. Go into the root directory of your project,
3. Do one of the following:

If you didn't push your code to git yet:

```
git init
heroku git:remote -a your-awesome-app
git add .
git commit -am "add my awesome data gathering service"
git push heroku master
```

If you already pushed your code to git:

```
heroku git:remote -a your-awesome-app
```
So, we pushed our server and it is deployed, so basically we are done! But what, if we wanted to check the logs of our service to see whether everything is all right? Use the following command:

```
heroku logs --app your-awesome-app --tail
```
