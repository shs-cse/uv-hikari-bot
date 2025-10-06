import re, hikari
from bot_environment.config import RegexPattern
from wrappers.utils import FormatText
from member_verification.response import Response, VerificationFailure
from member_verification.faculty.success import assign_faculty_section_roles
from member_verification.faculty.failure import (check_if_member_is_a_faculty, 
                                                 check_faculty_nickname_pattern)

async def try_faculty_verification(member: hikari.Member) -> Response:
    try:
        await check_if_member_is_a_faculty(member)
        log = f"Checked that Member is a Faculty: {member.mention} {member.display_name}"
        print(FormatText.success(log))
    except VerificationFailure as failure:
        return failure.response
    try:
        print(FormatText.wait(f"Verifying Faculty {member.mention} {member.display_name}..."))
        extracted_initial_ish = re.search(RegexPattern.FACULTY_NICKNAME, member.display_name)
        extracted_initial = await check_faculty_nickname_pattern(member, extracted_initial_ish)
        initial = extracted_initial.group(1)
        response = await assign_faculty_section_roles(member, initial)
        print(FormatText.success(f"Verified Faculty {member.mention} {member.display_name}."))
        return response
    except VerificationFailure as failure:
        return failure.response
    

