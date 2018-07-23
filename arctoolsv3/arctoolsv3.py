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

"""
Search for Incomplete to find things that were skipped over

OF UNKNOWN CONSEQUENCE:

Dict Value Change
Voice State Changes
User and Member Type Split

"""

class arctools:
	""" 
	 This cog creates a text channel for a vc
	 """
	def __init__(self, bot):
		self.bot = bot
		#AutoTextRoom
		self.vtoggle = False
		self.txtVcDict = {10: 10}
		self.autoid = 416492867532619776
		self.refID = 416491437002063883
		#self.autoid = 461575421067132928' 
		#self.refID = 451693081486688256'

		#Initializing self.vars below
		self.creation = None
		self.guild = None
		self.roles = None
		self.channels = None
		self.afkchan = None
		self.grand = None
		self.master = None
		self.diam = None
		self.plat = None
		self.gold = None
		self.sil = None
		self.bronze = None
		self.Unranked = None
		self.mercy = None
		self.mods = None
		self.arc = None
		#arcDefaults
		self.autoid = 416492867532619776
		self.tick = 0
		self.chan = None
		#mentionables
		#emojiAnalytics
		self.config = Config.get_conf(self, identifier=1123581321)
		default_global = {
			"emojis": []
		}
		default_guild = {}
		self.config.register_global(**default_global)
		self.config.register_guild(**default_guild)
		#self.file_path = "data/emojiAnalytics/emojiAnalysis.json"
		#self.json_data = dataIO.load_json(self.file_path)
		self.emojiList = []
		self.toggle = False
		self.embeds = []
		#Verify
		self.channelID = 431982248687042580
		self.relaychannelID = 398845926766280706
		self.unrankedRoleName = 'Unranked'

