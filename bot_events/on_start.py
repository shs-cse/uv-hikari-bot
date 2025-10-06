import hikari, crescent
import sync_with_state.init, sync_with_state.roles, sync_with_state.sheets
from bot_environment import state
from wrappers.utils import FormatText
from member_verification.faculty.success import assign_faculty_section_roles
from view_components.student_verification.modal_and_button import VerificationButtonView
from view_components.faculty_verification.assign_sec_button import AssignSectionsButtonView

plugin = crescent.Plugin[hikari.GatewayBot, None]()


@plugin.include
@crescent.event # after connecting to discord
async def on_started(event: hikari.StartedEvent) -> None:
    await sync_with_state.init.now(event)
    await sync_with_state.roles.now()
    await plugin.app.update_presence(status=hikari.Status.ONLINE)
    button_views = [VerificationButtonView(), AssignSectionsButtonView()]
    for button_view in button_views:
        state.miru_client.start_view(button_view, bind_to=None)
    print(FormatText.success(FormatText.bold("Bot has started.")))
