import discord
import os
from discord.ext import commands
from redbot.core import checks
import asyncio
import time
import logging
import pathlib
import aiohttp
#Redv3 imports
from redbot.core import Config
from redbot.core import bank
import random

"""
Arcs Economy Cog Notes:

I use u and p a lot
u stands for unpacked
p stands for packed

To fix:

Get bot owner object
Fix the send_cmd_help(ctx)
--owner is refrenced as if it is a user name when it is an id--
--Still here needs to be introduced(?)--
--The embeds all need implimented. #em means the embed has been added--
--The currency name and/or emoji needs to be added.--
--The currency name/emoji needs to be implemented--

Make it to where *anyone* can use it

To be added:
Independent server settings
sell
gift list

c&p

emmsg = str()
			em = em(False, emmsg)
			await ctx.send(embed=em)
"""
class ArcsEconomy:
	def __init__(self, bot):
		self.bot = bot
		#config setup
		self.config = Config.get_conf(self, identifier= 31415)
		def_global = {
			#presets- Customizable
			"ColorSet": {'error': 0xff0000, 'ok' = 0x2e5090}
			"BetrollMultipliers": {'99': 10, '91': 3, '67': 2}
			"dropChance": 50
			"dropAmounts": {'min': 100, 'max': 200}
			"coin_symbol": 438267940094214144
			"minWaifuPrice": 1000
			"waifuGiftMultiplier": 1.0
			"items": {}
			"lvlroles": {} #{level: role.id}
			"xppermessage": 5
			"xpcooldown": 300
			"boostToggle": True
			"roles": {} #{role.name: cost}
			"minLeavebalance": 500
			"leaveChannelID": 93284396739604480

			#presets- Not yet Customizable
			"gifts": {'potato': 5, 'cookie': 10, 'bread': 20, 'lollipop': 30, 'rose': 50, 'beer': 70, 'taco': 85, 'loveletter': 100, 'milk':  125, 'pizza': 150, 'chocolate': 200, 'icecream': 250, 'sushi': 300, 'rice': 400, 'watermelon': 500, 'bento': 600, 'movieticket': 800, 'cake': 1000, 'book': 1500, 'cat': 2000, 'dog': 2001, 'panda': 2500, 'lipstick': 3000, 'purse': 3500, 'iphone': 4000, 'dress': 4500, 'laptop': 5000, 'violin': 7500, 'piano': 8000, 'car': 9000, 'ring': 10000, 'yacht': 12000, 'house': 15000, 'helicopter': 20000, 'spaceship': 30000, 'moon': 50000}
			"giftsUnicode":  {'potato': '🥔', 'cookie': '🍪', 'bread': '🥖', 'lollipop': '🍭', 'rose': '🌹', 'beer': '🍺', 'taco': '🌮', 'loveletter': '💌', 'milk': '🥛', 'pizza': '🍕', 'chocolate': '🍫', 'icecream': '🍦', 'sushi': '🍣', 'rice': '🍚', 'watermelon': '🍉', 'bento': '🍱', 'movieticket': '🎟', 'cake': '🍰', 'book': '📔', 'cat': '🐱', 'dog': '🐶', 'panda': '🐼', 'lipstick': '💄', 'purse': '👛', 'iphone': '📱', 'dress': '👗', 'laptop': '💻', 'violin': '🎻', 'piano': '🎹', 'car': '🚗', 'ring': '💍', 'yacht': '🛳', 'house': '🏠', 'helicopter': '🚁', 'spaceship': '🚀', 'moon': '🌕'}
			"boosts": {"1 hour XP boost": 2000, "1 day XP Boost": 20000, "1 hour coin boost": 3000, "1 day coin boost": 30000}

		}
		def_member = {
			"stillhere": True
			#I know the structure is ugly
			"waifuPrice": 0
			"waifus": {} #make waifus a dictionairy of {member.id: member.name}
			"owner": "Nobody" 
			"gifts": {}
			"divorces": 0
			"Alias": "the Lonely"
			"likes": "Nobody"
			"selfL": 0
			"changes": 0
			#but it is easier
			"level": 0
			"xp": 0
			"prevMsgTime": 0
			#than set_raw()
			"inventory": {}
			"activeBoost": {}
			"activation_time": 0
		}
		self.config.register_global(**def_global)
		self.config.register_member(**def_member)
		#now to move on to the normal self.vars
		self.symbol = None
		self.cname = None
		self.channel = None

