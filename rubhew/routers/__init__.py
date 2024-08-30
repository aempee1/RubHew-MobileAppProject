from . import users
from . import root
from . import authentication
from . import profiles
from . import items

def init_router(app):
    app.include_router(root.router)
    app.include_router(profiles.router)
    app.include_router(users.router)
    app.include_router(authentication.router)
    app.include_router(items.router)




