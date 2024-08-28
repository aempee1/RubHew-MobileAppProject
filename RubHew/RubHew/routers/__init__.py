from . import users
from . import root

def init_router(app):
    app.include_router(root.router)
    app.include_router(users.router)



