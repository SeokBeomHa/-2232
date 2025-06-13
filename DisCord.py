import discord
from discord.ext import commands
import os

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)
        
#환영메시지 START
@bot.event  # 신규인원 입장 시 멘트 발생
async def on_member_join(member):
    channel_name = '입장'

    for channel in member.guild.text_channels:
        if channel.name == channel_name:
            welcome_message = (
                f"{member.mention}님, 단월길드 서버에 오신 것을 환영합니다.\n\n"
                "먼저, 단월길드 공지사항 확인을 위해 '공지체크' 역할을 드렸습니다.\n\n"
                '"안내" 카테고리 내용 숙지 후 각 내용에 :white_check_mark: 체크 필수!.\n'
                f"궁금한 점은 운영진 개인 DM,완료하시면 '체크'(단월봇 접속시) 써주시면 됩니다."
            )
            await channel.send(welcome_message)
            break
    # 역할 자동 부여
    role_name = "공지체크"
    role = discord.utils.get(member.guild.roles, name=role_name)
    if role:
        await member.add_roles(role)
#환영메시지END

#입장채널 신입변경START
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if message.channel.name == '입장' and '체크' in message.content:
        welcome_message = (
            f"{message.author.mention}님, 단월 길드 신입으로 오신거 축하드립니다.같이 열심히 합시다!!"
        )
        await message.channel.send(welcome_message)
        
        # 역할 자동 부여
        role_name = "신입"
        role = discord.utils.get(message.guild.roles, name=role_name)
        if role and role not in message.author.roles:
            await message.author.add_roles(role)

    await bot.process_commands(message)
#입장채널 운영자 채널 신입변경STOP



#모든길드원 DM보내기 명령어 "!공지디엠 링크" START
@bot.command()
@commands.has_permissions(administrator=True)  # 관리자만 사용 가능
async def 공지디엠(ctx, link: str):
    role_names = ["운영진", "정예", "일반", "신입"]
    message_text = (
        "안녕하세요, 단원 길마 계약조건 입니다.\n"
        "모두 읽어보셔야하는 내용이 있어 공유 드립니다.\n"
        f"({link})"
    )
    sent_members = set()  # 중복 DM 방지

    for role_name in role_names:
        role = discord.utils.get(ctx.guild.roles, name=role_name)
        if role:
            for member in role.members:
                if member.bot or member.id in sent_members:
                    continue
                try:
                    await member.send(message_text)
                    sent_members.add(member.id)
                except discord.Forbidden:
                    pass  # DM 차단 등 예외 무시

    await ctx.send("DM 발송이 완료되었습니다.")
#모든길드원 DM보내기 명령어 "!공지디엠 링크" END






#공지 미체크 인원 확인 명령어 "!공지조사" START
@bot.command(name="공지조사")
@commands.has_permissions(administrator=True)
async def 체크미실행(ctx):
    category = discord.utils.get(ctx.guild.categories, name="안내")
    if not category:
        await ctx.send("안내 카테고리를 찾을 수 없습니다.")
        return

    channel_names = ["공지사항", "안내사항", "규칙"]
    all_members = [member for member in ctx.guild.members if not member.bot]
    result_lines = []

    for channel_name in channel_names:
        channel = discord.utils.get(category.text_channels, name=channel_name)
        if not channel:
            result_lines.append(f"{channel_name} 채널을 찾을 수 없습니다.")
            continue

        async for message in channel.history(limit=50):
            reaction = discord.utils.get(message.reactions, emoji='✅')
            if reaction:
                users = [user async for user in reaction.users()]
                checked_ids = [user.id for user in users if not user.bot]
            else:
                checked_ids = []

            unchecked_members = [
                member.display_name
                for member in all_members
                if member.id not in checked_ids
            ]

            message_link = f"https://discord.com/channels/{ctx.guild.id}/{channel.id}/{message.id}"

            if unchecked_members:
                result_lines.append(
                    f"[{channel_name} 체크 미진행 내용]({message_link}) 멤버: {', '.join(unchecked_members)}"
                )
            else:
                result_lines.append(
                    f"{channel_name}: 모든 길드원 체크 완료했습니다."
                )

    # 한 번에 출력 (디스코드 메시지 최대 길이 2000자 제한)
    result_text = "\n".join(result_lines)
    for chunk in [result_text[i:i+1900] for i in range(0, len(result_text), 1900)]:
        await ctx.send(chunk)
#공지 미체크 인원 확인 명령어 "!공지조사" END









#공지 미체크 인원 확인 명령어 "!공지조사언급" START
@bot.command(name="공지조사언급")
@commands.has_permissions(administrator=True)
async def 체크미실행(ctx):
    category = discord.utils.get(ctx.guild.categories, name="안내")
    if not category:
        await ctx.send("안내 카테고리를 찾을 수 없습니다.")
        return

    channel_names = ["공지사항", "안내사항", "규칙"]
    all_members = [member for member in ctx.guild.members if not member.bot]
    result_lines = []

    for channel_name in channel_names:
        channel = discord.utils.get(category.text_channels, name=channel_name)
        if not channel:
            result_lines.append(f"{channel_name} 채널을 찾을 수 없습니다.")
            continue

        async for message in channel.history(limit=50):
            reaction = discord.utils.get(message.reactions, emoji='✅')
            if reaction:
                users = [user async for user in reaction.users()]
                checked_ids = [user.id for user in users if not user.bot]
            else:
                checked_ids = []

            unchecked_members = [
                member.mention
                for member in all_members
                if member.id not in checked_ids
            ]

            message_link = f"https://discord.com/channels/{ctx.guild.id}/{channel.id}/{message.id}"

            if unchecked_members:
                result_lines.append(
                    f"[{channel_name} 체크 미진행 내용]({message_link}) 멤버: {', '.join(unchecked_members)}"
                )
            else:
                result_lines.append(
                    f"{channel_name}: 모든 길드원 체크 완료했습니다."
                )

    # 한 줄씩 띄워서 출력
    result_text = "\n\n".join(result_lines)
    for chunk in [result_text[i:i+1900] for i in range(0, len(result_text), 1900)]:
        await ctx.send(chunk)

#공지 미체크 인원 확인 명령어 "!공지조사언급" END




#예비기능
@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')
#예비기능



















# 디스코드 토큰, 삭제 금지
TOKEN = os.environ.get("DISCORD_TOKEN")
bot.run(TOKEN)
# 디스코드 토큰, 삭제 금지
