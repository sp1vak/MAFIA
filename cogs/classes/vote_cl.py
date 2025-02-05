import disnake

class Vote(disnake.ui.View):
    def __init__ (self, members):
        super().__init__(timeout=100.0)
        self.vote = None
        self.members = members

        for member in self.members:
            if member != '---':
                button = disnake.ui.Button(style=disnake.ButtonStyle.red, label=str(member))

                async def button_callback(self, interaction: disnake.MessageInteraction, member=member):
                    self.vote = member
                    await interaction.response.send_message("Обрано!")#if it works, dont touch it))
                    self.stop()

                button.callback = button_callback.__get__(self)
                self.add_item(button)


    @disnake.ui.button(label="Пропустити", style=disnake.ButtonStyle.blurple)
    async def skip(self, button:disnake.Button, inter:disnake.CommandInteraction):
        await inter.response.send_message("Гравця було обрано!")
        self.stop()