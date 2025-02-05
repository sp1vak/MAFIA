import disnake
import asyncio
import random
from disnake.ext import commands
from .classes import join, choose_death, choose_heal, vote_cl


class StartGame(commands.Cog):
    def __init__(self,bot):
        self.bot = bot
        
    @commands.Cog.listener()  
    async def on_ready(self):
        print("Бот готовий до праці!")

    @commands.slash_command(name = 'start', description= 'Щоб почати гру, введи спочатку назву гри, а потім перелік гравців, яких ти запрошуєш')
    async def start(self, inter: disnake.ApplicationCommandInteraction, name: str):
        await inter.send(embed = disnake.Embed(title= "Відправлено запрошення!", description="Не забудь сам приєднатися!"), ephemeral=True)
        guild = inter.author.guild
        channel = inter.channel
        view = join.Join()
        await channel.send(embed = disnake.Embed(title = f'Підбір гравців до гри {name}', description='Жмяк "Приєднатися"!'), view=view)
        await view.wait()
        self.members = view.members

        #Надсилання результату та початок гри
        if len(self.members) <= 3:
            await inter.send(embed=disnake.Embed(title=f"Гру відмінено! Дехто не прийняв запрошення", color=0x000000))
        else:
            await inter.send(embed=disnake.Embed(title="Усі прийняли запрошення!", description="Очікуйте на початок гри", color=0xff0000))
            g = Game(self.bot, self.members, name, guild)
            await asyncio.sleep(2)
            await inter.send(embed=disnake.Embed(title="Гра починається.", description=f"Перейдіть в канал {name}", color=0x000000))
            await g.game_preparation()

    @commands.slash_command(name='help', description= 'Щоб почати гру, введи спочатку назву гри, а потім перелік гравців, яких ти запрошуєш')
    async def help(self, inter):
        author = inter.author
        embed = disnake.Embed(title=f"Привіт, {author}!", description="Це інформація про бота!", color = 0xffffff)
        embed.set_author(name="Mafia", icon_url="https://i.pinimg.com/564x/dc/a8/0b/dca80b34c94c2f25089b98e08503121a.jpg")
        embed.set_thumbnail(url="https://i.pinimg.com/564x/3a/0a/17/3a0a1753db493f176ec0b32b63302833.jpg")
        embed.set_footer(
        text="by sp1vak",
        icon_url="https://i.pinimg.com/564x/dc/a8/0b/dca80b34c94c2f25089b98e08503121a.jpg",
        )
        embed.set_image(url="https://i.pinimg.com/564x/ee/13/1f/ee131f1eb4316fdd9dc070addddda27b.jpg")
        embed.add_field(name="Команди", value="У цьому боті тіки одна команда окрім `/help` - `/start`. Приймає один параметр `назва гри`", inline=False)
        embed.add_field(name="Початок гри", value="Після вводу команди гравцям приходе запрошення. Коли всі прийняли, починається гра.", inline=True)
        embed.add_field(name="Вибір жертви", value="Після початку гри, гравцям видаються ролі: два мирних, вбивця, доктор. Гра починається з вибору вбивці, кого вбити. Після його вибіру йде доктор.", inline=True)
        embed.add_field(name="Обговорення", value=" Якщо доктор вгадав кого вибрав вбивця, той залишається живий. Якщо ж не вгадує, то ви втрачаєте одного гравця. Після цього хвилина обговорення.")
        embed.add_field(name="Голосування", value="Коли ви все обговорили, вибираєте проти кого голосувати.")
        embed.add_field(name="Нехай щастить!", value="Надіюсь, тобі ця інформація допомогла. На все добре!")
        await inter.send(embed=embed, ephemeral=True)


