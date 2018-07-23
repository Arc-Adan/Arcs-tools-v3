from .ArcsEconomy import ArcsEconomy

def setup(bot):
	n = ArcsEconomy(bot)
	bot.add_cog(n)