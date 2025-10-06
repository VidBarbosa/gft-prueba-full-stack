# Simple AWSlambda -> ASGI bridge using Mangum
from mangum import Mangum
from app.main import app

handler = Mangum(app)