#Settings and other shit
	#Let's ready up the bot real quick
	async def on_ready(self): #Ill have to fix this
		emojis = self.bot.emojis
		symID = await self.config.coin_symbol()
		chanID = await self.config.leaveChannelID()
		self.cname = await bank.get_currency_name()
		self.symbol = self.bot.get_emoji(symID)
		self.channel = self.bot.get_channel(chanID)
		if self.symbol is None or self.channel is None:
			botowner = (await bot.application_info()).owner
			await botowner.send('It appears setup is not complete. Run `[p]aes` to begin setup!')
		else:
			self.symbol = str(self.symbol)

	#Now, lets get a function for embeding basic stuff
	def em(error: bool, content: str):
		colorset = await self.config.ColorSet
		if error == False:
			emb = discord.Embed(colour=colorset['ok'], description=content)
		else:
			emb = discord.Embed(colour=colorset['error'], description=content)
		return emb

	#Now, lets get use a group command
	@commands.group()
	@checks.admin() 
	async def aes(self, ctx):
		""" Arcs economy settings and set up."""
		if ctx.invoked_subcommand is None:
			emmsg = str('Would you like to run bot setup? Y/N')
			em = em(False, emmsg)
			await ctx.send(embed=em)
			def check(m):
				return m.content.lower() == 'y' or m.content.lower() == 'n'
			timeout = False
			try:
				answer = await self.bot.wait_for('message', check=check)
			except asyncio.TimeoutError:
				timeout = True

			if answer.content.lower() == 'n' or timeout is False:
				await ctx.send_cmd_help() #Fix this
			else:
				emmsg = str('React to this message with the emote you would like to use as your custom currency emote. This must be a server emote.')
				em = em(False, emmsg)
				await ctx.send(embed=em)
				def check(r, u):
					return u == ctx.message.author
				try:
					react, user = await client.wait_for('reaction_add', timeout=60.0, check=check)
				except asyncio.TimeoutError:
					emmsg = str('No valid reaction detected. Exiting setup.')
					em = em(True, emmsg)
					await ctx.send(embed=em)
				else:
					c_emoji = self.bot.get_emoji(react.emoji)
					validemoji = False
					while isinstance(c_emoji, basestring):
						emmsg = str('Emoji is not a server emoji. Please react to this with a custom server emoji.')
						em = em(False, emmsg)
						await ctx.send(embed=em)
						def check(r, u):
							return u == ctx.message.author
						try:
							react, user = await client.wait_for('reaction_add', timeout=60.0, check=check)
						except asyncio.TimeoutError:
							emmsg = str('No valid reaction detected. Exiting setup.')
							em = em(True, emmsg)
							await ctx.send(embed=em)
						else:
							c_emoji = self.bot.get_emoji(react.emoji)
					await ctx.message.add_reaction('👌')
					await ctx.message.add_reaction(c_emoji)
					await self.config.coin_symbol.set(c_emoji.id)
					emmsg = str('Last step. We now need to determine what channel you would like for money to drop in when someone leaves or is removed from the server. Would you like to continue? Y/N')
					em = em(False, emmsg)
					await ctx.send(embed=em)
					def check(m):
						return m.content.lower() == 'y' or m.content.lower() == 'n'
					timeout = False
					try:
						answer = await self.bot.wait_for('message', check=check)
					except asyncio.TimeoutError:
						timeout = True

					if answer.content.lower() == 'y' or timeout:
						emmsg = str('Enter the channel ID of the channel you want the money to drop in when a user leaves.')
						em = em(False, emmsg)
						await ctx.send(embed=em)
						def check(m):
							return m.author = ctx.message.author
						try:
							channelID = await self.bot.wait_for('message', timeout= 60.0, check=check)
						except asyncio.TimeoutError:
							emmsg = str('No valid reaction detected. Exiting setup.')
							em = em(True, emmsg)
							await ctx.send(embed=em)
						else:
							channel = self.bot.get_channel(int(channelID))
							while channel is None:
								emmsg = str('Invalid channel ID.Enter the channel ID of the channel you want the money to drop in when a user leaves.')
								em = em(True, emmsg)
								await ctx.send(embed=em)
								def check(m):
									return m.author = ctx.message.author
								try:
									channelID = await self.bot.wait_for('message', timeout= 60.0, check=check)
								except asyncio.TimeoutError:
									emmsg = str('No valid reaction detected. Exiting setup.')
									em = em(True, emmsg)
									await ctx.send(embed=em)
								else:
									channel = self.bot.get_channel(int(channelID))
							await ctx.message.add_reaction('👌')


	@aes.command()
	@checks.admin()
	async def color(self, ctx): #might have a problem with how im formating the colors as str
		""" Set error and normal colors of embed """
		colors = await self.config.ColorSet()
		em = em('This is a Non-error embed. You are about to change its color type. Type the 6 digit hexadecimal below. Anything else will skip to the next prompt.')
		await ctx.send(embed=em)
		clr = await self.bot.wait_for('message')
		if len(clr.content) == 6:
			await ctx.message.add_reaction('👌')
			clr = str('0x'+clr)
			colors['ok'] = clr
		em = em('This is an Error embed. You are about to change its color type. Type the 6 digit hexadecimal below. Anything else will end this set-up.')
		await ctx.send(embed=em)
		clr = await self.bot.wait_for('message')
		if len(clr.content) == 6:
			await ctx.message.add_reaction('👌')
			clr = str('0x'+clr)
			colors['error'] = clr
		await self.config.ColorSet.set(colors)

	@aes.command()
	@checks.admin()
	async def brmulti(self, ctx):
		""" Set br multiplier """
		multis = await self.config.BetrollMultipliers()
		em = em('You are about to set the multiplier for 99 and up. Start the message with `br` for me to read it. Anything else will skip to the next prompt.')
		await ctx.send(embed=em)
		multi = await self.bot.wait_for('message')
		if multi.content.startswith('br'):
			await ctx.message.add_reaction('👌')
			multi = multi.content
			multi = multi[3:]
			multi = int(multi)
			multis['99'] = multi
		em = em('You are about to set the multiplier for 91 to 98. Start the message with `br` for me to read it. Anything else will skip to the next prompt.')
		await ctx.send(embed=em)
		multi = await self.bot.wait_for('message')
		if multi.content.startswith('br'):
			await ctx.message.add_reaction('👌')
			multi = multi.content
			multi = multi[3:]
			multi = int(multi)
			multis['91'] = multi
		em = em('You are about to set the multiplier for 67 to 91. Start the message with `br` for me to read it. Anything else will end this set-up.')
		await ctx.send(embed=em)
		multi = await self.bot.wait_for('message')
		if multi.content.startswith('br'):
			await ctx.message.add_reaction('👌')
			multi = multi.content
			multi = multi[3:]
			multi = int(multi)
			multis['67'] = multi
		await self.config.BetrollMultipliers.set(multis)

	@aes.command()
	@checks.admin()
	async def dropchance(self, ctx, chance: int): 
		""" Set drop chance. 
		It will be 1 out of the number you put. """
		await self.config.dropChance.set(chance)
		await ctx.message.add_reaction('👌')

	@aes.command()
	@checks.admin()
	async def droplimits(self, ctx, mindrop: int, maxdrop: int): 
		""" Set the min and max drop ammount. """
		limits = {'min': mindrop, 'max': maxdrop}
		await self.config.dropAmounts.set(limits)
		await ctx.message.add_reaction('👌')

	@aes.command()
	@checks.admin()
	async def csymobol(self, ctx, emoji: discord.Emoji): 
		""" Sets the currency symbol. """
		data = {emoji.id: emoji.guild.id}
		await self.config.coin_symbol.set(emoji.id)
		await ctx.message.add_reaction('👌')

	@aes.command()
	@checks.admin()
	async def minwaifuprice(self, ctx, price: int): 
		""" Sets the minimum waifu price  """
		await self.config.minWaifuPrice.set(price)
		await ctx.message.add_reaction('👌')

	@aes.command()
	@checks.admin()
	async def giftmuliplier(self, ctx, mulitplier: float): 
		""" Sets the waifu gift mulitplier.
		It must be a decimal value (1.0 for no multiplier)
		A waifu's price goes up as you give them gifts.
		The amount it goes up by is equal to
		the price of the gift times the 
		waifu gift mulitplier. """
		await self.config.waifuGiftMultiplier.set(price)
		await ctx.message.add_reaction('👌')

	@aes.command()
	@checks.admin()
	async def xpgain(self, ctx, xppermessage: int, xpcooldown: int): 
		""" Sets the xp gain settings.
		xpcooldown sould be in seconds.
		xppermessage is the amount of xp gained per message
		xpcooldown is the time to wait before giving xp again."""
		await self.config.xppermessage.set(xppermessage)
		await self.config.xpcooldown.set(xpcooldown)
		await ctx.message.add_reaction('👌')

	@aes.command()
	@checks.admin()
	async def boosttoggle(self, ctx, toggle: bool): 
		""" Toggles boosts on and off.
		BOOSTS ARE UNDERDEVELOPEMENT"""
		await self.config.minWaifuPrice.set(price)
		await ctx.message.add_reaction('👌')

