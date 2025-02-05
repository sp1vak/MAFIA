import disnake

class Join(disnake.ui.View):
    def __init__(self):
        super().__init__(timeout=45.0)
        self.members = []

    @disnake.ui.button(label="Приєднатися!", style=disnake.ButtonStyle.green)
    async def join(self, button: disnake.Button, interaction: disnake.Interaction):
        if interaction.author in self.members:
            self.members.append(interaction.author)
            await interaction.response.send_message(f"Приєднано гравця {interaction.author}")
        else:
            await interaction.response.send_message("Ти вже у грі!", ephemeral=True)

    @disnake.ui.button(label="Від'єднатися!", style=disnake.ButtonStyle.red)
    async def leave(self, button: disnake.Button, interaction: disnake.Interaction):
        if interaction.author in self.members:
            await interaction.response.send_message(f"Гравець {interaction.author} вийшов з гри")
            self.members.remove(interaction.author)
        else:
            await interaction.response.send_message("Ти не увійшов у гру!", ephemeral=True)