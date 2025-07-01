import databases
import sqlalchemy
import sys
from sqlalchemy import text
from storeapi.config import config

metadata = sqlalchemy.MetaData()

post_table = sqlalchemy.Table(
    "posts",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("body", sqlalchemy.String(255))
)

comment_table = sqlalchemy.Table(
    "comments",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("body", sqlalchemy.String(255)),
    sqlalchemy.Column("post_id", sqlalchemy.ForeignKey("posts.id"), nullable=False)
)

engine = sqlalchemy.create_engine(
    config.DATABASE_URL,
    connect_args={
        "charset": "utf8mb4",
        "use_unicode": True,
        "connect_timeout": 10
    },
    pool_recycle=3600,
    pool_size=10,
    pool_pre_ping=True,
    max_overflow=20
)

# SQLAlchemy에서 테이블 생성 시 기본 문자셋과 콜레이션 설정
@sqlalchemy.event.listens_for(metadata, "before_create")
def _set_mysql_charset(metadata, connection, **kw):
    """Set default charset and collation for MySQL tables."""
    if connection.dialect.name == 'mysql':
        connection.execute(text('SET character_set_server = utf8mb4'))
        connection.execute(text('SET collation_server = utf8mb4_unicode_ci'))


# 데이터베이스 연결 시 시간대 설정
@sqlalchemy.event.listens_for(engine, "connect")
def set_timezone(dbapi_connection, connection_record):
    """Set timezone to UTC when connecting to database."""
    if hasattr(dbapi_connection, "execute"):
        dbapi_connection.execute("SET time_zone = '+00:00'")


# 테이블 생성 대신 검증만 수행하는 함수
def validate_tables():
    """
    Validates the database table structure.
    Checks if tables exist and terminates the server if any are missing.
    """
    inspector = sqlalchemy.inspect(engine)
    
    # 정의된 테이블 목록
    defined_tables = metadata.tables.keys()
    # 실제 데이터베이스에 존재하는 테이블 목록
    existing_tables = inspector.get_table_names()
    
    # 누락된 테이블 확인
    missing_tables = set(defined_tables) - set(existing_tables)
    if missing_tables:
        print(f"ERROR: The following tables do not exist in the database: {', '.join(missing_tables)}")
        print("To create tables, enable the CREATE_TABLES setting.")
        sys.exit(1)  # 오류 코드 1로 프로그램 종료
    
    # 각 테이블의 컬럼 구조 검증
    for table_name in defined_tables:
        if table_name in existing_tables:
            # 정의된 컬럼 가져오기
            defined_columns = {c.name: c for c in metadata.tables[table_name].columns}
            # 실제 컬럼 가져오기
            existing_columns = {c['name']: c for c in inspector.get_columns(table_name)}
            
            # 누락된 컬럼 확인
            missing_columns = set(defined_columns.keys()) - set(existing_columns.keys())
            if missing_columns:
                print(f"ERROR: The following columns are missing in table '{table_name}': {', '.join(missing_columns)}")
                sys.exit(1)  # 오류 코드 1로 프로그램 종료
    
    print("All table structures are valid.")
    return True

# 테이블을 생성하는 함수
def create_tables():
    """
    Creates all defined tables in the database.
    First drops existing tables if they exist.
    """
    # 기존 테이블 삭제
    metadata.drop_all(engine)
    print("Existing tables have been dropped.")
    
    # 테이블 새로 생성
    metadata.create_all(engine)
    print("Tables have been created successfully.")

# 데이터베이스 객체 생성
database = databases.Database(config.DATABASE_URL)

# 설정에 따라 테이블 자동 생성 또는 검증만 수행
if hasattr(config, 'CREATE_TABLES') and config.CREATE_TABLES:
    create_tables()
else:
    validate_tables()
