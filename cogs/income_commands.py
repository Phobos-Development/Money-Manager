import calendar
from datetime import datetime
from typing import Literal

import discord
from discord import app_commands
from discord.ext import commands

from utils.database_handler import create_connection
from utils.database_handler import execute_sql
from utils.database_handler import query_sql
from utils.paginator import Paginator


class IncomeCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @staticmethod
    async def build_embeds(data, search_type=None):
        embeds = []
        new_data = {
            1: [],
            2: [],
            3: [],
            4: [],
            5: [],
            6: [],
            7: [],
            8: [],
            9: [],
            10: [],
            11: [],
            12: [],
        }
        for row in data:
            _, _, year, month, day, amount, note = row
            print(f"[{calendar.month_name[month]} {day}]")
            new_data[month].append((amount, note))
        for month, transactions in new_data.items():
            embed = discord.Embed(title=calendar.month_name[month], description="")
            total = sum([tx[0] for tx in transactions])
            embed.colour = 0xFF0000 if total < 0 else 0x00FF00
            if len(transactions) == 0:
                embed.description = (
                    f"No transactions were made in {calendar.month_name[month]}"
                )
            else:
                embed.description += (
                    f"`🔴` **Total**: -${total * -1}\n"
                    if total < 0
                    else f"`🟢` **Total**: +${total}\n"
                )
                for tx in transactions:
                    if len(embed.description) > 1800:
                        embeds.append(embed)
                        embed = discord.Embed(
                            title=calendar.month_name[month], description=""
                        )
                        embed.description += (
                            f"`🔴` **Total**: -${total * -1}\n"
                            if total < 0
                            else f"`🟢` **Total**: +${total}\n"
                        )
                    embed.description += (
                        f"\n`🔴` -${tx[0] * -1}" if tx[0] < 0 else f"\n`🟢` +${tx[0]}"
                    ) + (f" | {tx[1]}" if tx[1] is not None else "")
            if month <= datetime.now().month:
                embeds.append(embed)
        return embeds

    @app_commands.command(name="channel")
    async def set_channel(
        self, interaction: discord.Interaction, channel: discord.TextChannel
    ):
        current_channel = query_sql(
            create_connection(),
            f"SELECT channel_id FROM income_channels WHERE discord_id={interaction.user.id}",
        )
        if current_channel is None:
            execute_sql(
                create_connection(),
                f"INSERT INTO income_channels(discord_id, channel_id) VALUES(?, ?)",
                (interaction.user.id, channel.id),
            )
        else:
            self.bot.channels.remove(current_channel[0])
            execute_sql(
                create_connection(),
                f"UPDATE income_channels SET channel_id=? WHERE discord_id=?",
                (channel.id, interaction.user.id),
            )
        self.bot.channels.append(channel.id)
        await interaction.response.send_message(
            embed=discord.Embed(
                title="Channel Updated!",
                description=f"I have set your income channel to: {channel.mention}!\n\n"
                f"Now you may type `+100 [note]` or `-100 [note]` instead of `/add`",
            )
        )

    @app_commands.command(name="total")
    async def view_income(
        self,
        interaction: discord.Interaction,
        option: Literal["all", "income", "expenses"],
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
            (interaction.user.id,),
        )
        if data[0] is not None:
            amt = f"\n`🔴` -${data[0] * -1}" if data[0] < 0 else f"\n`🟢` +${data[0]}"
            await interaction.response.send_message(
                embed=discord.Embed(
                    description=f"**Total {option}**: {amt}",
                    colour=0xFF0000 if data[0] < 0 else 0x00FF00,
                )
            )
        else:
            await interaction.response.send_message(
                embed=discord.Embed(
                    title="Income Manager",
                    description="Run `/help` to get started!",
                    colour=0x19C7FC,
                )
            )

    @app_commands.command(name="monthly")
    async def view_monthly(self, interaction: discord.Interaction):
        data = query_sql(
            create_connection(),
            "SELECT * FROM income WHERE discord_id=? ORDER BY id DESC",
            (interaction.user.id,),
            one=False,
        )
        embeds = await self.build_embeds(data, "monthly")
        if len(embeds) == 0:
            embeds.append(
                discord.Embed(
                    description="No data has been stored yet!", colour=0xFF0000
                )
            )
        await interaction.response.send_message(
            embed=embeds[datetime.now().month - 1],
            view=Paginator(embeds, datetime.now().month - 1),
        )

    @app_commands.command(name="help")
    async def help(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="Income Manager Guide",
            description="This bot will allow you to store all your income and expenses.\n"
            "To get started, run `/add <amount> [note]`. If you don't like the idea of using slash "
            "commands, run `/channel <#channel>`.\n"
            "This will allow you to type `+<amount> [note]` or `-<amount> [note]` in the specified "
            "channel and have the bot track it for you.\n\n"
            "**Examples**:\n"
            "`/add -200 Bought clothes`\n"
            "`/channel #general`\n"
            "`+100 Completed a commission`\n"
            "`-30`\n"
            "`/monthly`\n"
            "`/total income`",
        )
        await interaction.response.send_message(embed=embed)


async def setup(bot):
    await bot.add_cog(IncomeCommands(bot))
