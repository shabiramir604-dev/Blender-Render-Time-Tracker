import bpy
import os

# Icon names mapping for the addon
ICONS = {
    'TIME': 'TIME',
    'RENDER': 'RENDER_STILL',
    'RENDER_ANIM': 'RENDER_ANIMATION',
    'STATS': 'GRAPH',
    'RESET': 'FILE_REFRESH',
    'EXPORT': 'EXPORT',
    'SETTINGS': 'PREFERENCES',
    'INFO': 'INFO',
    'WARNING': 'ERROR',
    'TRASH': 'TRASH',
    'PLAY': 'PLAY',
    'PAUSE': 'PAUSE',
    'STOP': 'STOP',
}

class IconManager:
    """Manager for custom icons"""
    def __init__(self):
        self.preview_collection = None
        self.loaded = False

    def load_icons(self):
        """Load custom icons from icons folder"""
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
                        print(f"[Render Time Tracker] Loaded icon: {name}")
                    except Exception as e:
                        print(f"[Render Time Tracker] Failed to load icon {name}: {e}")

        self.loaded = True

    def get_icon(self, name):
        """Get icon by name"""
        if self.preview_collection and name in self.preview_collection:
            return self.preview_collection[name].icon_id
        return None

    def unregister(self):
        """Cleanup icons"""
        if self.preview_collection:
            bpy.utils.previews.remove(self.preview_collection)
            self.preview_collection = None
        self.loaded = False

# Global icon manager instance
icon_manager = IconManager()

def register():
    """Register icons"""
    icon_manager.load_icons()

def unregister():
    """Unregister icons"""
    icon_manager.unregister()
