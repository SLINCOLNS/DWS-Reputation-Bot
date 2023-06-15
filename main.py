import disnake
import asyncio
from disnake.ext import commands
import json
import os


# Получение полного пути к файлу ratings.json
def get_ratings_filepath():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(current_dir, 'ratings.json')

def load_ratings():
    filepath = get_ratings_filepath()
    try:
        with open(filepath, 'r') as file:
            ratings = json.load(file)
    except FileNotFoundError:
        print(f"Файл {filepath} не найден.")
        ratings = {}
    except json.JSONDecodeError:
        print(f"Ошибка при декодировании файла {filepath}.")
        ratings = {}

    return ratings


def get_top_ratings():
    ratings = load_ratings()
    sorted_ratings = sorted(ratings.items(), key=lambda x: x[1], reverse=True)
    guild = bot.get_guild(GUILD_ID)
    top_ratings = []

    for user_id, rating in sorted_ratings:
        member = guild.get_member(int(user_id))
        member_name = member.display_name if member else f"Unknown User ({user_id})"
        top_ratings.append((member_name, rating))

    return top_ratings[:10]


# Сохранение рейтинга в файл
# Сохранение рейтинга в файл

def save_ratings(ratings):
    filepath = get_ratings_filepath()
    with open(filepath, 'w') as file:
        json.dump(ratings, file)


intents = disnake.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="+", help_command=None, intents=intents)
reputations = {}
ratings = load_ratings()  # Load ratings on bot startup

allowed_channel_id_rep = 1118537088892149820
allowed_channel_id_reputation = 1104747800220139620
GUILD_ID = 1104497017222348814

def in_allowed_channel_rep():
    async def predicate(ctx):
        return ctx.channel.id == allowed_channel_id_rep
    return commands.check(predicate)

def in_allowed_channel_reputation():
    async def predicate(ctx):
        return ctx.channel.id == allowed_channel_id_reputation
    return commands.check(predicate)

@bot.event
async def on_message(message):
    if message.channel.id == allowed_channel_id_rep and not message.content.startswith("+rep") and not message.content.startswith("-rep") and not message.author.bot:
        await message.delete()
    await bot.process_commands(message)

log_channel_id = 1118806465931640843

@bot.event
async def on_ready():
    print(f"Bot {bot.user} is ready to work!")
    await bot.change_presence(activity=disnake.Game(name="+help"))
    ratings = load_ratings()
    print('Loaded ratings:', ratings)

    log_channel = bot.get_channel(log_channel_id)
    if log_channel:
        embed = disnake.Embed(
            title="Статус бота",
            description="Бот успешно запущен и стабильно работает",
            color=disnake.Color.green()
        )
        await log_channel.send(embed=embed)

@bot.command()
async def stat(ctx):
    if bot.is_closed():
        await bot.login('MTExODI1NTc0NjQwOTMxNjQxMw.GnDg8u.Ry1m_WlhWqjAUZupIkyAfxuCpQMPoJaM4qUOYw')  # Подключение бота, если он был выключен
        await bot.connect()  # Соединение с Discord API
    if bot.is_ready():
        embed = disnake.Embed(
            title="Статус бота",
            description="Бот успешно запущен и стабильно работает",
            color=disnake.Color.green()
        )
    else:
        embed = disnake.Embed(
            title="Статус бота",
            description="Бот был выключен или не был запущен",
            color=disnake.Color.red()
        )
    await ctx.send(embed=embed)

@bot.command()
async def top(ctx):
    top_ratings = get_top_ratings()

    if not top_ratings:
        response_embed = disnake.Embed(
            title="Топ рейтинга",
            description="Рейтинг пуст.",
            color=disnake.Color.blue()
        )
        await ctx.send(embed=response_embed)
        return

    response_embed = disnake.Embed(
        title="Топ рейтинга",
        description="Топ 10 пользователей по рейтингу:",
        color=disnake.Color.blue()
    )
    ratings = load_ratings()

    for index, (member_id, rating) in enumerate(top_ratings, start=1):
        guild = bot.get_guild(GUILD_ID)
        member = guild.get_member(int(member_id))
        member_name = member.display_name if member else f"Unknown User ({member_id})"
        response_embed.add_field(name=f"#{index}: {member_name}", value=f"Рейтинг: {rating}", inline=False)

    await ctx.send(embed=response_embed)