#Base Economy- add plant
	@commands.command(name="give")#em
	@checks.is_owner()
	async def give(self, ctx, amount: int, *, user: discord.Member):
		""" Give your currency to another user """
		if amount > 0:
			can = await bank.can_spend(ctx.message.author, amount)
			currency = await bank.get_balance(user)
			if can:
				await bank.transfer_credits(ctx.message.author, user, amount)
				await ctx.message.add_reaction('👌')
			else:
				emmsg = str('Insufficient funds')
				em = em(True, emmsg)
				await ctx.send(embed=em)
		else:
			emmsg = str('Invalid amount.')
			em = em(True, emmsg)
			await ctx.send(embed=em)

	@commands.command(name="award",  aliases=["return", "yours"])
	@checks.is_owner()
	async def award(self, ctx, amount: int, *, user: discord.Member=None, role: discord.Role=None):
		""" Award currency to an user or a role """
		if user != None:
			await bank.deposit_credits(user, amount)
		else:
			for user in role.member:
				await bank.deposit_credits(user, amount)
		await ctx.message.add_reaction('👌')


	@commands.command(name="take",  aliases=["steal", "mine"])
	@checks.is_owner()
	async def take(self, ctx, amount: int, *, user: discord.Member=None, role: discord.Role=None):
		""" Take currency from an user """
		if user != None:
			can = await bank.can_spend(user, amount)
			currency = await bank.get_balance(user)
			if can: 
				await bank.withdraw_credits(user, amount)
			else:
				await bank.set_balance(user, 0)
		else:
			for user in role.member:
				can = await bank.can_spend(user, amount)
				currency = await bank.get_balance(user)
				if can: 
					await bank.withdraw_credits(user, amount)
				else:
					await bank.set_balance(user, 0)
		await ctx.message.add_reaction('👌')

	@commands.command(name="balance",  aliases=["$", "4", "wallet"])#em
	async def balancecheck(self, ctx, *, user: discord.Member=None):
		""" Bet roll! Higher Stakes. Higher Reward """
		if user is None:
			user = ctx.author
		bal = bank.get_balance(user)
		emmsg = str("{}'s balance is {}{}".format(user.display_name, bal, self.symbol))
		em = em(True, emmsg)
		await ctx.send(embed=em)

	@commands.command() #em
	async def broll(self, ctx, amount: int):
		""" Bet roll! Higher Stakes. Higher Reward """
		multipliers = await self.config.BetrollMultipliers()
		can = await bank.can_spend(member, amount)
		if not can:
			await ctx.send(You do not have enough!)
		else:
			await bank.withdraw_credits(member, amount)
			gained = amount
			minroll = 66
			roll = random.randint(1,100)
			balance = await bank.get_balance(member)
			if amount == balance:
				if roll < 70:
					roll = roll + 30
				elif roll > 90:
					roll = roll
				else:
					roll = random.randint(90,100)
			if roll >= 67:
				if roll >= 91:
					if roll >= 99:
						gained = amount * multipliers['99']
						minroll = 99
					else:
						gained = amount * multipliers['91']
						minroll = 91
				else:
					gained = amount * multipliers['67']
					minroll = 67
				emmsg = str('Congrats, you rolled a {}. You get {}{} for rolling at or above {}!'.format(str(roll), str(gained), self.symbol, str(minroll)))
				em = em(False, emmsg)
				await ctx.send(embed=em)
				await bank.deposit_credits(member, gained)
			else:
				emmsg = str('Sorry, you only rolled a {}'.format(str(roll)))
				em = em(False, emmsg)
				await ctx.send(embed=em)

