from dotenv import load_dotenv
from infrastructure.config import load

load_dotenv('.env.local')


conf = load()