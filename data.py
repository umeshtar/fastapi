import json
import os
import uuid


class DummyDataBase:
    """
    DummyDataBase is a simple file-based data management class that mimics basic CRUD
    operations on model-like entities using the file system and JSON storage.

    Attributes:
        model (str): The name of the model (used as the filename).
        db_dir (str): Directory where the JSON file is stored.
        file_name (str): Full path to the model's JSON file.
    """

    def __init__(self, model):
        """
        Initialize the DummyDataBase with a model name.
        Creates a directory and file for storing the data if they don't exist.

        Args:
            model (str): The model name used as the JSON filename.
        """
        self.model = model
        self.db_dir = "database"
        os.makedirs(self.db_dir, exist_ok=True)
        self.file_name = os.path.join(self.db_dir, f"{model}.json")
        if not os.path.exists(self.file_name):
            with open(self.file_name, 'w') as f:
                json.dump([], f)

    def _read_data(self):
        """
        Internal helper to read all data from the JSON file.

        Returns:
            list: List of all records.
        """
        with open(self.file_name, 'r') as f:
            return json.load(f)

    def _write_data(self, data):
        """
        Internal helper to write data to the JSON file.

        Args:
            data (list): The list of records to save.
        """
        with open(self.file_name, 'w') as f:
            json.dump(data, f, indent=4)

    def retrieve_all(self):
        """
        Retrieve all records from the model's data store.

        Returns:
            list: All records stored in the JSON file.
        """
        return self._read_data()

    def retrieve(self, pk: uuid.UUID):
        """
        Retrieve a single record by its primary key.

        Args:
            pk (str): The UUID of the record.

        Returns:
            dict or None: The matching record or None if not found.
        """
        data = self._read_data()
        for item in data:
            if item.get("id") == str(pk):
                return item
        return None

    def create(self, **kwargs):
        """
        Create a new record with the given keyword arguments.

        Args:
            **kwargs: Arbitrary keyword arguments representing the record fields.

        Returns:
            dict: The newly created record with a UUID.
        """
        data = self._read_data()
        new_id = str(uuid.uuid4())
        kwargs["id"] = new_id
        data.append(kwargs)
        self._write_data(data)
        return kwargs

    def update(self, pk: uuid.UUID, **kwargs):
        """
        Update an existing record with new field values.

        Args:
            pk (str): The UUID of the record to update.
            **kwargs: Updated field values.

        Returns:
            dict or None: The updated record, or None if not found.
        """
        data = self._read_data()
        for index, item in enumerate(data):
            if item.get("id") == str(pk):
                data[index].update(kwargs)
                self._write_data(data)
                return data[index]
        return None

    def delete(self, pk: uuid.UUID) -> object:
        """
        Delete a record by its primary key.

        Args:
            pk (str): The UUID of the record to delete.

        Returns:
            bool: True if a record was deleted, False otherwise.
        """
        data = self._read_data()
        new_data = [item for item in data if item.get("id") != str(pk)]
        self._write_data(new_data)
        return len(data) != len(new_data)


if __name__ == '__main__':
    db = DummyDataBase(model='test')

    # Create example
    record = db.create(name="Umesh", department="IT")
    print("Created:", record)

    # Retrieve all
    print("All:", db.retrieve_all())

    # Retrieve by UUID
    print("Single:", db.retrieve(record["id"]))

    # Update
    print("Updated: ", db.update(record["id"], department="EE"))

    # Delete
    print("Deleted: ", db.delete(record["id"]))