#Waifu System 
	@commands.command()#em
	async def claim(self, ctx, amount: int, member: discord.Member):
		""" Claim a waifu as your own. """
		canbuy = True
		minprice = await self.config.minWaifuPrice
		price = await self.config.member(member).waifuPrice()
		price = int(price * 1.1)
		if not amount >= minprice:
			canbuy = False
			emmsg = str("Don't be cheap. This waifu is obviously worth more than that. At lease pay {}{}".format(str(minprice), self.symbol))
			em = em(True, emmsg)
			await ctx.send(embed=em)
		if not amount >= price:
			canbuy = False
			emmsg = str("You must pay {}{} or more to purchase this waifu".format(str(price), self.symbol))
			em = em(True, emmsg)
			await ctx.send(embed=em)
		can = await bank.can_spend(member, amount)
		if not can:
			emmsg = str('You do not have enough!')
			em = em(True, emmsg)
			await ctx.send(embed=em)
			canbuy = False
		if canbuy:
			await bank.withdraw_credits(ctx.message.author, amount)
			affinityID = await self.config.member(member).likes()
			if ctx.message.author.id == affinityID:
				amount = int(amount * 1.1)
			await self.config.member(member).waifuPrice.set(amount)
			await self.config.member(member).owner.set(ctx.message.author.id)
			waifus = await self.config.member(ctx.message.author).waifus()
			waifus.append(member.id)
			await self.config.member(ctx.message.author).waifus.set(waifus)
			await ctx.message.add_reaction('👌')

	@commands.command(name="infocard",  aliases=["cardinfo", "card", "ic"])#swap emojis
	async def infocards(self, ctx, member: discord.Member=None):
		""" Displays an user's cards 
		Each user has 2 cards
		their Waifu Card and their Character Card  """
		emojiW = '💞'
		emojiI = '📜'
		if member == None:
			member = ctx.message.author

		#Creating Waifu Card
		#formating Gift string
		gifts = await self.config.member(member).gifts()
		giftEmojis = await self.config.giftEmojis()
		giftContent = ""
		n_inline = 1
		for gift in gifts:
			amount = gifts[gift]
			emoji = giftEmojis[gift]
			if n_inline == 1:
				n_inline = 2
				giftContent += str("{}x{}".format(str(emoji), str(amount)))
			else: 
				n_inline = 1
				giftContent += str("{}x{}\n".format(str(emoji), str(amount)))
		#formating basic
		price = await self.config.member(member).waifuPrice()
		owner = await self.config.member(member).owner()
		owner = self.bot.get_user(owner)
		if owner is None:
			owner = "Nobody"
		likes = await self.config.member(member).likes()
		changes = await self.config.member(member).changes()
		divorces = await self.config.member(member).divorces()
		avatar = member.avatar_url if member.avatar \
						else member.default_avatar_url
		#formating Waifus 
		waifuList = await self.config.member(member).waifus
		waifuContent = ""
		waifuCount = 0
		for waifu in waifuList:
			waifuCount = waifuCount + 1
			waifuContent += str("{}\n".format(str(waifuList[waifu])))
		#creating Embed
		waifu_embed = discord.Embed(colour=0x2e5090, description="Waifu Info")
		waifu_embed.set_author(name='{}'.format(member.name), icon_url=avatar)
		waifu_embed.title = str("{}'s Card".format(member.name))
		waifu_embed.add_field(name="Price", value=str(price), inline=False)
		waifu_embed.add_field(name="Claimed by", value=str(owner), inline=True)
		waifu_embed.add_field(name="Likes", value=str(likes), inline=False)
		waifu_embed.add_field(name="Affinity Changes", value=str(changes), inline=True)
		waifu_embed.add_field(name="Divorces", value=str(divorces), inline=False)
		waifu_embed.add_field(name="Waifus ({})".format(waifuCount), value=str(waifuContent), inline=False)
		
		#Creating an inventory/ XP Card
		xp = self.config.member(member).xp()
		lvl = self.config.member(member).level()
		xpreq = int((5*lvl)+50)
		balance = await bank.get_balance(member)
		balance = str(balance)
		balance = balance + self.symbol
		#formating roles
		roleList = await self.config.member(member).roles()
		roleContent = ""
		roleCount = 0
		for role in roleList:
			roleCount = roleCount + 1
			raw_rolestr = str("{}\n".format(str(roleList[role])))
			content_len = len(roleContent)
			if int(content_len + len(raw_rolestr)) > 1024:
				break  
			roleContent += raw_rolestr
		#formating items
		itemList = await self.config.member(member).items()
		itemContent = ""
		itemCount = 0
		for item in itemList::
			itemCount = itemCount + 1
			raw_itemstr = str("{} x{}\n".format(str(item), str(itemList[item])))
			content_len = len(itemContent)
			if int(content_len + len(raw_itemstr)) > 1024:
				break  
			itemContent += raw_itemstr

		#Creating embed
		char_embed = discord.Embed(colour=0x2e5090, description="Character Card")
		char_embed.set_author(name='{}'.format(member.name), icon_url=avatar)
		char_embed.title = str("{}'s Card".format(member.name))
		char_embed.add_field(name=str("Level: {}".format(str(lvl))), value=str("{} / {} xp".format(str(xp), str(xpreq))), inline=False)
		char_embed.add_field(name="Bank Balance", value=str(balance), inline=True)
		char_embed.add_field(name="Roles ({})".format(roleCount), value=str(roleContent), inline=False)
		char_embed.add_field(name="Items ({})".format(itemCount), value=str(itemContent), inline=False)

		#Embeds are now built... time for the reaction shit
		index = 0
		await message.add_reaction(emojiI)
		await message.add_reaction(emojiW)
		asyncio.sleep(1)
		timeout = False
		def check(r, u):
			return u == ctx.message.author
		while timeout == False:
			try:
				reaction, r_user = await self.bot.wait_for('reaction_add', timeout=120.0, check=check)
			except asyncio.TimeoutError:
				timeout = True
			if reaction.emoji == emojiI:
				if index == 1:
					index = 0
					await message.edit(embed=char_embed)
			if reaction.emoji == emojiW:
				if index == 0:
					index = 1
					await message.edit(embed=waifu_embed)
		asyncio.sleep(1)
		try:
			await message.clear_reactions()
		except:

	@commands.command() #em
	async def divorce(self, ctx, member: discord.Member=None):
		""" Divorce a waifu you own. """
		price = await self.config.member(member).waifuPrice() 
		ownerID = await self.config.member(member).owner()
		affinityID = await self.config.member(member).likes()
		if ctx.message.author.id == ownerID:
			if ctx.message.author.id == affinityID:
				emmsg = str("You divorced a waifu that likes you, you heartless monster! They recieved {}{} to mend their broken heart".format(str(price), self.symbol))
				em = em(True, emmsg)
				await ctx.send(embed=em)
				await bank.deposit_credits(member, price)
				await self.config.member(member).owner.set("Nobody")
			else:
				price = int(price/2)
				emmsg = str("You divorced a waifu that doesnt like you. You have gained {}{}".format(str(price), self.symbol))
				em = em(True, emmsg)
				await ctx.send(embed=em)
				await bank.deposit_credits(ctx.message.author, price)
			await self.config.member(member).owner.set("Nobody")
			divorces = await self.config.member(ctx.message.author).divorces()
			divorces = divorces + 1
			await self.config.member(ctx.message.author).divorces.set(divorces)
		else:
			emmsg = str("You cannot divorce a waifu you do not own.")
			em = em(True, emmsg)
			await ctx.send(embed=em)

	@commands.command() #Done
	async def affinity(self, ctx, member: discord.Member=None):
		""" Set who you like """
		curAff = await self.config.member(ctx.message.author).likes()
		if member.id == ctx.message.author.id:
			narC = await self.config.member(ctx.message.author).selfL()
			narC = narC + 1
			await self.config.member(ctx.message.author).selfL.set(narC)
			if narC > 3:
				emmsg = str("Okay, okay, I give up! Here you go, you egomaniac! You have now set your affinity to yourself. Congratulations...")
				em = em(False, emmsg)
				await ctx.send(embed=em)
				await self.config.member(ctx.message.author).likes.set(ctx.message.author.id)
				changes = await self.config.member(ctx.message.author).changes()
				changes = changes + 1
				await self.config.member(ctx.message.author).changes.set(changes)
			else:
				emmsg = str("You cant affinity yourself. Wierdo...")
				em = em(True, emmsg)
				await ctx.send(embed=em)
		elif member.id == curAff:
			await self.config.member(ctx.message.author).selfL.set(0)
			emmsg = str("You already like this person")
			em = em(True, emmsg)
			await ctx.send(embed=em)
		else:
			wait self.config.member(ctx.message.author).selfL.set(0)
			await self.config.member(ctx.message.author).likes.set(member.id)
			changes = await self.config.member(ctx.message.author).changes()
			changes = changes + 1
			await self.config.member(ctx.message.author).changes.set(changes)
			await ctx.message.add_reaction('👌')

	@commands.command()
	async def giftList(self, ctx, jump:int=None):
		""" UNDER DEVELOPEMENT
		Displays gifts in an embed"""
		pass

	@commands.command() #Done
	async def gift(self, ctx, gift: str, *, member: discord.Member):
		gift = gift.lower()
		pGifts = await self.config.gifts()
		uGift = pgifts[gift]
		can = await bank.can_spend(ctx.message.author, uGift)
		if can:
			pGifts = await self.config.member(member).gifts()
			pGifts_names = pGifts.keys()
			if gift in pGifts_names:
				amount = pGifts[gift]
				amount = amount + 1
				gData = {gift, amount}
				pGifts.update(gData)
				await self.config.member(member).gifts.set(pGifts)
				await bank.withdraw_credits(ctx.message.author, uGift)
				price = await self.config.member(member).waifuPrice()
				mulitplier = await self.config.waifuGiftMultiplier()
				adjustprice = int(uGift * mulitplier)
				price = int(price + adjustprice)
				await self.config.member(member).waifuPrice.set(price)
			emmsg = str("Giving {} to {} for {}{}".format(gift, str(member.name), uGift, self.symbol))
			em = em(True, emmsg)
			await ctx.send(embed=em)

