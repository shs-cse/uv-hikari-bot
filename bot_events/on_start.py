import hikari, crescent
import sync_with_state.init, sync_with_state.roles
from bot_environment import state
from bot_environment.config import EnrolmentSprdsht, InfoKey
from wrappers.pygs import get_sheet_by_name
from wrappers.utils import FormatText
from view_components.student_verification.modal_and_button import VerificationButtonView
from view_components.faculty_verification.assign_sec_button import AssignSectionsButtonView
from view_components.marks.button_fetch import ShowMarksView

plugin = crescent.Plugin[hikari.GatewayBot, None]()


@plugin.include
@crescent.event  # after connecting to discord
async def on_started(event: hikari.StartedEvent) -> None:
    await sync_with_state.init.now(event)
    await sync_with_state.roles.now()
    # start member verification buttons
    verification_button_views = (VerificationButtonView(), AssignSectionsButtonView())
    for button_view in verification_button_views:
        state.miru_client.start_view(button_view, bind_to=None)
    # start marks buttons
    for section, assessments in state.info[InfoKey.MARKS_BUTTONS].items():
        section = int(section)
        for assessment in assessments:
            button_view = ShowMarksView(section, assessment)
            state.miru_client.start_view(button_view, bind_to=None)
    print(FormatText.success(FormatText.bold("Bot has started.")))
    # warn user if enrolment is empty by accident
    if state.students.empty:
        enrolment_sheet_id = state.info[InfoKey.ENROLMENT_SHEET_ID]
        connect_sheet = get_sheet_by_name(enrolment_sheet_id, EnrolmentSprdsht.Connect.TITLE)
        log = "Student list in Enrolment spreadsheet is empty. Please fill in the"
        log += f" '{connect_sheet.title}' sheet (linked above ↑)"
        log += " and then run the '/sync enrolment' command in discord."
        print(FormatText.error(log))
    await plugin.app.update_presence(status=hikari.Status.ONLINE)
