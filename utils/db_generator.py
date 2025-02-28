import os
import re
import json
import pymysql
from dotenv import load_dotenv
from langchain.agents import Tool
from langgraph.graph import Graph
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from typing import List, Dict, Any, Optional
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import AIMessage, HumanMessage

load_dotenv()

class SQLStatement(BaseModel):
    statement: str = Field(description="The complete SQL statement")
    table_name: Optional[str] = Field(None, description="Name of the table being created or altered")
    statement_type: Optional[str] = Field(None, description="Type of SQL statement (CREATE or ALTER)")

class SQLResponse(BaseModel):
    create_statements: List[SQLStatement] = Field(default_factory=list)
    alter_statements: List[SQLStatement] = Field(default_factory=list)
    validation_status: str = Field(description="Status of the Mermaid diagram validation")
    errors: Optional[List[str]] = Field(default=None)

class State(BaseModel):
    """Class to manage state between nodes"""
    diagram: str
    validation_result: Optional[str] = None
    corrected_diagram: Optional[str] = None
    create_statements: Optional[str] = None
    alter_statements: Optional[str] = None

class MermaidToSQLAgent:
    def __init__(self):
        self.llm = ChatOpenAI(temperature=0, model="gpt-4")
        self.graph = self._create_graph()
        
    def _create_validation_node(self):
        validation_prompt = ChatPromptTemplate.from_messages([
            ("system", "You are an expert in Mermaid ER diagrams. Check the given diagram for errors and return 'VALID' if correct, or list specific issues found."),
            ("human", "{diagram}")
        ])
        
        def validate_mermaid(state: Dict) -> Dict:
            diagram = state["input"]["diagram"]
            response = self.llm.invoke(validation_prompt.format(diagram=diagram))

            output = {
                "validate": {  # Ensures the validate node's output is accessible
                    "output": {
                        "diagram": diagram,
                        "validation_result": response.content
                    }
                }
            }
            
            # print("DEBUG - VALIDATE OUTPUT:", output)  # Debugging statement
            return output

        return validate_mermaid

    def _create_correction_node(self):
        correction_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert in Mermaid ER diagrams. Fix the following issues in the provided diagram.
            IMPORTANT: Return the COMPLETE corrected diagram with ALL tables and relationships, not just the corrected parts.
            The diagram uses the 'erDiagram' syntax, not 'graph TD' syntax. Maintain the original formatting and theme."""),
            ("human", "Original diagram:\n{diagram}\n\nIssues to fix:\n{issues}")
        ])
        
        def correct_mermaid(state: Dict) -> Dict:
            if "validate" not in state or "output" not in state["validate"]:
                raise ValueError("Missing validation output in state")

            validation_result = state["validate"]["output"]["validation_result"]
            original_diagram = state["validate"]["output"]["diagram"]

            if "VALID" in validation_result.upper():
                corrected_diagram = original_diagram
            else:
                response = self.llm.invoke(
                    correction_prompt.format(
                        diagram=original_diagram,
                        issues=validation_result
                    )
                )
                corrected_diagram = response.content

            output = {
                "correct": {  
                    "output": {
                        "diagram": original_diagram,
                        "corrected_diagram": corrected_diagram,
                        "validation_result": validation_result
                    }
                }
            }
            
            # print("DEBUG - CORRECT OUTPUT:", output)  # Debugging
            return output
            
        return correct_mermaid

    def clean_sql_response(self,response: str) -> str:
            """Removes markdown formatting and extra system text from SQL response."""
            response = re.sub(r"```sql|```", "", response)  # Remove Markdown SQL blocks
            response = response.replace("System: ", "").strip()  # Remove any extra prefixes
            return response
    
    def generate_single_table_sql(self, table_definition: str) -> str:
        """
        Generates a CREATE TABLE statement for a single table using the LLM.
        
        :param table_definition: Mermaid ER diagram portion defining a single table.
        :return: Generated SQL CREATE TABLE statement.
        """
        table_prompt = ChatPromptTemplate.from_messages([
            ("system", """
            You are an expert SQL developer. Generate a CREATE TABLE statement for the given ER diagram.

            STRICT RULES:
            1. Parse ALL attributes exactly as specified.
            2. Use these SQL data types:
            - uuid → CHAR(36) 
            - varchar → VARCHAR(X) (Choose X intelligently based on column meaning)
            - enum → ENUM (Infer values based on column name)
            - timestamp → TIMESTAMP 
            - date → DATE 
            - int → INT 
            3. Constraints:
            - "PK" → PRIMARY KEY
            - "not null" → NOT NULL
            - "unique" → UNIQUE
            - "indexed" → Create an INDEX
            - "soft delete" → Nullable TIMESTAMP (for soft deletes)
            4. **VARCHAR Size Rules:**
            - **Short fields** (e.g., `name`, `status`, `role`) → `VARCHAR(50-100)`
            - **Longer fields** (e.g., `email`, `description`) → `VARCHAR(150-300)`
            - **Do NOT default everything to VARCHAR(255)**.
            5. **ENUM Handling:**
            - DO NOT use generic ENUM values like 'value1', 'value2'.
            6. NO missing columns. ALL attributes must be included.
            7. Do **NOT** generate FOREIGN KEY constraints.
            8. **Format Strictly:**  
            - Each column must be on a new line.  
            - End each statement with `;`.  

            Only return a valid `CREATE TABLE` SQL statement. NO explanations, NO placeholders.
            """),
            ("human", "{diagram}")
        ])

        # Invoke LLM for this single table
        create_response = self.llm.invoke(table_prompt.format(diagram=table_definition))
        
        return create_response.content.strip()
    
    def generate_alter_statements(self, diagram: str) -> str:
        """
        Generates ALTER TABLE statements for relationships from the Mermaid ER diagram.
        :return: Generated SQL ALTER TABLE statements.
        """
        relationship_prompt = ChatPromptTemplate.from_messages([
            ("system", """
            You are an expert SQL developer. Generate ALTER TABLE statements for ALL relationships in the provided ER diagram.

            STRICT RULES:
            1. Create an ALTER TABLE statement for EVERY relationship in the diagram.
            2. For each foreign key:
            - Reference the exact column names from the CREATE TABLE statements.
            - Include ON DELETE CASCADE and ON UPDATE CASCADE.
            - Use the relationship type to determine the exact constraints.
            3. Handle junction tables for many-to-many relationships correctly.
            4. For many-to-many relationships:
            - Create correct ALTER TABLE statements for both sides of the relationship.
            5. **Format Strictly:**
            - Each constraint must be in its own ALTER TABLE statement.
            - End each statement with `;`.
            
            ONLY return valid ALTER TABLE SQL statements. NO explanations, NO placeholders.
            """),
            ("human", "{diagram}")
        ])

        alter_response = self.llm.invoke(relationship_prompt.format(diagram=diagram))
        
        return alter_response.content.strip()

    def extract_tables_from_mermaid(self,diagram: str):
        """
        Extract individual table definitions from a Mermaid ER diagram.
        :return: List of table definitions as separate strings
        """
        tables = {}
        current_table = None
        lines = diagram.split("\n")
        # print(diagram) # Debugging
        for line in lines:
            line = line.strip()

            # Detect table name
            match = re.match(r"^(\w+)\s*\{", line)
            if match:
                current_table = match.group(1)
                tables[current_table] = []

            # Detect column definitions within a table
            elif current_table and "}" not in line and line:
                tables[current_table].append(line)

            # End of a table definition
            elif "}" in line:
                current_table = None

        # Convert to individual table definitions
        table_definitions = [
            f"{table} {{\n    " + "\n    ".join(columns) + "\n}" for table, columns in tables.items()
        ]

        return table_definitions

    def _create_sql_generation_node(self):
        def generate_sql(state: Dict) -> Dict:
            if "correct" not in state or "output" not in state["correct"]:
                raise ValueError("Missing corrected Mermaid diagram in state")

            diagram = state["correct"]["output"]["corrected_diagram"]
            validation_result = state["correct"]["output"]["validation_result"]

            # Extract individual table definitions
            tables = self.extract_tables_from_mermaid(diagram)

            create_statements = []
            
            for table in tables:
                # print(f"Generating SQL for table: {table}")  # Debugging
                sql_statement = self.generate_single_table_sql(table)
                print("Generated SQL:", sql_statement)  # Debugging
                create_statements.append(sql_statement)

            # Generate ALTER TABLE statements
            alter_statements = self.generate_alter_statements(diagram)
            print("Generated ALTER Statements:", alter_statements)  # Debugging

            output = {
                "generate": {
                    "output": {
                        "create_statements": "\n\n".join(create_statements),
                        "alter_statements": alter_statements,
                        "validation_result": validation_result
                    }
                }
            }

            return output

        return generate_sql

    def _create_sql_parser_node(self):
        def parse_sql(state: Dict) -> Dict:
            # print("STATE BEFORE PARSE:", state)  # Debugging
            
            if "generate" not in state or "output" not in state["generate"]:
                raise ValueError("Missing 'generate' output in state")

            create_statements = self._parse_sql_statements(state["generate"]["output"]["create_statements"], "CREATE")
            alter_statements = self._parse_sql_statements(state["generate"]["output"]["alter_statements"], "ALTER")
            validation_result = state["generate"]["output"]["validation_result"]

            response = SQLResponse(
                create_statements=create_statements,
                alter_statements=alter_statements,
                validation_status="valid" if "VALID" in validation_result.upper() else "corrected",
                errors=None if "VALID" in validation_result.upper() else [validation_result]
            )

            output = {"parse": {"output": response}}
            # print("PARSE OUTPUT:", output)  # Debugging
            return output
            
        return parse_sql

    def _parse_sql_statements(self, sql_text: str, stmt_type: str) -> List[SQLStatement]:
        statements = []
        sql_text = self.clean_sql_response(sql_text)  # Ensure it’s cleaned

        for stmt in sql_text.split(";"):
            stmt = stmt.strip()
            if stmt:
                statements.append(SQLStatement(statement=f"{stmt};", statement_type=stmt_type))  # Ensure semicolon is retained

        return statements

    
    def _create_graph(self) -> Graph:
        graph = Graph()

        # Add nodes
        graph.add_node("validate", self._create_validation_node())
        graph.add_node("correct", self._create_correction_node())
        graph.add_node("generate", self._create_sql_generation_node())
        graph.add_node("parse", self._create_sql_parser_node())

        # Define edges
        graph.add_edge("validate", "correct")
        graph.add_edge("correct", "generate")
        graph.add_edge("generate", "parse")

        # Explicitly set "parse" as an output node
        graph.set_entry_point("validate")
        graph.set_finish_point("parse")  

        return graph.compile()


    def process_mermaid(self, mermaid_code: str) -> SQLResponse:
        state = {"input": {"diagram": mermaid_code}}

        try:
            result = self.graph.invoke(state)
        except Exception as e:
            print("ERROR DURING GRAPH EXECUTION:", str(e))
            raise ValueError("Graph execution failed with an exception")

        # print("result AFTER GRAPH EXECUTION:", result)  # Debugging

        if not result:
            raise ValueError("Graph execution failed: No result returned")

        if "parse" not in result:
            raise ValueError("Graph execution failed: 'parse' node missing in result")

        final_state = result["parse"]
        if "output" not in final_state:
            raise ValueError("Final state missing expected output")

        return final_state["output"]

    def write_schema_file(self, sql_response: SQLResponse, filename: str = 'schema.sql'):
        """Write SQL statements to schema file"""
        with open(filename, 'w') as f:
            # Write header
            header = """
            DROP DATABASE IF EXISTS flight_booking;
            CREATE DATABASE flight_booking;
            USE flight_booking;
            """.strip()
            f.write(header + "\n\n")
            
            # Write CREATE statements
            f.write("-- Create Tables\n\n")
            for stmt in sql_response.create_statements:
                f.write(f"{stmt.statement}\n\n")
            
            # Write ALTER statements
            f.write("-- Add Foreign Key Constraints\n\n")
            for stmt in sql_response.alter_statements:
                f.write(f"{stmt.statement}\n\n")
    
    def execute_sql_file(self, sql_file="schema.sql"):
        """Connects to MySQL and executes the given SQL schema file."""
        try:
            # Connect to MySQL
            connection = pymysql.connect(
                host=os.getenv("DB_HOST"),
                user=os.getenv("DB_USER"),
                password=os.getenv("DB_PASSWORD"),
                autocommit=True  
            )

            with connection.cursor() as cursor:
                with open(sql_file, "r") as f:
                    sql_script = f.read()

                    sql_statements = re.split(r';\s*\n', sql_script)

                    for statement in sql_statements:
                        statement = statement.strip()
                        if statement:
                            try:
                                cursor.execute(statement)
                            except Exception as e:
                                print(f"Error executing SQL statement:\n{statement}\nError: {e}")
                                self.handle_error(statement, e)

            print("Database schema executed successfully.")

        except Exception as e:
            print(f"Error executing SQL: {e}")
        finally:
            connection.close()

    def handle_error(self, sql_statement: str, error: Exception) -> bool:
        """
        Handle SQL execution error by allowing human or AI correction.
        Returns True if the corrected statement executed successfully, False otherwise.
        """
        print(f"Error executing SQL statement: {sql_statement}")
        print(f"Error details: {str(error)}")
        
        max_attempts = 6
        attempts = 0

        while attempts < max_attempts:
            # correction = input("Would you like to (1) Fix it manually, (2) Let AI suggest corrections, or (3) Abort? Enter 1, 2, or 3: ")
            correction = "2"
            if correction == "1":
                corrected_sql = input("Please provide the corrected SQL statement: ")
                if not corrected_sql.strip():
                    print("Empty statement provided. Aborting.")
                    return False
                return self.reexecute_sql_statement(corrected_sql)

            elif correction == "2":
                corrected_sql = self.ask_ai_for_sql_fix(sql_statement)
                if not corrected_sql:
                    print("AI could not provide a fix. Please try manual correction.")
                    attempts += 1
                    continue  # Retry up to max_attempts

                print(f"AI suggested fix: {corrected_sql}")
                # proceed = input("Would you like to execute this fix? (y/n): ")
                proceed = "y"
                if proceed.lower() == 'y':
                    return self.reexecute_sql_statement(corrected_sql)
                attempts += 1  # Increment attempts after an AI attempt
                continue  # Retry loop if not executed

            elif correction == "3":
                print("Aborting operation.")
                return False  # Exit loop and function

            else:
                print("Invalid option. Please enter 1, 2, or 3.")

            attempts += 1

        print("Maximum retry attempts reached. Aborting.")
        return False  # Exit after max attempts


    def ask_ai_for_sql_fix(self, sql_statement: str) -> Optional[str]:
        """Ask the AI model to generate a corrected SQL statement."""
        try:
            llm = ChatOpenAI(temperature=0, model="gpt-4")
            
            prompt = ChatPromptTemplate.from_messages([
                ("system", "You are a database expert assisting with fixing SQL execution errors. "
                          "Return ONLY the corrected SQL statement, with no additional explanation."),
                ("human", f"The following SQL statement caused an error during execution:\n{sql_statement}\n\n"
                         f"Please provide ONLY the corrected SQL statement:")
            ])
            
            formatted_prompt = prompt.format()
            response = llm.invoke(formatted_prompt)
            corrected_sql = response.content.strip()
            
            # Basic validation that we got a SQL statement
            if not any(keyword in corrected_sql.upper() for keyword in ['CREATE', 'ALTER', 'DROP', 'INSERT', 'UPDATE', 'DELETE']):
                print("AI response doesn't appear to be a valid SQL statement")
                return None
                
            return corrected_sql
            
        except Exception as e:
            print(f"Error getting AI suggestion: {str(e)}")
            return None

    def reexecute_sql_statement(self, corrected_sql: str):
        """Reattempt executing the corrected SQL statement."""
        try:
            connection = pymysql.connect(
                host=os.getenv("DB_HOST"),
                user=os.getenv("DB_USER"),
                password=os.getenv("DB_PASSWORD"),
                database=os.getenv("DB_NAME"),  # Ensure database is specified
                autocommit=True
            )

            with connection.cursor() as cursor:       
                try:
                    cursor.execute(corrected_sql)  
                    print(f"Successfully executed the corrected statement: {corrected_sql}")
                except Exception as e:
                    print(f"Error executing corrected statement: {corrected_sql}")
                    print(f"Error details: {str(e)}")
        except pymysql.MySQLError as db_err:
            print(f"Database connection error: {str(db_err)}")
        finally:
            if 'connection' in locals():
                connection.close()