#Leveling -XP message gain, Xp level up, lvluprewards, lvluproles
	#XP based leveling, leveling rewards, leveling roles
	#dont really think this is even necissary
	@commands.group()
	@checks.admin() #No help command
	async def level(self, ctx):
		""" UNDER DEVELOPEMENT
		Arcs economy leveling admin commands """
		if ctx.invoked_subcommand is None:
			pass

	async def on_message(self, message): #em
		if message.content == ".pick":
			await message.delete()
		#droping/pick
		dropamounts = await self.config.dropAmounts()
		dropamount = random.randint(dropamounts['min'], dropamounts['max'])
		pickchance = await self.config.dropchance()
		pickChance = random.randint(1,pickchance)
		if pickChance == 1:
			emmsg = str('{}{} apeared! type `.pick` to claim them!'.format(str(dropamount), self.symbol))
			em = em(False, emmsg)
			op = await ctx.send(embed=em)
			def check(m):
				return m.content == '.pick'
			msg = await self.bot.wait_for('message', check=check)
			emmsg = str("{} picked {}{}!".format(str(msg.author.name), str(dropamount), self.symbol))
			em = em(False, emmsg)
			await op.edit(embed=em, delete_after=60.0)
			await bank.deposit_credits(msg.author, dropamount)
		#leveling xp 
		last = await self.config.member(message.author).prevMsgTime()
		if last == 0:
			await self.config.member(message.author).prevMsgTime.set(5)
		else:
			sec = abs(((message.created_at)-(last)).seconds)
			cooldown = await self.config.xpcooldown()
			if int(sec+15) >= cooldown:
				await self.config.member(message.author).prevMsgTime.set(message.created_at)
				xp = await self.config.member(message.author).xp()
				gain = await self.config.xpgain()
				xp = xp+gain
				await self.config.member(message.author).xp.set(xp)
				lvl = await self.cofig.member(message.author).level()
				xpreq = int((5*lvl)+50)
				if xp == xpreq:
					await self.config.member(message.author).xp.set(0)
					lvl = lvl+1
					await self.cofig.member(message.author).level.set(lvl)
					emmsg = str('{} leveled up and is now level {}! Congrats!'.format(str(message.author.mention), str(lvl)))
					em = em(False, emmsg)
					await ctx.send(embed=em)
					if lvl == 1 or int(lvl%5) == 0:
						payout = int(lvl*1000)
						await bank.deposit_credits(message.author, payout)
					rolerws = await self.config.lvlroles()
					if lvl in rolerws:
						roleID = rolerws[lvl]
						role = discord.utils.get(message.guild.roles, id=int(roleID))
						await message.author.add_roles(role)

