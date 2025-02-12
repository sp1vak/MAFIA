import os
import disnake
from disnake.ext import commands


bot = commands.Bot(command_prefix=".", help_command=None, intents=disnake.Intents.all(), test_guilds=[1081203721607847956, 1229395978080092191], activity=disnake.Game(name="Вибираю тобі роль..."))

@bot.command()
@commands.is_owner()
async def load(ctx, extension):
    bot.load_extension(f"cogs.{extension}")

@bot.command()
@commands.is_owner()
async def unload(ctx, extension):
    bot.unload_extension(f"cogs.{extension}")
    await ctx.send(f"Extension {extension} unloaded!")

@bot.command()
@commands.is_owner()
async def reload(ctx, extension):
    bot.reload_extension(f"cogs.{extension}")
    await ctx.send(f"Extension {extension} reloaded!")

for filename in os.listdir("cogs"):
    if filename.endswith(".py"):
        bot.load_extension(f"cogs.{filename[:-3]}")

bot.run('')