#AutoTextRooms'''
	async def create_txt_channel(self, guild, name, parent_id):
		payload = {
			"name": name,
			"type": 0
		}
		if parent_id is not None:
			payload["parent_id"] = parent_id

		data = await self.bot.http.request(
			discord.http.Route(
				'POST', '/guilds/{guild_id}/channels',
				guild_id=guild.id), json=payload)

		return discord.Channel(guild=guild, **data)

	@commands.command()
	@checks.admin() 
	async def autotext(self, ctx, toggled: bool):
		""" Toggles autotext to true or false. This exists to catch guild data without complicating things. """
		self.vtoggle = toggled
		self.guild = ctx.message.guild
		guild = self.guild
		self.afkchan = guild.afk_channel
		self.arc = discord.utils.get(guild.members, name= 'Arc')
		try:
			self.mercy = discord.utils.get(guild.roles, id=350065360835444736)
			self.grand = discord.utils.get(guild.roles, name='Grand Master')
			self.mods = discord.utils.get(guild.roles, name='Moderators')
			self.master = discord.utils.get(guild.roles, name='Master')
			self.diam = discord.utils.get(guild.roles, name= 'Diamond')
			self.plat = discord.utils.get(guild.roles, name='Platinum')
			self.gold = discord.utils.get(guild.roles, name='Gold')
			self.sil = discord.utils.get(guild.roles, name='Silver')
			self.bronze = discord.utils.get(guild.roles, name='Bronze')
			self.Unranked = discord.utils.get(guild.roles, name='Unranked')
		except Exception as e:
			await self.arc.send(e)
		#self.Unranked = discord.utils.get(guild.roles, name='Attendents')
		await ctx.send("Setting auto text channel creation to " + str(self.vtoggle))

	@commands.command()
	async def txtname(self, ctx, *, chaname: str):
		""" Sets the name of the text and voice channel the user is in if they are in an autoroom """
		txtIDs = self.txtVcDict.values()
		if ctx.message.channel.id in txtIDs:
			await ctx.send("Setting text channel name to {}".format(chaname))
			try:
				await ctx.message.channel.edit(name=chaname)
				await ctx.message.author.voice.channel.edit(name=chaname)
			except Exception as e:
				pass

	async def on_voice_state_update(self, memAfter, memBefore, After):
		guild = memAfter.guild
		everyone_perms = discord.PermissionOverwrite(read_messages=False)
		vc_perms = discord.PermissionOverwrite(read_messages=True)
		#Create or give readable permissions on Voice Channel join 
		if self.vtoggle and After.channel != None:
			if memBefore.channel != After.channel and After.channel.id != self.autoid:
				self.channels = memAfter.guild.channels
				vcID = After.channel.id
				textchannel = None
				vcIDs = self.txtVcDict.keys()
				if not vcID in vcIDs:
					textchannel = str(memAfter.name + "s-voice-channel")
					cat = After.channel.category
					#newChannel = await self.create_txt_channel(memAfter.guild, textchannel, self.refID)
					newChannel = await guild.create_text_channel(textchannel, category=cat) 
					tempDict = {After.channel.id: newChannel.id}
					self.txtVcDict.update(tempDict)

					await newChannel.set_permissions(memAfter, overwrite=vc_perms)
					await newChannel.set_permissions(self.mercy, overwrite=everyone_perms)
					await newChannel.set_permissions(self.grand, overwrite=everyone_perms)
					await newChannel.set_permissions(self.mods, overwrite=vc_perms)
					await newChannel.set_permissions(self.master, overwrite=everyone_perms)
					await newChannel.set_permissions(self.diam, overwrite=everyone_perms)
					await newChannel.set_permissions(self.plat, overwrite=everyone_perms)
					await newChannel.set_permissions(self.gold, overwrite=everyone_perms)
					await newChannel.set_permissions(self.sil, overwrite=everyone_perms)
					await newChannel.set_permissions(self.bronze, overwrite=everyone_perms)
					await newChannel.set_permissions(self.Unranked, overwrite=everyone_perms)
					await newChannel.send(str('Congrats {} on your new room! Feel free to customize the room how you like, just **DO NOT** make the room invisible to users and **DO NOT** touch the everyone permissions. If you have any questions, feel free to DM me.'.format(str(memAfter.mention))))

				else:
					textchannel = self.bot.get_channel(self.txtVcDict[vcID])
					await textchannel.set_permissions(memAfter, overwrite=vc_perms)
		#Delete or remove readable permissions on Voice Channel Leave
		if self.vtoggle and memBefore.channel is not None:
			if not memBefore.channel == After.channel and not memBefore.channel.id == self.autoid:
				vcID = memBefore.channel.id
				channel = self.bot.get_channel(self.txtVcDict[vcID])
				if len(memBefore.channel.members) == 0:
					del self.txtVcDict[vcID]
					await channel.delete()
				else:
					await channel.set_permissions(memAfter, overwrite=everyone_perms)

#Arc Defaults

	@commands.command()
	async def gather(self, ctx):
		""" Gathers info on the server """
		self.arc = discord.utils.get(guild.members, name= 'Arc')

	async def on_guild_channel_update(self, chanBefore, chanAfter):
		if self.tick == 0:
			notperms = discord.PermissionOverwrite(connect=True)
			everyone_perms = discord.PermissionOverwrite(connect=False)
			view_perms = discord.PermissionOverwrite(speak=True)
			if chanAfter is not None and isinstance(chanAfter, discord.VoiceChannel) and chanAfter != self.afkchan:
				for role in chanAfter.changed_roles:
					if role.is_default() == True:
						self.tick = 1
						try:
							await chanAfter.set_permissions(role, overwrite=view_perms)
						except Exception as e:
							await self.arc.send(e)
		else:
			#asyncio.sleep(3)
			self.tick = 0

	async def on_guild_channel_create(self, channel):
		guild = channel.guild
		default_perms = discord.PermissionOverwrite(connect=None)
		default = discord.utils.get(guild.roles, name='Bronze')
		if isinstance(channel, discord.VoiceChannel):
			try:
				await channel.set_permissions(default, overwrite=default_perms)
			except Exception as e:
				await self.arc.send(e)

