from . import users
from . import root
from . import authentication
from . import profiles
from . import items
from . import transactions
from . import categories
from . import tags
from . import requests
def init_router(app):
    app.include_router(root.router)
    app.include_router(profiles.router)
    app.include_router(users.router)
    app.include_router(authentication.router)
    app.include_router(items.router)
    app.include_router(transactions.router)
    app.include_router(categories.router)
    app.include_router(tags.router)
    app.include_router(requests.router)





