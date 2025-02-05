import disnake

class ChooseDeath(disnake.ui.View):
    def __init__ (self, members_name_wtht_don):
        super().__init__(timeout=20.0)
        self.killed = None
        self.members_name_wtht_don = members_name_wtht_don

        for member in self.members_name_wtht_don:
            if member != '---':
                button = disnake.ui.Button(style=disnake.ButtonStyle.red, label=str(member))

                async def button_callback(self, interaction: disnake.MessageInteraction, member=member):
                    self.killed = member
                    await interaction.response.send_message("Обрано!")#if it works, dont touch it
                    self.stop()

                button.callback = button_callback.__get__(self)
                self.add_item(button)

    @disnake.ui.button(label="Пропустити", style = disnake.ButtonStyle.blurple)
    async def skip(self, button:disnake.Button, inter:disnake.CommandInteraction):
        await inter.response.send_message("Вибір зроблено!")
        self.stop()