#Arc's Unmentionables
	@commands.command()
	@checks.admin()
	async def mentionable(self, ctx, role1: discord.Role,  role2: discord.Role=None, role3: discord.Role=None, role4: discord.Role=None, role5: discord.Role=None):
		""" Makes up to 5 roles mentionable/unmentionable. If mentionable, it is set to unmentionable and vice versa. """
		guild = ctx.message.guild
		try:
			self.arc = discord.utils.get(guild.members, name= 'Arc')
		except:
			pass
		try:
			if role1 != None:
				if role1.mentionable == True:
					await role1.edit(mentionable=False)
					await ctx.send("Making {} unmentionable.".format(str(role1.name)))
				else:
					await role1.edit(mentionable=True)
					await ctx.send("Making {} mentionable.".format(str(role1.name)))
			if role2 != None:
				if role2.mentionable == True:
					await role2.edit(mentionable=False)
					await ctx.send("Making {} unmentionable.".format(str(role2.name)))				
				else:
					await role2.edit(mentionable=True)
					await ctx.send("Making {} mentionable.".format(str(role2.name)))
			if role3 != None:
				if role3.mentionable == True:
					await role3.edit(mentionable=False)
					await ctx.send("Making {} unmentionable.".format(str(role3.name)))
				else:
					await role3.edit(mentionable=True)
					await ctx.send("Making {} mentionable.".format(str(role3.name)))
			if role4 != None:
				if role4.mentionable == True:
					await role4.edit(mentionable=False)
					await ctx.send("Making {} unmentionable.".format(str(role4.name)))
				else:
					await role4.edit(mentionable=True)
					await ctx.send("Making {} mentionable.".format(str(role4.name)))
			if role5 != None:
				if role5.mentionable == True:
					await role5.edit(mentionable=False)
					await ctx.send("Making {} unmentionable.".format(str(role5.name)))
				else:
					await role5.edit(mentionable=True)
					await ctx.send("Making {} mentionable.".format(str(role5.name)))
		except Exception as e:
			try:
				await self.arc.send(e)
			except:
				pass

