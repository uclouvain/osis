from learning_unit.auth.roles import central_manager
from osis_role import role

role.role_manager.register(central_manager.CentralManager)