#Shop - Missing sell 
	@commands.group()
	@checks.admin() #No help command
	async def shop(self, ctx):
		""" Arcs economy shop settings """
		if ctx.invoked_subcommand is None:
			ctx.send_cmd_help()
			pass

	@shop.command() #Done
	async def addrole(self, ctx, price: int, *, role: discord.Role):
		""" Adds/updates a role in shop """
		roleName = role.name
		roles = await self.config.roles()
		roleCosts = roles.values()
		roleNames = roles.keys()
		roleData = {roleName: price}
		i = len(roleIDs)
		i = i + 1
		roles.update(roleData)
		await self.config.roles.set(roles)
		emmsg = str("Updating roles. {} is role number {} and it costs {}{}".format(str(role.name), str(i), str(roleCosts[i]), self.symbol))
		em = em(False, emmsg)
		await ctx.send(embed=em)


	@shop.command() #Done
	async def additem(self, ctx, price: int, *, itemName: str):
		""" Adds/updates an item in shop. """
		items = await self.config.items()
		itemCosts = items.values()
		itemData = {itemName: price}
		i = len(roleIDs)
		i = i + 1
		items.update(itemData)
		await self.config.items.set(items)
		emmsg = str("Updating Items. {} is item number {} and it costs {}{}".format(str(itemName), str(i), str(itemCosts[i]), self.symbol))
		em = em(False, emmsg)
		await ctx.send(embed=em)

	@commands.group() #No help Command
	async def buy(self, ctx):
		""" Buys something from the shop"""
		if ctx.invoked_subcommand is None:
			await ctx.send_cmd_help()
			pass

	@buy.command() #Done
	async def role(self, ctx, index: int):
		""" Buys a role from the shop """
		packedDict = await self.config.roles()
		packedKeys = packedDict.keys()
		packedValues = packedDict.values()
		uKey = packedKeys[index]
		uCost = packedValues[index]
		can = await bank.can_spend(ctx.message.author, uCost)
		if can:
			inventory = await self.config.member(ctx.message.author).inventory()
			inv = inventory.keys()
			if uKey in inv:
				emmsg = str('You already own this role.')
				em = em(False, emmsg)
				await ctx.send(embed=em)
			else:
				invData = {ukey: role}
				inventory.update(invData)
				await self.config.member(ctx.message.author).inventory.set(inventory)
				role = discord.utils.get(guild.roles, name=uKey)
				await ctx.message.author.add_roles(role, reason= "Purchased from shop")
				emmsg = str("You have purchased {} for {}{}".format(str(uKey), str(uCost), self.symbol))
				em = em(False, emmsg)
				await ctx.send(embed=em)

	@buy.command() #Done
	async def item(self, ctx, index: int):
		""" Buys a item from the shop """
		packedDict = await self.config.items()
		packedKeys = packedDict.keys()
		packedValues = packedDict.values()
		uKey = packedKeys[index]
		uCost = packedValues[index]
		can = await bank.can_spend(ctx.message.author, uCost)
		if can:
			inventory = await self.config.member(ctx.message.author).inventory()
			inv = inventory.keys()
			amount = 1
			if uKey in inv:
				amount = amount + 1
			else:
				invData = {ukey: amount}
				inventory.update(invData)
				await self.config.member(ctx.message.author).inventory.set(inventory)
				emmsg = str("You have purchased {} for {}{}.".format(str(uKey), str(uCost), self.symbol))
				em = em(False, emmsg)
				await ctx.send(embed=em)

