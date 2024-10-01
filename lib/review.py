from __init__ import CURSOR, CONN


class Review:

    # Dictionary of objects saved to the database.
    all = {}

    def __init__(self, year, summary, employee_id, id=None):
        self.id = id
        self.year = year
        self.summary = summary
        self.employee_id = employee_id

    def __repr__(self):
        return (
            f"<Review {self.id}: {self.year}, {self.summary}, "
            + f"Employee: {self.employee_id}>"
        )

    @classmethod
    def create_table(cls):
        """ Create a new table to persist the attributes of Review instances """
        sql = """
            CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY,
            year INT,
            summary TEXT,
            employee_id INTEGER,
            FOREIGN KEY (employee_id) REFERENCES employee(id))
        """
        CURSOR.execute(sql)
        CONN.commit()

    @classmethod
    def drop_table(cls):
        """ Drop the table that persists Review  instances """
        sql = """
            DROP TABLE IF EXISTS reviews;
        """
        CURSOR.execute(sql)
        CONN.commit()

    def save(self):
        """ Save the current Review instance to the database and set its ID. """
        if self.id:
            # Update existing review record
            CURSOR.execute('''
                UPDATE reviews
                SET year = ?, summary = ?, employee_id = ?
                WHERE id = ?
            ''', (self.year, self.summary, self.employee_id, self.id))
        else:
            # Insert a new review record into the database
            CURSOR.execute('''
                INSERT INTO reviews (year, summary, employee_id)
                VALUES (?, ?, ?)
            ''', (self.year, self.summary, self.employee_id))
            self.id = CURSOR.lastrowid  # Retrieve the ID of the new row
            Review.all[self.id] = self  # Add the review instance to the `all` dictionary
        CONN.commit()

    @classmethod
    def create(cls, year, summary, employee_id):
        """ Create a new Review instance and save it to the database """
        review = cls(year, summary, employee_id)  # Create a new Review instance
        review.save()  # Persist it to the database
        return review

    @classmethod
    def instance_from_db(cls, row):
        """ Create or retrieve a Review instance from a database row """
        review_id = row[0]
        year = row[1]
        summary = row[2]
        employee_id = row[3]

        # Check if the review is already cached in the `all` dictionary
        if review_id in cls.all:
            # Return the cached object if it exists
            return cls.all[review_id]
        else:
            # Create a new Review instance from the row data
            review = cls(year, summary, employee_id, review_id)
            cls.all[review_id] = review  # Cache the new object in the dictionary
            return review

    @classmethod
    def find_by_id(cls, id):
        """ Find a Review instance by its ID """
        CURSOR.execute('SELECT * FROM reviews WHERE id = ?', (id,))
        row = CURSOR.fetchone()  # Fetch one row from the database
        if row:
            return cls.instance_from_db(row)  # Return the corresponding Review instance
        return None

    def update(self):
        """ Update the current Review instance's data in the database """
        CURSOR.execute('''
            UPDATE reviews
            SET year = ?, summary = ?, employee_id = ?
            WHERE id = ?
        ''', (self.year, self.summary, self.employee_id, self.id))
        CONN.commit()

    def delete(self):
        """ Delete the Review instance from the database and remove it from the cache """
        CURSOR.execute('DELETE FROM reviews WHERE id = ?', (self.id,))
        CONN.commit()

        # Remove the instance from the `all` dictionary
        if self.id in Review.all:
            del Review.all[self.id]

        # Set the ID to None as the object no longer exists in the database
        self.id = None

    @classmethod
    def get_all(cls):
        """ Return a list of all Review instances from the database """
        CURSOR.execute('SELECT * FROM reviews')
        rows = CURSOR.fetchall()  # Fetch all rows from the database
        return [cls.instance_from_db(row) for row in rows]

    @property
    def year(self):
        return self._year

    @year.setter
    def year(self, value):
        if not isinstance(value, int):
            raise ValueError("Year must be an integer")
        if value < 2000:
            raise ValueError("Year must be greater than or equal to 2000")
        self._year = value

    # Property for summary with validation
    @property
    def summary(self):
        return self._summary

    @summary.setter
    def summary(self, value):
        if not isinstance(value, str) or not value.strip():
            raise ValueError("Summary must be a non-empty string")
        self._summary = value

    # Property for employee_id with validation
    @property
    def employee_id(self):
        return self._employee_id

    @employee_id.setter
    def employee_id(self, value):
        # Ensure employee exists in the employees table
        CURSOR.execute('SELECT * FROM employees WHERE id = ?', (value,))
        row = CURSOR.fetchone()
        if row is None:
            raise ValueError("Employee ID must refer to an existing employee")
        self._employee_id = value
