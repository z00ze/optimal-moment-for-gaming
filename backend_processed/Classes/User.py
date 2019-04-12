class User:
    def __init__(self, id, token):
        self.id = id
        self.token = token

    def set_data_entries(self, data_entries):
        self.data_entries = data_entries