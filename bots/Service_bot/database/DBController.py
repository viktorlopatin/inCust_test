from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey

#Подключение к БД
class DBConnect(object):
	
	def __init__(self):
		super(DBConnect, self).__init__()
		self.DATABASE_NAME = 'database.db'
		self.engine = create_engine(f'sqlite:///{self.DATABASE_NAME}')
		self.Session = sessionmaker(bind=self.engine)
		self.Base = declarative_base()
		self.session = None


	def start_db(self):
		self.Base.metadata.create_all(self.engine)
		self.session = Session()

	def create_session(self):
		return self.Session()

#Создание таблиц
DB = DBConnect()
class User(DB.Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    chat_id = Column(Integer)
    name = Column(String)
    username = Column(String)
    in_client_bot = Column(Boolean)
    in_service_bot = Column(Boolean)
    with_chat = Column(Integer)
    

    def __init__(self, chat_id: int, name: str, username: str, in_client_bot: bool, in_service_bot: bool, with_chat: int):
        self.chat_id = chat_id
        self.name = name
        self.username = username
        self.in_client_bot = in_client_bot
        self.in_service_bot = in_service_bot
        self.with_chat = with_chat


class Event(DB.Base):
	__tablename__ = 'events'

	id = Column(Integer, primary_key=True)
	user_id = Column(Integer)
	nameEvent = Column(String)
	title = Column(String)
	description = Column(String)
	media_type = Column(String)
	media = Column(String)
	endDate = Column(String)

    

	def __init__(self, user_id: int, nameEvent: str, title: str, description: str, media_type: str, media: str, endDate: str):
		self.user_id = user_id
		self.nameEvent = nameEvent
		self.title = title
		self.description = description
		self.media_type = media_type
		self.media = media
		self.endDate = endDate

		
#Работа с запросами к БД
class DBController(object):
	"""docstring for DBController"""
	def __init__(self):
		super(DBController, self).__init__()
		self.DB = DB
		self.DB.Base.metadata.create_all(self.DB.engine)
		self.session = self.DB.Session()


	#Добавить ползователя в БД
	async def addUser(self, user: User): 
		self.session.add(user)
		self.session.commit()

	#Найти пользователя
	async def getUser(self, chat_id):
		try:
			user = self.session.query(User).filter_by(chat_id=chat_id)[0]
			return user
		except Exception as e:
			return None

	#Добавить Event
	async def addEvent(self, event: Event): 
		self.session.add(event)
		self.session.commit()

	async def getEvents(self):
		Events = self.session.query(Event).all()
		return Events

	async def getEvent(self, event_id):
		try:
			event = self.session.query(Event).filter_by(id=event_id)[0]
			return event
		except Exception as e:
			return None

	async def delEvent(self, event_id):
		self.session.query(Event).filter(Event.id==event_id).delete()
		self.session.commit()

	async def commit(self):
		self.session.commit()

db = DBController()

