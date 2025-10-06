import hikari, crescent
from bot_environment import state
from member_verification.faculty.check import try_faculty_verification
from wrappers.utils import FormatText

plugin = crescent.Plugin[hikari.GatewayBot, None]()

@plugin.include
@crescent.event
async def on_faculty_guild_nickname_change(event: hikari.MemberUpdateEvent) -> None:
    # if faculty name changes in faculty guild, update cache
    if event.guild_id != state.eee_guild.id:
        return
    if event.member.is_bot:
        return
    new_name = event.member.display_name
    old_name = event.old_member.display_name
    if new_name == old_name:
        return
    log = f"Display name of {event.member.mention} has been changed in {state.eee_guild.name}"
    log += f" from '{old_name}' to '{new_name}'"
    print(FormatText.warning(log))
    # change member name in state.guild
    faculty = state.guild.get_member(event.member.user.id)
    log = f"Changing Nickname: {faculty.mention} {faculty.display_name} -> {new_name}..."
    faculty = await faculty.edit(nickname=new_name)
    # faculty.nickname = new_name # bug fix hack
    print(FormatText.status(log))
    await try_faculty_verification(faculty)
    