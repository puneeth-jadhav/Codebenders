import os
import json
import pymysql
from controllers.base import BaseController
from database.models import Project, DataModel, DataColumn
from utils.db_generator import MermaidToSQLAgent

class DataModelController(BaseController):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.db_config = {
            "host": os.getenv("DB_HOST"),
            "user": os.getenv("DB_USER"),
            "password": os.getenv("DB_PASSWORD"),
            "database": os.getenv("DB_NAME"),
        }

    def generate_db(self, project_id):
        """Generates a database schema from a project's ERD schema."""
        try:
            project = self.session.query(Project).filter(Project.id == project_id).first()

            if not project:
                print(f"Project with ID {project_id} not found.")
                return None

            project_content = project.get_content()
            erd_schema = project_content.get("erd_schema")

            if not erd_schema:
                print(f"ERD schema missing for project {project_id}.")
                return None

            agent = MermaidToSQLAgent()

            db_config = {
                "host": os.getenv("DB_HOST"),
                "user": os.getenv("DB_USER"),
                "password": os.getenv("DB_PASSWORD"),
                "database": os.getenv("DB_NAME"),
            }

            # Initialize and execute SQLAgent
            statements = agent.process_mermaid(erd_schema)
            agent.write_schema_file(statements)
            agent.execute_sql_file()


            self.store_data(db_config, project_id)

            return db_config
        except Exception as e:
            print(f"Error generating DB for project {project_id}: {e}")

    def _connect_db(self):
        """Creates a connection to MySQL database."""
        return pymysql.connect(**self.db_config, cursorclass=pymysql.cursors.DictCursor)

    def connect_db_with_config(self, config):
        """Creates a connection to MySQL database."""
        return pymysql.connect(**config, cursorclass=pymysql.cursors.DictCursor)

    def get(self, data_model_id):
        """Returns metadata of a single table by table name (data_model_id)."""
        pass

    def get_models(self, project_id):

        """Retrieves metadata for all tables in a given project."""
        models = self.session.query(DataModel).filter(DataModel.project_id == project_id).all()
        tables_metadata = {}

        for model in models:
            tables_metadata[model.table_name] = {"columns": []}
            columns = self.session.query(DataColumn).filter(DataColumn.table_id == model.id).all()

            for column in columns:
                tables_metadata[model.table_name]["columns"].append(
                    {
                        "column_name": column.column_name,
                        "column_type": column.column_type,
                        "is_nullable": "YES" if column.is_nullable else "NO",
                        "is_unique": "YES" if column.is_unique else "NO",
                        "relation": column.relationships,
                    }
                )

        return {"tables": tables_metadata}

    def store_data(self, config, project_id):
        """Stores metadata of tables and columns in the database for a project."""
        try:
            # Delete existing records
            self.session.query(DataColumn).filter(
                DataColumn.table_id.in_(
                    self.session.query(DataModel.id).filter(DataModel.project_id == project_id)
                )
            ).delete(synchronize_session=False)

            self.session.query(DataModel).filter(DataModel.project_id == project_id).delete(synchronize_session=False)
            self.session.commit()

        except Exception as e:
            self.session.rollback()
            print(f"Error deleting previous records for project {project_id}: {e}")
            return None

        column_query = """
        SELECT TABLE_NAME, COLUMN_NAME, COLUMN_TYPE, IS_NULLABLE, COLUMN_KEY
        FROM information_schema.columns
        WHERE TABLE_SCHEMA = %s
        """

        primary_key_query = """
        SELECT TABLE_NAME, COLUMN_NAME
        FROM information_schema.columns
        WHERE TABLE_SCHEMA = %s AND COLUMN_KEY = 'PRI'
        """

        foreign_key_query = """
        SELECT TABLE_NAME, COLUMN_NAME, REFERENCED_TABLE_NAME, REFERENCED_COLUMN_NAME
        FROM information_schema.KEY_COLUMN_USAGE
        WHERE TABLE_SCHEMA = %s AND REFERENCED_TABLE_NAME IS NOT NULL
        """

        unique_key_query = """
        SELECT TABLE_NAME, COLUMN_NAME
        FROM information_schema.columns
        WHERE TABLE_SCHEMA = %s AND COLUMN_KEY = 'UNI'
        """
        try:
            with self.connect_db_with_config(config) as connection:
                with connection.cursor() as cursor:
                    cursor.execute(column_query, (config["database"],))
                    columns = cursor.fetchall()

                    cursor.execute(primary_key_query, (config["database"],))
                    primary_keys = {f"{row['TABLE_NAME']}.{row['COLUMN_NAME']}" for row in cursor.fetchall()}

                    cursor.execute(foreign_key_query, (config["database"],))
                    foreign_keys = cursor.fetchall()

                    cursor.execute(unique_key_query, (config["database"],))
                    unique_keys = {f"{row['TABLE_NAME']}.{row['COLUMN_NAME']}" for row in cursor.fetchall()}

        except Exception as e:
            print(f"Error fetching schema metadata from MySQL: {e}")
            return None

        # Organizing table metadata
        tables_metadata = {}

        for col in columns:
            table_name = col["TABLE_NAME"]
            column_name = col["COLUMN_NAME"]

            if table_name not in tables_metadata:
                tables_metadata[table_name] = {"columns": []}

            relation = None
            key = f"{table_name}.{column_name}"
            is_unique = key in unique_keys
            
            if key in primary_keys:
                relation = "PRIMARY"

            for fk in foreign_keys:
                if fk["TABLE_NAME"] == table_name and fk["COLUMN_NAME"] == column_name:
                    relation = f"FOREIGN KEY {fk['TABLE_NAME']}({column_name}) -> {fk['REFERENCED_TABLE_NAME']}({fk['REFERENCED_COLUMN_NAME']})"

            tables_metadata[table_name]["columns"].append(
                {
                    "column_name": column_name,
                    "column_type": col["COLUMN_TYPE"],
                    "is_nullable": col["IS_NULLABLE"],
                    "is_unique": is_unique,
                    "relation": relation,
                }
            )
        
        print(tables_metadata)    
        # Insert tables and columns into database
        try:
            for table_name, metadata in tables_metadata.items():
                new_table = DataModel(project_id=project_id, table_name=table_name)
                self.session.add(new_table)
                self.session.commit()

                for column in metadata["columns"]:
                    new_column = DataColumn(
                        table_id=new_table.id,
                        column_name=column["column_name"],
                        column_type=column["column_type"],
                        is_nullable=(column["is_nullable"] == "YES"),
                        is_unique=column["is_unique"],
                        relationships=column["relation"]
                    )
                    self.session.add(new_column)

            self.session.commit()

        except Exception as e:
            self.session.rollback()
            print(f"Error storing metadata for project {project_id}: {e}")
            return None

        return {"tables": tables_metadata}

    def get_many(self):
        """Returns metadata for all tables, including primary keys and relationships directly in columns."""

        # Query to get all table columns
        column_query = """
        SELECT TABLE_NAME, COLUMN_NAME, COLUMN_TYPE, IS_NULLABLE, COLUMN_KEY
        FROM information_schema.columns 
        WHERE TABLE_SCHEMA = %s
        """

        # Query to get primary keys
        primary_key_query = """
        SELECT TABLE_NAME, COLUMN_NAME
        FROM information_schema.columns
        WHERE TABLE_SCHEMA = %s AND COLUMN_KEY = 'PRI'
        """

        # Query to get foreign keys
        foreign_key_query = """
        SELECT TABLE_NAME, COLUMN_NAME, REFERENCED_TABLE_NAME, REFERENCED_COLUMN_NAME
        FROM information_schema.KEY_COLUMN_USAGE
        WHERE TABLE_SCHEMA = %s AND REFERENCED_TABLE_NAME IS NOT NULL
        """
        
        unique_key_query = """
        SELECT TABLE_NAME, COLUMN_NAME
        FROM information_schema.columns
        WHERE TABLE_SCHEMA = %s AND COLUMN_KEY = 'UNI'
        """

        connection = self._connect_db()
        with connection.cursor() as cursor:
            # Fetch all table column metadata
            cursor.execute(column_query, (self.db_config["database"],))
            columns = cursor.fetchall()

            # Fetch primary keys
            cursor.execute(primary_key_query, (self.db_config["database"],))
            primary_keys = {
                f"{row['TABLE_NAME']}.{row['COLUMN_NAME']}" for row in cursor.fetchall()
            }  # Set for quick lookup

            # Fetch foreign keys
            cursor.execute(foreign_key_query, (self.db_config["database"],))
            foreign_keys = cursor.fetchall()

            cursor.execute(unique_key_query, (self.db_config["database"],))
            unique_keys = {f"{row['TABLE_NAME']}.{row['COLUMN_NAME']}" for row in cursor.fetchall()}
        connection.close()

        # Organizing data by table
        tables_metadata = {}


        for col in columns:
            table_name = col["TABLE_NAME"]
            column_name = col["COLUMN_NAME"]

            # Initialize table entry if not present
            if table_name not in tables_metadata:
                tables_metadata[table_name] = {"columns": []}

            # Determine relation type
            relation = None
            key = f"{table_name}.{column_name}"
            is_unique = key in unique_keys
            if key in primary_keys:
                relation = "PRIMARY"

            for fk in foreign_keys:
                if fk["TABLE_NAME"] == table_name and fk["COLUMN_NAME"] == column_name:
                    relation = f"FOREIGN KEY {fk['TABLE_NAME']}({column_name}) -> {fk['REFERENCED_TABLE_NAME']}({fk['REFERENCED_COLUMN_NAME']})"

            # Add column metadata
            tables_metadata[table_name]["columns"].append(
                {
                    "column_name": column_name,
                    "column_type": col["COLUMN_TYPE"],
                    "is_nullable": col["IS_NULLABLE"],
                    "is_unique": is_unique,
                    "relation": relation,  # Add relation inside column
                }
            )

        return {"tables": tables_metadata}

    def delete(self, data_model_id):
        """Deletes a single data model"""
        pass

    def delete_many(self, data_model_ids):
        """Deletes list of data models"""
        pass