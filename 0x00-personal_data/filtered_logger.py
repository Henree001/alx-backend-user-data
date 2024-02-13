#!/usr/bin/env python3
"""filter_datum function definition"""
import re
from typing import List, Union
import logging
import os
import mysql.connector


PII_FIELDS = ("name", "email", "phone", "ssn", "password")


def filter_datum(
    fields: List[str], redaction: str, message: str, seperator: str
) -> str:
    spilted = message.split(seperator)
    for i in fields:
        for j in range(len(spilted)):
            if i in spilted[j]:
                spilted[j] = re.sub(r"=(.*)", f"={redaction}", spilted[j])
    return seperator.join(spilted)


def get_logger() -> logging.Logger:
    """Get logger function"""
    logger = logging.getLogger("user_data")
    logger.setLevel(logging.INFO)
    logger.propagate = False
    stream = logging.StreamHandler()
    stream.setFormatter(RedactingFormatter(list(PII_FIELDS)))
    logger.addHandler(stream)
    return logger


def get_db() -> Union[mysql.connector.connection.MySQLConnection, None]:
    """Get database function"""
    # Get database credentials from environment variables
    db_username = os.getenv("PERSONAL_DATA_DB_USERNAME", "root")
    db_password = os.getenv("PERSONAL_DATA_DB_PASSWORD", "")
    db_host = os.getenv("PERSONAL_DATA_DB_HOST", "localhost")
    db_name = os.getenv("PERSONAL_DATA_DB_NAME")

    # Connect to the MySQL database
    try:
        connection = mysql.connector.connect(
            user=db_username, password=db_password, host=db_host,
            database=db_name
        )
        return connection
    except mysql.connector.Error as err:
        print("Error connecting to the database:", err)
        return None


class RedactingFormatter(logging.Formatter):
    """Redacting Formatter class"""

    REDACTION = "***"
    FORMAT = "[HOLBERTON] %(name)s %(levelname)s %(asctime)-15s: %(message)s"
    SEPARATOR = ";"

    def __init__(self, fields: List[str]) -> None:
        super(RedactingFormatter, self).__init__(self.FORMAT)
        self.fields = fields

    def format(self, record: logging.LogRecord) -> str:
        return filter_datum(
            self.fields, self.REDACTION, super().format(record), self.SEPARATOR
        )


def main():
    """Main function"""
    db = get_db()
    if db:
        cursor = db.cursor()
        cursor.execute("SELECT * FROM users")
        logger = get_logger()
        for row in cursor:
            message = f"name={row[0]}; email={row[1]}; phone={row[2]};\
            ssn={row[3]}; password={row[4]}; ip={row[5]}; last_login={row[6]};\
            user_agent={row[7]};"
            logger.info(message)
        cursor.close()
        db.close()


if __name__ == "__main__":
    main()
