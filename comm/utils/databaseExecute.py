from sqlalchemy import create_engine, Table, MetaData
from sqlalchemy.orm import sessionmaker

from config import DB_CONFIG, PROJECT_NAME, DB_TYPE
from comm.utils.readYaml import read_yaml_data
DB_CONFIG = read_yaml_data(DB_CONFIG)[PROJECT_NAME]


class Database:
    def __init__(self, db_url=None):
        if db_url is None:
            driver = "psycopg2" if DB_TYPE == "postgresql" else "cx_oracle"
            db_url = f"{DB_TYPE}+{driver}://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"
        self.engine = create_engine(db_url, echo=True)
        self.Session = sessionmaker(bind=self.engine)
        self.meta = MetaData(bind=self.engine)

    def execute(self, statement):
        with self.engine.connect() as conn:
            result = conn.execute(statement)
        return result

    def query(self, table_name, filters=None, select_cols=None):
        """
        Query data
        :param table_name: indicates the table name
        : param filters: filter conditions, format for [{" column ":" xx ", "op" : "= =", "value" : "xx"},...
        :param select_cols: specifies the name of the column that you want to query. By default, all columns are queried
        :return: list of query results. Each element is a dictionary type in the format of {"column1": value1, "column2": value2,... }
        """
        table = Table(table_name, self.meta, autoload=True)
        session = self.Session()
        if not select_cols:
            query = session.query(table)
        else:
            query = session.query(*[getattr(table.c, col) for col in select_cols])
        if filters:
            for f in filters:
                column = getattr(table.c, f["column"], None)
                if column is not None:
                    if f["op"] == "==":
                        query = query.where(column == f["value"])
                    elif f["op"] == "!=":
                        query = query.where(column != f["value"])
                    elif f["op"] == ">":
                        query = query.where(column > f["value"])
                    elif f["op"] == ">=":
                        query = query.where(column >= f["value"])
                    elif f["op"] == "<":
                        query = query.where(column < f["value"])
                    elif f["op"] == "<=":
                        query = query.where(column <= f["value"])
                    elif f["op"] == "in":
                        query = query.where(column.in_(f["value"]))
                    elif f["op"] == "not in":
                        query = query.where(~column.in_(f["value"]))

            # Logical operation between multiple search conditions. The default value is AND
            query = query.where(*[clause for clause in query._where_criteria if clause is not None])

        rows = session.execute(query).fetchall()
        result = [dict(row) for row in rows]
        return result


if __name__ == '__main__':
    # SELECT AGILE_ENTITY_ID FROM PPM_INT_AGILE_ENTITY_MAP WHERE PPM_REQUEST_ID=30154
    print(Database().query("ppm_int_agile_entity_map", [{"column": "ppm_request_id", "op": "==", "value": "30154"}], ["agile_entity_id"]))