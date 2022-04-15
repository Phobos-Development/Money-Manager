from datetime import datetime

import discord
from discord import app_commands
from discord.ext import commands

from utils.database_handler import create_connection, execute_sql


class IncomeTracker(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def sync(self, ctx):
        if ctx.author.id != 847438985612623882:
            return
        await self.bot.tree.sync(guild=discord.Object(id=853295571448233985))
        await ctx.send("Done")

    @app_commands.command(name="add")
    @app_commands.guilds(discord.Object(id=853295571448233985))
    async def add_income(
            self,
            interaction: discord.Interaction,
            amount: int,
            note: str = None
    ):
        if amount > 0:
            embed = discord.Embed(
                title="Updated your income!",
                description=f"+${amount} {'- ' + note if note is not None else 'N/A'}",
                colour=0x00FF00
            )
        else:
            embed = discord.Embed(
                title="Updated your expenses!",
                description=f"-${amount * -1} {'- ' + note if note is not None else 'N/A'}",
                colour=0xFF0000
            )
        await interaction.response.send_message(embed=embed)

    @commands.Cog.listener()
    async def on_message(self, message):
        if self.bot.channels is None:
            return
        if message.channel.id not in self.bot.channels:
            return
        amount, note = message.content.split(" ")[0].replace("+", ""), message.content.split(" ")[1:]
        try:
            amount = int(amount)
        except ValueError:
            return
        colour = 0xFF0000 if amount < 0 else 0x00FF00
        _amount = f"${amount}" if int(amount) >= 0 else f"-${int(amount) * -1}"
        emb = discord.Embed(
            description=f"**Amount**: {_amount}",
            colour=colour
        )
        if len(note) >= 1:
            emb.description += f"\n**Note**: {' '.join(note)}"
        await message.reply(
            embed=emb
        )
        note = None if len(note) < 1 else " ".join(note)
        execute_sql(
            create_connection(),
            f"INSERT INTO income(discord_id, year, month, day, amount, note)"
            f"VALUES(?, ?, ?, ?, ?, ?)",
            (message.author.id, datetime.now().year, datetime.now().month, datetime.now().day, amount, note)
        )


async def setup(bot):
    await bot.add_cog(IncomeTracker(bot))