#emojiAnalytics
	@commands.command()
	@checks.admin()
	async def turnon(self, ctx):
		""" Turns on emoji analysis. This is mainly so that it doesnt error on its first run. """
		self.toggle = True
		await ctx.message.add_reaction('👌')
		


	@commands.command()
	@checks.admin()
	async def emojistart(self, ctx):
		""" Logs all guild emojis to the emoji config file. """
		self.toggle = True
		await ctx.send("Discovering your guilds emojis.")
		emojiList = ctx.message.guild.emojis
		self.emojiList = emojiList
		data = await self.config.emojis()
		for emoji in emojiList:
			if emoji.name not in data:
				data = await self.config.emojis()
				data.append({
					'name': emoji.name,
					#'obj': emoji,
					'uses': 0,
					'lastUse': 'none'
					#'animated': "unavailable"
					})
				await self.config.emojis.set(data)


	@commands.command()
	async def reportall(self, ctx, jump: int=None):
		""" Reports all emoji uses in an embed from least to most used. Can accept a number to jump to that page. """
		channel = ctx.message.channel
		emojiList = ctx.message.guild.emojis
		SavedEmojis = await self.config.emojis()
		#Sorting them into least to most
		nameList = []
		usesList = []
		lastuseList = []
		i = -1
		for e in emojiList:
			usesList.append(9999)
			i = int(i+1)
			for emoji in SavedEmojis:
				if emoji['uses'] < usesList[i]:
					if str(emoji["name"]) not in nameList:
						usesList[i] = int(emoji['uses'])
						tempName = emoji['name']
						tempUse = emoji['lastUse']
			nameList.append(tempName)
			lastuseList.append(tempUse)
		#Now to make the embeds
		emojiLen = int(len(nameList))
		pages = emojiLen//5
		extra = emojiLen%5
		self.embeds = []
		j = 0
		i = 0
		totaluses = sum(usesList)
		while i < pages: #Packing the embeds into a list
			description = ("Total emoji usage - {}".format(str(totaluses)))
			embed = discord.Embed(description=description, color=0x2E5090)
			embed.title = "Emoji analytics"
			footer = str("Page {}/{}".format(str(int(i+1)), str(pages)))
			embed.set_footer(text=footer)
			fieldnames = []
			fieldcontents = []
			count = 0
			while count < 5:
				fieldnames.append(str(str(int(j+1)) + ". " + str(nameList[j])))
				fieldcontents.append(str("Used {} time(s). Last use was {}".format(str(usesList[j]), str(lastuseList[j]))))
				embed.add_field(name=str(fieldnames[count]), value=str(fieldcontents[count]))
				count = count+1
				j = j+1
			self.embeds.append(embed)
			i = i+1
		#self.active = True
		author = ctx.message.author
		index = 0
		if jump == None:
			jump = 0
		elif int(jump) >= pages:
			jump = pages-1
		else:
			jump = int(jump-1)
		jumpedembed = self.embeds[jump]
		message = await channel.send(embed=jumpedembed)
		await message.add_reaction('◀')
		await message.add_reaction('▶')
		asyncio.sleep(1)
		timeout = False
		def check(r, u):
			return u == author# and ((str(r.emoji) == "◀") or (str(r.emoji) == "▶"))
		while timeout == False:
			try:
				reaction, r_user = await self.bot.wait_for('reaction_add', timeout=120.0, check=check) #[,] 
			except asyncio.TimeoutError:
				timeout = True
				break
			if reaction.emoji == '◀':
				if index > 0:
					index = index-1
					await message.edit(embed=self.embeds[index])
			if reaction.emoji == '▶':
				if index < int(pages-1):
					index = index+1
					await message.edit(embed=self.embeds[index])
		asyncio.sleep(1)
		try:
			await message.clear_reactions()
		except:
			pass

	async def on_message(self, message):
		data = await self.config.emojis()
		date = str(message.created_at)
		messageContent = message.content
		if not self.emojiList: #checks if list is empty. This is neccisary because if bot restarts it wont think emojis exist
			for emoji in data:
				self.emojiList.append(emoji['name'])
		for emojiname in self.emojiList:
			if emojiname in messageContent:
				for emoji in data:
					if emojiname == emoji['name']:
						if ":" in messageContent:
							emoji['uses'] = int(emoji['uses'] + 1)
							emoji['lastUse'] = date
							await self.config.emojis.set(data)
#'''
#Arc Relay
	@commands.command()
	@checks.mod_or_permissions(manage_roles=True)
	async def verify(self, ctx, *, user : discord.Member):
		""" Adds the verified roll to a user and relays their messages. """
		guild = ctx.message.guild
		member = guild.get_member(user.id)
		#user = member
		relaychannel = discord.utils.get(self.bot.get_all_channels(), id=self.relaychannelID)
		channel = discord.utils.get(self.bot.get_all_channels(), id=self.channelID)
		unrankedRole = discord.utils.get(guild.roles, name=self.unrankedRoleName)
		if member not in guild.members:
			await ctx.send("Role not added. No user with that ID was found.")
			return
		else:
			if unrankedRole in member.roles:
				await ctx.send("Cannot add role {} to {}. They already have this role.".format(self.unrankedRoleName, user.nick))
				return
			else:	
				await ctx.send("Adding the {} role to {} and relaying messages to {}".format(str(self.unrankedRoleName), user.name, relaychannel.name))
				await user.add_roles(unrankedRole)
				messages = await channel.history().filter(lambda m: m.author == user).flatten()
				messages.reverse()
				for message in messages:
					#if message.author == user:
					asyncio.sleep(1)
					content = message.clean_content
					author = message.author
					sname = guild.name
					cname = channel.name
					avatar = author.avatar_url if author.avatar \
						else author.default_avatar_url
					footer = 'Said in {} #{}'.format(sname, cname)
					em = discord.Embed(description=content, color=0x2E5090, timestamp=message.created_at)
					em.set_author(name='{}'.format(author.name), icon_url=avatar)
					em.set_footer(text=footer, icon_url=guild.icon_url)
					await relaychannel.send(embed=em)