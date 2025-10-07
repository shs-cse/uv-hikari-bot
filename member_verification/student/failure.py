import hikari
from bot_environment import state
from bot_environment.config import EnrolmentSprdsht, DisplayName
from member_verification.response import Response, VerificationFailure
from wrappers.utils import FormatText
from view_components.student_verification.yes_no_button import YesNoButtonsView


# Case 0: retyped input does not match
def check_retyped_user_input(input_text:str, reinput_text:str) -> None:
    if reinput_text != input_text:
        log = f"Student Verification: Someone's entered input ({input_text})"
        log += f" doesn't match retyped input ({reinput_text})."
        print(FormatText.warning(log))
        comment = "### Inputs Don't Match\nPlease try again. Your inputs"
        comment += f" `{input_text}` and `{reinput_text}` does not match."
        raise VerificationFailure(Response(comment))
    
# Case 1: id is not a valid student id
def check_if_input_is_a_valid_id(input_text: str, extracted: str) -> None:
    if extracted:
        return # silently fall through to next check
    log = f"Student Verification: Someone's input ({input_text}) is not a valid student ID."
    print(FormatText.warning(log))
    comment = "### Input is Not Valid\nPlease try again. Your input"
    comment += f" `{input_text}` is not a valid student ID."
    raise VerificationFailure(Response(comment))
    
# Case 2: id is valid but not in the sheet
def check_if_student_id_is_in_database(student_id:int) -> None:
    if student_id in state.students.index:
        return # silently fall through to next check
    log = f"Student Verification: Student ({student_id}) not in course enrolment."
    print(FormatText.warning(log))
    comment = f"### ID Not in Database\n`{student_id}` is not in our database."
    comment += " Please double check your student ID and try again."
    raise VerificationFailure(Response(comment))
    
# Case 3: id is valid and in the sheet, but already taken (by another student/their old id)
def check_if_student_id_is_already_taken(member: hikari.Member, student_id:int) -> None:
    existing_member: hikari.Member = None
    for _, mem in state.guild.get_members().items():
        if mem.get_top_role() == state.student_role:
            if DisplayName.fmt(DisplayName.STUDENT, student_id, '') in mem.display_name:
                if mem.id != member.id:
                    existing_member = mem
                    break
    if existing_member: # taken by another student -> contact admin
        log = f"Student Verification: {mem.mention} tried to take ({student_id});"
        log += f" but {existing_member.mention} already took it."
        print(FormatText.warning(log))
        comment = f"### ID Already Taken\n`{student_id}` is already taken"
        comment += f" by {existing_member.mention}.  If this is your old discord account"
        comment += " and you want to use this new one,"
        comment += " please leave the sever from your old account first."
        comment += " Then try again with your new account."
        comment += " If someone else took your ID, Please report to admins ASAP."
        raise VerificationFailure(Response(comment))
    

# Case 4: id is valid and in the sheet, but discord acc mismatch with advising server (you sure?)
async def check_if_matches_advising_server(member:hikari.Member, student_id:int) -> None:
    ADVISING_DISCORD_ID_COL = EnrolmentSprdsht.Students.ADVISING_DISCORD_ID_COL
    NAME_COL = EnrolmentSprdsht.Students.NAME_COL
    # check advising discord id
    advising_id = state.students.loc[student_id, ADVISING_DISCORD_ID_COL]
    if not advising_id: # not in our advising database
        return
    if member.id in state.students[ADVISING_DISCORD_ID_COL]:
        conflict_id = state.students[state.students[ADVISING_DISCORD_ID_COL] == member.id]
        conflict_name = state.students.loc[conflict_id, NAME_COL]
        student_name = state.students.loc[student_id, NAME_COL]
        log = f"Student Verification: {member.mention} tried to take ({student_id});"
        log += f" but advising server points to <@{advising_id}>."
        print(FormatText.warning(log))
        student_display_name = DisplayName.fmt(DisplayName.STUDENT, student_id, student_name)
        conflict_display_name = DisplayName.fmt(DisplayName.STUDENT, conflict_id, conflict_name)
        comment = "Your discord account is verified as"
        comment += f" `{conflict_display_name}` in the advising server."
        comment += " However, you are trying to get verified as"
        comment += f" `{student_display_name}`."
        comment += "If you think this is an error, please contact admins with proper proof."
        raise VerificationFailure(Response(comment))
    # member probably has alt account -> sure?
    else:
        log = f"Student Verification: {member.mention} tried to take ({student_id}), alt account?"
        print(FormatText.warning(log))
        comment = f"### Alt Account?\n`{student_id}` was used by account with discord account"
        comment += f" <@{advising_id}> in the advising server."
        comment += " We recommend using the same discord account for both servers."
        comment += f" Are you sure you want to use this account ({member.mention}) with"
        comment += f" student id `{student_id}` for this server?"
        raise VerificationFailure(Response(comment, kind=Response.Kind.WAITING, 
                                        components=YesNoButtonsView(member,student_id)))