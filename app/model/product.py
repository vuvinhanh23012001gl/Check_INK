class Product:

    def __init__(
        self,
        id: int,
        name: str,
        description: str = ""
    ):

        self._id = id
        self._name = name
        self._description = description

        # metadata
        self.created_at = ""
        self.updated_at = ""

    # =========================
    # ID
    # =========================

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, value):
        self._id = value

    # =========================
    # NAME
    # =========================

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    # =========================
    # DESCRIPTION
    # =========================

    @property
    def description(self):
        return self._description

    @description.setter
    def description(self, value):
        self._description = value

    # =========================
    # TO DICT
    # =========================

    def to_dict(self):

        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    # =========================
    # REPR
    # =========================

    def __repr__(self):

        return (
            f"Product("
            f"id={self.id}, "
            f"name='{self.name}'"
            f")"
        )