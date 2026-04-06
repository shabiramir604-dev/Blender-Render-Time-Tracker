import bpy
import os

class IconManager:
    def __init__(self):
        self.preview_collection = None
        self.loaded = False

    def load_icons(self):
        import bpy.utils.previews
        if self.loaded:
            return
        self.preview_collection = bpy.utils.previews.new()
        icons_dir = os.path.join(os.path.dirname(__file__), "icons")
        if os.path.exists(icons_dir):
            for icon_file in os.listdir(icons_dir):
                if icon_file.endswith(('.png', '.jpg', '.jpeg')):
                    name = os.path.splitext(icon_file)[0].upper()
                    filepath = os.path.join(icons_dir, icon_file)
                    try:
                        self.preview_collection.load(name, filepath, 'IMAGE')
                    except Exception as e:
                        print(f"[Render Time Tracker] Failed to load icon {name}: {e}")
        self.loaded = True

    def unregister(self):
        if self.preview_collection:
            bpy.utils.previews.remove(self.preview_collection)
            self.preview_collection = None
        self.loaded = False

icon_manager = IconManager()

def register():
    icon_manager.load_icons()

def unregister():
    icon_manager.unregister()
