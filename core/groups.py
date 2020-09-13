class Group:

    def __init__(self, group_id, name):
        self.group_id = group_id
        self.name = name

    @staticmethod
    def create(name):
        return Group(None, name)


class Groups:

    def __init__(self, database):
        self.database = database

    def persist(self, group):
        query = """INSERT INTO item_groups (name) VALUES (?)"""
        data = (group.name,)
        generated_id = self.database.execute(query, data)
        group.id = generated_id
