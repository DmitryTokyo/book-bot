from environs import Env
from bot import app

env = Env()

if __name__ == "__main__":
    env.read_env()
    app.run()