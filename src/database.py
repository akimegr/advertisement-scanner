# src/database.py
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, BigInteger, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from config import POSTGRESQL
from src import constants

Base = declarative_base()

class Link(Base):
    __tablename__ = 'links'

    id = Column(Integer, primary_key=True, autoincrement=True)
    url = Column(String, nullable=False)
    kufar_div_class_before_section = Column(String, nullable=True)
    previous_adverts = Column(String, nullable=True)  # Сохраняем список ID предыдущих объявлений в виде строки

class UserLink(Base):
    __tablename__ = 'users_links'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False)
    link_id = Column(Integer, ForeignKey('links.id'), nullable=False)

    link = relationship("Link")

class Database:
    def __init__(self):
        self.engine = create_engine(
            f"postgresql+psycopg2://{POSTGRESQL['user']}:{POSTGRESQL['password']}@"
            f"{POSTGRESQL['host']}:{POSTGRESQL['port']}/{POSTGRESQL['dbname']}"
        )
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

    def get_user_by_link(self, link_id):
        session = self.Session()
        users = session.query(UserLink).filter_by(link_id=link_id)
        session.close()
        return users

    def get_links(self):
        session = self.Session()
        links = session.query(Link).all()
        session.close()
        return links

    def add_link(self, user_id, url):
        session = self.Session()

        # Проверяем, существует ли уже такая ссылка
        existing_link = session.query(Link).filter_by(url=url).first()
        if existing_link:
            link_id = existing_link.id
        else:
            # Создаем новую ссылку
            new_link = Link(url=url)
            session.add(new_link)
            session.commit()
            link_id = new_link.id

        # Добавляем связь пользователя и ссылки
        user_link = UserLink(user_id=user_id, link_id=link_id)
        session.add(user_link)
        session.commit()
        session.close()

    def get_user_links(self, user_id):
        session = self.Session()
        user_links = session.query(UserLink).filter_by(user_id=user_id).all()
        session.close()
        return user_links

    def update_previous_adverts(self, link_id, adverts):
        session = self.Session()
        link = session.query(Link).filter_by(id=link_id).first()
        if link:
            link.previous_adverts = constants.Constant.delimeter.join(adverts)  # Сохраняем идентификаторы объявлений в виде строки
            session.commit()
        session.close()

    def get_previous_adverts(self, link_id):
        session = self.Session()
        link = session.query(Link).filter_by(id=link_id).first()
        session.close()
        if link and link.previous_adverts:
            return link.previous_adverts.split(constants.Constant.delimeter)
        return None

    def close(self):
        self.engine.dispose()
