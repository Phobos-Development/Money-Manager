import calendar
from datetime import datetime
from typing import Literal

import discord
from discord import app_commands
from discord.ext import commands

from utils.database_handler import query_sql, create_connection, execute_sql
from utils.paginator import Paginator


class IncomeCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @staticmethod
    async def build_embeds(data, search_type=None):
        embeds = []
        new_data = {
            "January": [],
            "February": [],
            "March": [],
            "April": [],
            "May": [],
            "June": [],
            "July": [],
            "August": [],
            "September": [],
            "October": [],
            "November": [],
            "December": [],
        }
        for row in data:
            _, _, year, month, day, amount, note = row
            print(f"[{calendar.month_name[month]} {day}]")
            new_data[calendar.month_name[month]].append((amount, note))
        print(new_data)
        return [discord.Embed(description="123"), discord.Embed(description="1234")]

    @app_commands.command(name="channel")
    @app_commands.guilds(discord.Object(id=853295571448233985))
    async def set_channel(
            self,
            interaction: discord.Interaction,
            channel: discord.TextChannel
    ):
        current_channel = query_sql(
            create_connection(),
            f"SELECT channel_id FROM income_channels WHERE discord_id={interaction.user.id}"
        )
        if current_channel is None:
            execute_sql(
                create_connection(),
                f"INSERT INTO income_channels(discord_id, channel_id) VALUES(?, ?)",
                (interaction.user.id, channel.id)
            )
        else:
            self.bot.channels.remove(current_channel[0])
            execute_sql(
                create_connection(),
                f"UPDATE income_channels SET channel_id=? WHERE discord_id=?",
                (channel.id, interaction.user.id)
            )
        self.bot.channels.append(channel.id)
        await interaction.response.send_message(
            embed=discord.Embed(
                title="Channel Updated!",
                description=f"I have set your income channel to: {channel.mention}!\n\n"
                            f"Now you may type `+100 [note]` or `-100 [note]` instead of `/add`"
            )
        )

    @commands.command(aliases=["spent", "earned"])
    async def total(self, ctx):
        if ctx.invoked_with.lower() == "spent":
            data = query_sql(create_connection(), "SELECT SUM(amount) FROM income WHERE amount < 0 AND discord_id=?", )
        elif ctx.invoked_with.lower() == "earned":
            data = query_sql(create_connection(), "SELECT SUM(amount) FROM income WHERE amount > 0")
        else:
            data = query_sql(create_connection(), "SELECT SUM(amount) FROM income")
        amt = f"\n`🔴` -${data[0] * -1}" if data[0] < 0 else f"\n`🟢` +${data[0]}"
        await ctx.send(
            embed=discord.Embed(
                description=f"**Total {ctx.invoked_with.title() if ctx.invoked_with.lower() != 'total' else ''}**: "
                            f"{amt}",
                colour=0xFF0000 if data[0] < 0 else 0x00FF00
            )
        )

    @app_commands.command(name="total")
    @app_commands.guilds(discord.Object(id=853295571448233985))
    async def view_income(
            self,
            interaction: discord.Interaction,
            option: Literal["all", "income", "expenses"]
    ):
        if option == "all":
            append = ""
        elif option == "income":
            append = "AND amount > 0"
        else:
            append = "AND amount < 0"
        data = query_sql(
            create_connection(),
            f"SELECT SUM(amount) FROM income WHERE discord_id=? {append}",
            (interaction.user.id,)
        )
        if data[0] is not None:
            amt = f"\n`🔴` -${data[0] * -1}" if data[0] < 0 else f"\n`🟢` +${data[0]}"
            await interaction.response.send_message(
                embed=discord.Embed(
                    description=f"**Total {option}**: {amt}",
                    colour=0xFF0000 if data[0] < 0 else 0x00FF00
                )
            )
        else:
            await interaction.response.send_message(
                embed=discord.Embed(
                    title="Income Manager",
                    description="Run `/help` to get started!",
                    colour=0x19C7FC
                )
            )

    @app_commands.command(name="monthly")
    @app_commands.guilds(discord.Object(id=853295571448233985))
    async def view_monthly(
            self,
            interaction: discord.Interaction
    ):
        data = query_sql(
            create_connection(),
            "SELECT * FROM income WHERE discord_id=? ORDER BY id DESC",
            (interaction.user.id,),
            one=False
        )
        embeds = await self.build_embeds(data, "monthly")
        if len(embeds) == 0:
            embeds.append(discord.Embed(description="No data has been stored yet!", colour=0xFF0000))
        await interaction.response.send_message(embed=embeds[0], view=Paginator(embeds))


async def setup(bot):
    await bot.add_cog(IncomeCommands(bot))
