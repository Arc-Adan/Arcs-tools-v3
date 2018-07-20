from .arctoolsv3 import arctools


def setup(bot):
	#e = emojiAnalytics(bot)
	#a = arcRelay(bot)
	#o = mentionable(bot)
	#m = arcdef(bot)
	n = arctools(bot)
	#bot.add_cog(m)
	bot.add_cog(n)
	#bot.add_cog(o)
	#bot.add_cog(a)
	#bot.add_cog(e)