from pony.orm import Database, Required, Json

from settings import DB_CONFIG



db = Database()

db.bind(**DB_CONFIG)  # Настройки бд взяты из settings.py


# Create table (entity) with row
class UserState(db.Entity):  # Entity - сущность
    """
        user states inside the scenario
    """
    scenario_name = Required(str)  # Required - define the type
    step_name = Required(str)  # Required - требуемый, необходимый
    context = Required(Json)  # context - dict, because type is Json   # context is defined in handlers.py
    user_id = Required(str, unique=True)  # UNIQUE!


class Registration (db.Entity):   # Create table registration
    """
    registration application
    """
    name = Required(str)
    email = Required(str)



db.generate_mapping(create_tables=True)  # mapping - отображение (в самом низу находиться должна запись)