#Deleting Members
		async def on_member_remove(self, leaver):
			#dropping their balance
			await self.config.member(leaver).stillhere.set(False)
			balance = await bank.get_balance(leaver)
			minbalance = await self.config.minLeavebalance()
			chan = await self.config.leaveChannelID()
			chan = discord.utils.get(leaver.guild.channels, id=int(chan))
			if balance >= minbalance:
				emmsg = str('{} is no longer here. So sad. Their balance of {}{} now can become yours! Type `.gimme` to claim them!'.format(str(balance), self.symbol))
				em = em(False, emmsg)
				op = await chan.send(embed=em)
				def check(m):
					return m.content == '.gimme'
				msg = await self.bot.wait_for('message', check=check)
				emmsg = str("{} picked {}{}!".format(str(msg.author.name), str(balance), self.symbol))
				em = em(False, emmsg)
				await op.edit(embed=em, delete_after=60.0)
				await bank.transfer_credits(leaver, msg.author, balance)
			#crediting their owner
			owner = await self.config.member(leaver).owner()
			if owner is not None:
				owner = self.bot.get_user(owner)
				price = await self.config.member(leaver).waifuPrice()
				price = int(price*1.1)
				await bank.deposit_credits(owner, price)
				await owner.send("It would appear that {} is no longer part of the server. As their owner, you have recieved {}{}".format(str(leaver.name), str(price), self.symbol))