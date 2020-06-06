# COVID GraphBot

Telegram COVID bot is intended to provide visual statistical information about Novel Coronavirus (2019-nCoV). It is written in Python with micro web-framework Bottle.


[Telegram bot](https://t.me/covid19_visual_bot) is deployed on [Zeit Now](https://zeit.co/now).


Source data is provided by [Johns Hopkins CSSE repository](https://github.com/CSSEGISandData/COVID-19) within [transformer](https://github.com/pomber/covid19)


#### Getting Started
To use this telegram bot, you need to set up API credentials in *.prefs* file.
```
token_prod=TOKEN_PROD // telegram bot token for production
token_debug=TOKEN_DEBUG // telegram bot token for debug mode
webhook_url=WEBHOOK // webhook url
```


![Preview-demo](/art/preview_demo.gif "Preview demo")

### Deploying From Your Terminal

You can deploy your new Now project with a single command from your terminal using [Now CLI](https://zeit.co/download):

```shell
$ now
```

Issues
------

If you find any problems or would like to suggest a feature, please
feel free to file an [issue](https://github.com/iglaweb/covid19_visual_bot/issues)
