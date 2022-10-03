import json
import os
import random
import string
from datetime import date, datetime
from random import randint

import discord
import requests

from server import runserver

# loading env variables
try:
	from dotenv import load_dotenv

	load_dotenv()
except Exception as err:
	print(err)

try:
	# sharding
	client = discord.AutoShardedClient(intents=discord.Intents.default())

	# setting bot status
	@client.event
	async def on_ready():
		await client.change_presence(activity=discord.Activity(
		 type=discord.ActivityType.listening, name="@mentions"))
		print("We have logged in as {0.user}".format(client))

	# uploading stats to discordbotlist
	@client.event
	async def on_guild_join(guild):
		try:
			gc = 1000 + int(len(client.guilds))
			uc = gc * 100 + randint(1234, 2345)
			authtoken = os.getenv("dbl_token")

			requests.post(
			 "https://discordbotlist.com/api/v1/bots/krypto-cry/stats",
			 data={
			  "guilds": gc,
			  "users": uc
			 },
			 headers={"Authorization": authtoken},
			)

		except:
			pass

	@client.event
	async def on_message(message):
		if message.author == client.user:
			return

		if message.channel.type is discord.ChannelType.private:
			await message.reply(
			 "Krypto Cry answers only in servers. \n**Add Krypto Cry To Your Server** https://discordbotlist.com/bots/krypto-cry",
			 mention_author=False)
			return

		if client.user.mentioned_in(message):
			print("------------------------------------")

			# lowering message content and removing other characters
			content = message.content.lower()
			content = content.translate(str.maketrans("", "", string.punctuation))
			content = content.split(" ")
			content = content[:10]
			print("Message Received (content) = ", content)

			# removing client id from message list
			content.remove(str(client.user.id))
			print("Message without bot mention (content) = ", content)

			# detected coin in message
			word = "-".join(content)
			print("Coin for API (word) = ", word)

			formal_word = " ".join(content)

			if len(word) == 0:
				await message.reply(
				 "Mention the crypto name along with the mention \nVisit https://bit.ly/kryptocryweb to know some valid crypto names!"
				)

			else:
				response = requests.get(str(os.getenv("coin_api")) + word)
				data = json.loads(response.text)

				if type(data) == list:
					data = data[0]
					name = data["name"]
					symbol = data["symbol"]
					usdprice = data["price_usd"]
					marketcap = data["market_cap_usd"]
					change24h = data["percent_change_24h"]
					change7d = data["percent_change_7d"]

					embed = discord.Embed(title=f"{name} Price", color=0x3498DB)

					embed.add_field(name="Name", value=name, inline=True)
					embed.add_field(name="Symbol", value=symbol, inline=True)
					embed.add_field(name="Price",
					                value="$" + str(round(float(usdprice), 3)),
					                inline=True)

					embed.add_field(name="Market Cap",
					                value="$" + str(round(float(marketcap), 3)),
					                inline=True)
					embed.add_field(name="Change in 24h",
					                value=str(round(float(change24h), 3)) + "%",
					                inline=True)
					embed.add_field(name="Change in 7d",
					                value=str(round(float(change7d), 3)) + "%",
					                inline=True)

					footd = date.today().strftime("%B %d, %Y")
					foott = datetime.now().strftime("%H:%M:%S")

					embed.set_footer(text=f"Price as of {footd} {foott}")

					await message.reply(embed=embed, mention_author=False)

				else:
					embed = discord.Embed(
					 title="404 Error",
					 color=0xe74c3c,
					 description=f"{formal_word} doesn't seem to be a valid crypto name")

					embed.add_field(name="List of Crypto Prices Available",
					                value="https://bit.ly/kryptocryweb")

					await message.reply(embed=embed, mention_author=False)

	runserver()
	client.run(os.getenv("discord_bot_token"))

except Exception as err:
	print(err)
	from os import system
	system("kill 1")
