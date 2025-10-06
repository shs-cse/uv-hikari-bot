import re, hikari
from bot_environment import state
from bot_environment.config import RegexPattern
from member_verification.response import Response, VerificationFailure
from wrappers.utils import FormatText


async def check_if_member_is_a_faculty(member: hikari.Member) -> None:
    log = f"Checking if Member is a Faculty: {member.mention} {member.display_name}"
    print(FormatText.wait(log))
    # may have hard-assigned faculty role
    if state.faculty_role in member.get_roles():
        return # silently fall through to next check
    if member.id in state.eee_guild.get_members():
        await member.add_role(state.faculty_role)
        return # silently fall through to next check    
    log = f"Checked that Member is not a Faculty: {member.mention} {member.display_name}."
    log = FormatText.dim(f"{FormatText.DIM_BOLD_RESET}{log}")
    print(FormatText.warning(log))
    comment = "### Not A Faculty Member\n"
    comment += f"You neither have the {state.faculty_role.mention} role"
    comment += f" nor are you a member of the **{state.eee_guild.name}** server."
    comment += " So you can't assign sections to you."
    raise VerificationFailure(Response(comment))
    
    
async def check_faculty_nickname_pattern(faculty: hikari.Member, extracted: str) -> str:
    if extracted:
        return extracted# silently fall through to next check
    # try display name from ECT-BC server
    name_in_eee_guild = state.eee_guild.get_member(faculty.id).display_name
    extracted = re.search(RegexPattern.FACULTY_NICKNAME, name_in_eee_guild)
    if extracted:
        log = f"Changing Nickname: {faculty.mention} {faculty.display_name}"
        log += f" -> {name_in_eee_guild}..."
        print(FormatText.status(log))
        faculty = await faculty.edit(nickname=name_in_eee_guild)
        return extracted# silently fall through to next check
    log = "Failed to Verify Faculty due to nickname issue:"
    log += f" {faculty.mention} {faculty.display_name}."
    print(FormatText.error(log))
    comment = "### Nickname Not Set Properly\n"
    comment += f"Your nicknames for both this server and **{state.eee_guild.name}** server"
    comment += " is not set properly. It must be of the form: `[INITIAL] Your Name`."
    comment += f" Change your **{state.eee_guild.name}** server name, then try again."
    comment += " Some examples: \n```css\n"
    comment += "[SDS] Shadman Shahriar\n"
    comment += "[MFSQ] Md. Farhan Shadiq\n"
    comment += "[X01] Not Assigned Yet```"
    raise VerificationFailure(Response(comment))