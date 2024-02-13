#!/usr/bin/env python3
"""filter_datum function definition"""
import re
from typing import List
import logging
import os
import mysql.connector


PII_FIELDS = ("name", "email", "phone", "ssn", "password")


def filter_datum(
    fields: List[str], redaction: str, message: str, separator: str
) -> str:
    """returns the log message obfuscated"""
    formatted_msg = message
    for field in fields:
        formatted_msg = re.sub(
            field + "=.*?" + separator,
            field + "=" + redaction + separator,
            formatted_msg,
        )
    return formatted_msg


def get_logger() -> logging.Logger:
    """Get logger function"""
    logger = logging.getLogger("user_data")
    logger.setLevel(logging.INFO)
    logger.propagate = False
    stream = logging.StreamHandler()
    stream.setFormatter(RedactingFormatter(list(PII_FIELDS)))
    logger.addHandler(stream)
    return logger


def get_db() -> mysql.connector.connection.MySQLConnection:
    """Connect to mysql server with environmental vars"""
    db_username = os.environ.get("PERSONAL_DATA_DB_USERNAME", "root")
    db_password = os.environ.get("PERSONAL_DATA_DB_PASSWORD", "")
    db_host = os.environ.get("PERSONAL_DATA_DB_HOST", "localhost")
    db_name = os.environ.get("PERSONAL_DATA_DB_NAME")
    connection = mysql.connector.connection.MySQLConnection(
        user=db_username, password=db_password, host=db_host, database=db_name
    )
    return connection


class RedactingFormatter(logging.Formatter):
    """Redacting Formatter class"""

    REDACTION = "***"
    FORMAT = "[HOLBERTON] %(name)s %(levelname)s %(asctime)-15s: %(message)s"
    SEPARATOR = ";"

    def __init__(self, fields: List[str]):
        super(RedactingFormatter, self).__init__(self.FORMAT)
        self.fields = fields

    def format(self, record: logging.LogRecord) -> str:
        """Filter values in incoming log records using filter_datum"""
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
