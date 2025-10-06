import hikari, crescent
from bot_environment.config import RolePermissions
from member_verification.faculty.success import assign_faculty_section_roles
from member_verification.response import get_generic_error_response_while_verifying
from wrappers.utils import FormatText


plugin = crescent.Plugin[hikari.GatewayBot, None]()