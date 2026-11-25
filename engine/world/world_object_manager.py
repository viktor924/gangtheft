
from engine.world.game_object import GameObject

class WorldObjectManager:

    def __init__(self):

        self.objects = {}

        self.initialized = True

        print("[WorldObjectManager] Initialized.")

    # ======================================
    # CREATE OBJECT
    # ======================================

    def create_object(
        self,
        name="GameObject",
        mesh=None,
        position=None,
        rotation=None,
        scale=None,
        color=(1.0, 1.0, 1.0, 1.0)
    ):

        if not self.initialized:
            raise RuntimeError(
                "WorldObjectManager is not initialized."
            )

        game_object = GameObject(
            name=name,
            mesh=mesh,
            position=position,
            rotation=rotation,
            scale=scale,
            color=color
        )

        self.add_object(game_object)

        return game_object

    # ======================================
    # ADD OBJECT
    # ======================================

    def add_object(self, game_object):

        if not self.initialized:
            raise RuntimeError("WorldObjectManager is not initialized.")

        if game_object.id in self.objects:
            raise ValueError(
                f"Object ID {game_object.id} already exists."
            )

        self.objects[game_object.id] = game_object

        print(
            f"[WorldObjectManager] Added: "
            f"{game_object.name} (ID: {game_object.id})"
        )

        return game_object

    # ======================================
    # REMOVE OBJECT
    # ======================================

    def remove_object(self, object_id, destroy=True):

        game_object = self.objects.pop(object_id, None)

        if game_object is None:
            return False

        if destroy:
            game_object.close()

        print(
            f"[WorldObjectManager] Removed object ID: {object_id}"
        )

        return True

    # ======================================
    # GET OBJECT
    # ======================================

    def get_object(self, object_id):

        return self.objects.get(object_id)

    # ======================================
    # FIND BY NAME
    # ======================================

    def find_by_name(self, name):

        return [
            obj
            for obj in self.objects.values()
            if obj.name == name
        ]

    # ======================================
    # GET ALL OBJECTS
    # ======================================

    def get_all_objects(self):

        return list(self.objects.values())

    # ======================================
    # GET ACTIVE OBJECTS
    # ======================================

    def get_active_objects(self):

        return [
            obj
            for obj in self.objects.values()
            if obj.active
        ]

    # ======================================
    # GET VISIBLE OBJECTS
    # ======================================

    def get_visible_objects(self):

        return [
            obj
            for obj in self.objects.values()
            if obj.active and obj.visible
        ]

    # ======================================
    # UPDATE OBJECTS
    # ======================================

    def update(self, delta_time):

        if not self.initialized:
            return

        for game_object in list(self.objects.values()):

            if game_object.active:
                game_object.update(delta_time)

    # ======================================
    # STATISTICS
    # ======================================

    def get_object_count(self):

        return len(self.objects)

    def get_active_count(self):

        return len(self.get_active_objects())

    def get_visible_count(self):

        return len(self.get_visible_objects())

    # ======================================
    # CLEANUP
    # ======================================

    def clear(self, destroy=True):

        for object_id in list(self.objects.keys()):

            self.remove_object(
                object_id,
                destroy=destroy
            )

    def close(self):

        if not self.initialized:
            return

        self.clear(destroy=True)

        self.initialized = False

        print("[WorldObjectManager] Shutdown complete.")