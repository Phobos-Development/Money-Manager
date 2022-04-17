from typing import List

import discord.ui


class Paginator(discord.ui.View):
    def __init__(self, embeds: List[discord.Embed], start_page):
        super().__init__(timeout=60)
        self.embeds = embeds
        self.current_page = start_page
        if self.current_page == 0:
            self.previous_page.disabled = True
        if self.current_page == len(embeds):
            self.next_page.disabled = True

    @discord.ui.button(label="←", style=discord.ButtonStyle.blurple, disabled=False)
    async def previous_page(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        if self.current_page == 1:
            self.previous_page.disabled = True
        self.next_page.disabled = False
        self.current_page -= 1
        embed = self.embeds[self.current_page]

        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="→", style=discord.ButtonStyle.blurple, disabled=False)
    async def next_page(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        self.current_page += 1
        print(self.current_page)
        if self.current_page == len(self.embeds) - 1:
            self.next_page.disabled = True
        self.previous_page.disabled = False
        embed = self.embeds[self.current_page]

        await interaction.response.edit_message(embed=embed, view=self)