class Game(commands.Cog):
    def __init__(self, bot, members, nameofgame, guild):
        self.members = members
        self.nameofgame = nameofgame
        self.guild = guild
        self.members_name_wtht_don = []
        self.bot = bot
        self.killed_list = []


    async def game_preparation(self):
        """підготовка до гри: створювання ролей, каналів, видача прав(фіміністкам не видаємо)"""
        #Створюємо роль гри та роль вбитої людини, яку будемо видавати тим, кого вбили або вибрали в голосуванні
        await self.guild.create_role(name = self.nameofgame)#створення ролі звичайних гравців
        await self.guild.create_role(name='Вмер')# створення ролі для вбитих

        self.rolegame = disnake.utils.get(self.guild.roles, name = self.nameofgame)# засовуємо роль гравця в змінну
        self.roledead = disnake.utils.get(self.guild.roles, name = 'Вмер')# role for dead -> self.roledead

        #Визначаємо, хто буде доном, доктором, мирними жителями
        random.shuffle(self.members)
        self.peaceful_list = []
        for member in self.members:
            await member.add_roles(self.rolegame)
        self.don = self.members[0]
        self.doctor = self.members[1]
        for member in self.members[2:]:
            self.peaceful_list.append(member)
        print('don: ', self.don)
        print('doctor: ', self.doctor)

        self.members_name_wtht_don.append(self.doctor)
        for member in self.peaceful_list:
            self.members_name_wtht_don.append(member)

        #Для голосування
        self.voting = {None: 0}
        for member in self.members:
            self.voting[member] = 0

        #Створювання текстового каналу, де буде проводитися гра та видання прав
        await self.guild.create_text_channel(self.nameofgame)
        self.channel = disnake.utils.get(self.guild.channels, name=self.nameofgame)
        await self.channel.set_permissions(self.guild.default_role, speak=False, send_messages = False, read_message_history=False, read_messages = False)
        await self.channel.set_permissions(self.rolegame, speak=True,send_messages=True,read_message_history=True,read_messages=True)
        await self.channel.set_permissions(self.roledead, speak=False, send_messages = False, read_message_history=True, read_messages = True)

        #Повідомлення гравців про їхню роль
        await asyncio.sleep(5)
        
        await self.channel.send(embed = disnake.Embed(title="Гра підібрала ваші ролі.", description="Перейдіть в приватні повідомлення з ботом", color = 0x000000))
        await asyncio.sleep(2)
        await self.don.send(embed = disnake.Embed(title = 'Ти вбивця', description='Убий всіх, поки не вбили тебе', color = 0xff0000))
        await self.doctor.send(embed = disnake.Embed(title= 'Ти доктор', description='Твоя ціль - лікувати людей та знаходити вбивцю', color = 0xffffff))
        for member in self.peaceful_list:
            await member.send(embed = disnake.Embed(title = 'Ти мирний', description='Знайди вбивцю та вижени його!', color = 0xffffff)) # - Розсилка ролей гравців

        #Повідомлення про початок гри
        await asyncio.sleep(5)
        await self.channel.send(embed = disnake.Embed(title = 'Гра почалась', color = 0x000000))# - Повідомлення про початок гри
        await asyncio.sleep(5)

        #Повідомлення про вечерю перед ніччю, та час для спілкування
        await self.channel.send(embed = disnake.Embed(title= 'Вечеря перед ніччю.', description='Намагайтеся виявити вбивцю!', color=0xff0000))
        await asyncio.sleep(60)# - Обговорення майбутньої ночі, гравці знайомляться один з одним.

        #початок гри.
        await self.game_2()

    async def game_2(self):
        """Вбивця та доктор виходять на нічну зміну."""
        await self.channel.set_permissions(self.rolegame, speak=False,send_messages=False,read_message_history=True,read_messages=True)

        await self.channel.send(embed=disnake.Embed(title="Настала ніч...", description="Намагайся вижити!", color = 0x000000))

        #Кнопки
        view = choose_death.ChooseDeath(self.members_name_wtht_don)
        await self.don.send(embed = disnake.Embed(title = 'Кого вб`ємо?',description="Обери, кого буде найвигідніше вбити!", color = 0xff0000), view=view)
        await view.wait()

        self.killed = view.killed

        await asyncio.sleep(2)

        if self.killed == view.killed:
            self.killed = None

        if self.doctor not in self.killed_list:
            view = choose_heal.ChooseHeal(self.members)
            await self.doctor.send(embed = disnake.Embed(title = 'До кого в дім зайдемо?', description="Обери, кого лікуватимеш цієї ночі.", color = 0xffffff), view=view)
            await view.wait()
            await asyncio.sleep(2)

        if self.killed in self.members:
            self.members[self.members.index(self.killed)] = '---'
            self.members_name_wtht_don[self.members_name_wtht_don.index(self.killed)] = '---'
        
        await asyncio.sleep(1)

        #Оголошення, кого вбили чи нікого
        if self.killed == None:
            await self.channel.send(embed=disnake.Embed(title='Ніч пройшла!', description='Цієї ночі нікого не вбили!', color = 0xffffff))
        else:
            await self.channel.send(embed=disnake.Embed(title="Ніч пройшла!", description=f'{self.killed} покидає нас...', color = 0xff0000))
            await self.killed.add_roles(self.roledead)
            await self.killed.remove_roles(self.rolegame)
            self.killed_list.append(self.killed)

        #Підрахунок вбитих
        count = 0
        for member in self.members:
            if member != '---':
                count +=1
        if count <= 2:
            await self.over_game()
            await self.channel.send(embed=disnake.Embed(title="Дон виграв"))
        elif count > 2:
            await self.voting_game()


    async def voting_game(self):
        """Голосування, хто вбивця"""
        #Обговорення
        await self.channel.set_permissions(self.rolegame, speak=True,send_messages=True,read_message_history=True,read_messages=True)
        await self.channel.send(embed = disnake.Embed(title = "Обговорення. У вас одна хвилина", description="Обговоріть вбивцю, та проголосуйте"))

        #Кнопки для голосування
        tasks = []
        for member in self.members:
            async def vote(member):
                if member != '---':
                    view = vote_cl.Vote(self.members)
                    await member.send(embed = disnake.Embed(title = "Голосування", description="Виберіть людину, що здається підозрілою", color = 0xffffff), view=view)
                    await view.wait()
                    return view.vote
                return 'kill'
            tasks.append(vote(member))
        values = await asyncio.gather(*tasks)

        for i in values:
            if i != 'kill':
                self.voting[i] += 1

        #Підрахунок та вибір гравця, якого кікаємо.
        voted = max(self.voting, key=self.voting.get)
        if voted != None:
            self.members[self.members.index(voted)] = '---'
            if voted in self.members_name_wtht_don:
                self.members_name_wtht_don[self.members_name_wtht_don.index(voted)] = '---'
            await voted.add_roles(self.roledead)
        self.killed_list.append(voted)

        #Підрахунок вбитих
        count = 0
        for member in self.members:
            if member != '---':
                count += 1
        await self.channel.send(embed = disnake.Embed(title="Підбито підсумки голосування", color=0xffffff))
        await asyncio.sleep(1)

        #Оголошення гравцям
        if voted == self.doctor:
            if count > 2:
                await self.channel.send(embed=disnake.Embed(title=f"Гравця {voted} викинуто", description="Він був доктором"))
                self.voting = {}
                for i in self.members:
                    if i != '---':
                        self.voting[i] = 0
                await self.game_2()
            elif count <= 2:
                await self.channel.send(embed=disnake.Embed(title=f"Дон виграв {self.don}", color=0xff0000))
                await self.over_game()
        elif voted == self.don:
            await self.channel.send(embed=disnake.Embed(title=f"Гравця {voted} викинуто", description="Він був доном", color=0x000000))
            await self.channel.send(embed=disnake.Embed(title="Дон програв!"))
            await self.over_game()
        elif voted in self.peaceful_list:
            if count > 2:
                await self.channel.send(embed=disnake.Embed(title=f"Гравця {voted} викинуто", description="Він був мирним жителем", color = 0x000000))
                self.peaceful_list.remove(voted)
                self.voting = {}
                for i in self.members:
                    if i !=  '---':
                       self.voting[i] = 0
                await self.game_2()
            elif count <= 2:
                await self.channel.send(embed=disnake.Embed(title="Дон виграв!"))
                await self.over_game()
        elif voted == None:
            await self.channel.send(embed=disnake.Embed(title="Більшість вирішила не голосувати!", description="На один шанс більше для вбивці?", color = 0x000000))
            await self.game_2()

    async def over_game(self):
        await self.channel.send(embed = disnake.Embed(title = f'Вбивцею був {self.don}'))
        await self.channel.send(embed = disnake.Embed(title='Гру видалено', description='Щоб створити нову, введіть команду /start назва гри', color = 0x000000))
        await asyncio.sleep(5)
        await self.channel.delete()
        await self.roledead.delete()
        await self.rolegame.delete()

def setup(bot):
    bot.add_cog(StartGame(bot))