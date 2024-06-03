from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Index, inspect
from sqlalchemy.orm import sessionmaker

class SQLAlchemyManager:
    def __init__(self, db_name: str = 'postgres'):
        try:
            self.engine = create_engine(
                f'postgresql://lada:lada@postgres:5432/{db_name}')
            self.metadata = MetaData()
            self.metadata.bind = self.engine
            self.Session = sessionmaker(bind=self.engine)
        except Exception as e:
            print(e)

    def create_tables(self):
        users = Table(
            'users', self.metadata,
            Column('id', Integer, primary_key=True),
            Column('login', String(255), unique=True, nullable=False),
            Column('password', String(255), nullable=False),
            Column('name', String(255), nullable=False),
            Column('last_name', String(255)),
            Column('mail', String(255))
        )

        self.metadata.create_all(self.engine)

        Index('id_index', users.c.id)
        Index('login_index', users.c.login)
        Index('name_index', users.c.name)
        Index('last_name_index', users.c.last_name)
        Index('mail_index', users.c.mail)

    def insert_data(self, data, table_name):
        session = self.Session()
        table = self.metadata.tables[table_name]
        session.execute(table.insert(), data)
        session.commit()
        session.close()

    def delete_table(self, table_name):
        self.metadata.reflect(bind=self.engine)
        if table_name in self.metadata.tables:
            table = self.metadata.tables[table_name]
            table.drop(bind=self.engine)
            self.metadata.clear()
            print(f"Table {table_name} was dropped")
        else:
            print(f"Table {table_name} not found")

    def init_database(self):
        inspector = inspect(self.engine)
        if inspector.has_table("users"):
            self.delete_table("users")
        print("Initializing DB")
        self.create_tables()
        sample_data = [
            {'login': '12', 'password': 'gh23bd3hXXE', 'name': 'Alan', 'last_name': 'Kross', 'mail': 'alan1@example.com'},
            {'login': '34', 'password': 'opwk$gye67', 'name': 'Ivan', 'last_name': 'Ivanov', 'mail': 'ivan2@example.com'},
            {'login': '56', 'password': 'kiowkx882!)wj', 'name': 'Kate', 'last_name': 'Solnceva', 'mail': 'kate3@example.com'}
        ]
        self.insert_data(sample_data, "users")

sqlalchemy_manager = SQLAlchemyManager(db_name="archdb")
sqlalchemy_manager.init_database()
print("Database successfully initialized with new schema")