@bot.command()
@in_allowed_channel_rep()
async def rep(ctx, member: disnake.Member = None, *, comment: str = ""):
    if member is None:
        error_embed = disnake.Embed(
            title="+rep",
            description="Вы не упомянули пользователя, которому хотите дать репутацию.",
            color=disnake.Color.red()
        )
        error_message = await ctx.send(embed=error_embed)
        await error_message.delete(delay=5)
        await ctx.message.delete()
        return

    sender = ctx.author
    if member.id == sender.id:
        error_embed = disnake.Embed(
            title="+rep",
            description="Вы не можете дать репутацию самому себе!",
            color=disnake.Color.red()
        )
        error_message = await ctx.send(embed=error_embed)
        await error_message.delete(delay=5)
        await ctx.message.delete()
        return

    if member.id not in reputations:
        reputations[member.id] = 0

    reputations[member.id] += 1
    save_ratings(reputations)
    comment_text = f"Комментарий: {comment}\n" if comment else ""
    member_name = member.display_name if member else f"Unknown User ({member.id})"
    response_embed = disnake.Embed(
        title="+rep",
        description=f'📈  Пользователь **{sender.mention}** поблагодарил пользователя **{member.mention}**.\n{comment_text}',
        color=disnake.Color.green()
    )
    await ctx.send(embed=response_embed)

    await ctx.message.delete()

@bot.command()
@in_allowed_channel_reputation()
async def reputation(ctx, member: disnake.Member):
    ratings = load_ratings()
    reputation = ratings.get(str(member.id), 0)
    reputation_embed = disnake.Embed(
        title="📈 Репутация",
        description=f"У пользователя {member.mention} репутации: **{reputation}**",
        color=disnake.Color.green()
    )
    response_message = await ctx.send(embed=reputation_embed)

    await asyncio.sleep(10)  # Измените время на необходимое вам (в секундах)
    try:
        await response_message.delete()
    except disnake.NotFound:
        pass

    await ctx.message.delete()




@bot.command()
async def help(ctx):
    """
    Список команд бота.
    Использование: +help
    """
    help_embed = disnake.Embed(
        title="Список команд",
        description="Список всех доступных команд бота",
        color=disnake.Color.blue()
    )
    help_embed.add_field(name="+rep @пользователь", value="Дать репутацию пользователю", inline=False)
    help_embed.add_field(name="+unrep @пользователь", value="Убавить репутацию пользователю", inline=False)
    help_embed.add_field(name="+reputation @пользователь", value="Показать репутацию пользователя", inline=False)
    help_embed.add_field(name="**+help @пользователь**", value="Показать все доступные команды", inline=False)

    await ctx.send(embed=help_embed)

@bot.command()
@in_allowed_channel_rep()
async def unrep(ctx, member: disnake.Member, *, comment: str = ""):
    """
    Убавить репутацию пользователю.
    Использование: +unrep @пользователь
    """
    if member.id not in reputations:
        reputations[member.id] = 0

    reputations[member.id] -= 1
    save_ratings(reputations)
    comment_text = f"Комментарий: {comment}\n" if comment else ""
    member_name = member.display_name if member else f"Unknown User ({member.id})"

    response_embed = disnake.Embed(
        title="-rep",
        description=f'📉  Пользователь **{ctx.author.mention}** убавил репутацию пользователю **{member.mention}**.\n{comment_text}',
        color=disnake.Color.red()
    )
    await ctx.send(embed=response_embed)

    await ctx.message.delete()

@bot.command()
@disnake.ext.commands.has_permissions(administrator=True)
async def setrep(ctx, member: disnake.Member, reputation: int):
    reputations[member.id] = reputation
    save_ratings(reputations)
    response_embed = disnake.Embed(
        title="Установка репутации",
        description=f"Администратор **{ctx.author.mention}** установил репутацию пользователя **{member.mention}** на {reputation}.",
        color=disnake.Color.green()
    )
    response_message = await ctx.send(embed=response_embed)


@bot.command()
async def rhelp(ctx):
    """
    Помощь по командам бота.
    Использование: +rhelp
    """
    rhelp_embed = disnake.Embed(
        title="Список команд",
        description="Список всех доступных команд бота",
        color=disnake.Color.blue()
    )
    rhelp_embed.set_author(name="Помощь по командам", icon_url=bot.user.avatar.url)
    rhelp_embed.add_field(name="**+rep @пользователь**", value="Дать репутацию пользователю", inline=False)
    rhelp_embed.add_field(name="**+unrep @пользователь**", value="Убавить репутацию пользователю", inline=False)
    rhelp_embed.add_field(name="**+reputation @пользователь**", value="Показать репутацию пользователя", inline=False)
    rhelp_embed.add_field(name="**+rhelp @пользователь**", value="Показать все доступные команды", inline=False)

    help_message = await ctx.send(embed=rhelp_embed)

    await asyncio.sleep(15)  # Измените время на необходимое вам (в секундах)
    try:
        await ctx.message.delete()
        await help_message.delete()
    except disnake.NotFound:
        pass

bot.run("MTExODI1NTc0NjQwOTMxNjQxMw.GnDg8u.Ry1m_WlhWqjAUZupIkyAfxuCpQMPoJaM4qUOYw")
