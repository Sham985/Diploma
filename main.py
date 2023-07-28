from sqlalchemy.orm import declarative_base
from sqlalchemy import create_engine
from interface import BotInterface
from config import community_token, acces_token, db_url_object

def main():
    engine = create_engine(db_url_object, echo = True)
    Base = declarative_base()
    Base.metadata.create_all(engine)
    bot_interface = BotInterface(community_token, acces_token, engine = engine)
    bot_interface.event_handler()


if __name__ == '__main__':
    main()