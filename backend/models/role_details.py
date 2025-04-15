"""RoleDetails extends the Role model to include the permissions and users associated with the role."""

from pydantic import BaseModel
from .user import User
from .permission import Permission
from .role import Role


__authors__ = ["Kris Jordan"]
__copyright__ = "Copyright 2023"
__license__ = "MIT"


class RoleDetails(Role):
    """
    Pydantic model to represent a `Role`, including back-populated
    relationship fields.

    This model is based on the `RoleEntity` model, which defines the shape
    of the `Role` database in the PostgreSQL database.
    """

    permissions: list[Permission]
    users: list[User]
