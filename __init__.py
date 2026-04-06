import bpy
import time
import os
from bpy.props import BoolProperty, FloatProperty, IntProperty, StringProperty, EnumProperty
from bpy.types import Panel, Operator, PropertyGroup, AddonPreferences

# Global tracking variables
render_start_time = None
frame_start_time = None
total_frames_rendered = 0
render_history = []
render_stats = {
    "total_time": 0,
    "current_frame_time": 0,
    "average_time": 0,
    "estimated_remaining": 0,
    "is_rendering": False,
    "frame_count": 0,
    "start_frame": 0,
    "end_frame": 0,
}

def format_time(seconds):
    """Format seconds to HH:MM:SS.ms"""
    if seconds < 0 or seconds is None:
        return "00:00:00.00"
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds % 1) * 100)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}.{millis:02d}"

# Property Groups
class RenderTimeItem(PropertyGroup):
    """Individual render time entry"""
    frame: IntProperty(name="Frame")
    time: FloatProperty(name="Time (s)")
    timestamp: StringProperty(name="Timestamp")

class RenderTimeProperties(PropertyGroup):
    """Main properties for render time tracking"""

    show_in_render_window: BoolProperty(
        name="Show in Render Window",
        description="Display render stats in render window",
        default=True
    )

    show_total_time: BoolProperty(
        name="Show Total Time",
        description="Display total render time",
        default=True
    )

    show_per_frame: BoolProperty(
        name="Show Per Frame Time",
        description="Display time per frame",
        default=True
    )

    show_eta: BoolProperty(
        name="Show ETA",
        description="Display estimated time remaining",
        default=True
    )

    show_progress_bar: BoolProperty(
        name="Show Progress Bar",
        description="Display visual progress bar",
        default=True
    )

    auto_refresh: BoolProperty(
        name="Auto Refresh",
        description="Auto refresh stats during render",
        default=True
    )

    refresh_interval: IntProperty(
        name="Refresh Interval",
        description="Refresh interval in seconds",
        default=1,
        min=1,
        max=60
    )

    notify_complete: BoolProperty(
        name="Notify on Complete",
        description="Show notification when render completes",
        default=True
    )

    notify_sound: BoolProperty(
        name="Play Sound",
        description="Play sound when render completes",
        default=False
    )

    auto_export: BoolProperty(
        name="Auto Export on Complete",
        description="Automatically export stats when render completes",
        default=False
    )

    export_path: StringProperty(
        name="Export Path",
        description="Path to auto-export stats",
        default="//render_stats.txt",
        subtype='FILE_PATH'
    )

    export_format: EnumProperty(
        name="Export Format",
        description="Format for exporting statistics",
        items=[
            ('TXT', "Text", "Plain text format"),
            ('CSV', "CSV", "Comma separated values"),
            ('JSON', "JSON", "JSON format"),
        ],
        default='TXT'
    )

    history: bpy.props.CollectionProperty(type=RenderTimeItem)
    history_index: IntProperty(default=0)

# Render Handlers
def on_render_init(scene):
    """Called when render starts"""
    global render_start_time, total_frames_rendered, render_stats, render_history
    render_start_time = time.time()
    total_frames_rendered = 0
    render_history = []
    render_stats["is_rendering"] = True
    render_stats["total_time"] = 0
    render_stats["current_frame_time"] = 0
    render_stats["average_time"] = 0
    render_stats["estimated_remaining"] = 0
    render_stats["frame_count"] = 0
    render_stats["start_frame"] = scene.frame_start
    render_stats["end_frame"] = scene.frame_end

    print(f"[Render Time Tracker] Render Started - Frames: {scene.frame_start} to {scene.frame_end}")

def on_render_complete(scene):
    """Called when render completes"""
    global render_start_time, render_stats
    if render_start_time:
        total_time = time.time() - render_start_time
        render_stats["total_time"] = total_time
        render_stats["is_rendering"] = False

        props = scene.render_time_props
        if props.notify_complete:
            bpy.ops.render.time_tracker_notification(
                message=f"Render Complete! Total time: {format_time(total_time)}",
                type='INFO'
            )

        if props.auto_export:
            bpy.ops.render.export_stats()

        print(f"[Render Time Tracker] Render Completed in {format_time(total_time)}")

def on_render_cancel(scene):
    """Called when render is cancelled"""
    global render_stats
    render_stats["is_rendering"] = False
    print("[Render Time Tracker] Render Cancelled")

def on_frame_pre(scene):
    """Called before frame render"""
    global frame_start_time
    frame_start_time = time.time()

def on_frame_post(scene):
    """Called after frame render"""
    global frame_start_time, total_frames_rendered, render_stats, render_history

    if frame_start_time:
        frame_time = time.time() - frame_start_time
        total_frames_rendered += 1
        render_stats["current_frame_time"] = frame_time
        render_stats["frame_count"] = total_frames_rendered

        # Add to history
        props = scene.render_time_props
        item = props.history.add()
        item.frame = scene.frame_current
        item.time = frame_time
        item.timestamp = time.strftime("%H:%M:%S")

        # Calculate average
        if total_frames_rendered > 0:
            render_stats["average_time"] = render_stats["total_time"] / total_frames_rendered

        # Calculate ETA
        if scene.frame_end > scene.frame_start:
            remaining_frames = scene.frame_end - scene.frame_current
            render_stats["estimated_remaining"] = remaining_frames * render_stats["average_time"]

        render_stats["total_time"] = time.time() - render_start_time if render_start_time else 0

        # Print to console
        print(f"[Render Time Tracker] Frame {scene.frame_current}: {format_time(frame_time)} | Total: {format_time(render_stats['total_time'])}")

# Operators
class RENDER_OT_start_with_tracker(Operator):
    """Start render with time tracking"""
    bl_idname = "render.start_with_tracker"
    bl_label = "Render with Tracker"
    bl_description = "Start rendering with time tracking enabled"
    bl_options = {'REGISTER'}

    animation: BoolProperty(default=False)

    def execute(self, context):
        if self.animation:
            bpy.ops.render.render('INVOKE_DEFAULT', animation=True)
        else:
            bpy.ops.render.render('INVOKE_DEFAULT')
        return {'FINISHED'}

class RENDER_OT_reset_stats(Operator):
    """Reset render statistics"""
    bl_idname = "render.reset_stats"
    bl_label = "Reset Stats"
    bl_description = "Reset all render statistics"
    bl_options = {'REGISTER'}

    def execute(self, context):
        global render_stats, total_frames_rendered, render_history
        render_stats = {
            "total_time": 0,
            "current_frame_time": 0,
            "average_time": 0,
            "estimated_remaining": 0,
            "is_rendering": False,
            "frame_count": 0,
            "start_frame": 0,
            "end_frame": 0,
        }
        total_frames_rendered = 0
        render_history = []
        context.scene.render_time_props.history.clear()
        self.report({'INFO'}, "Render statistics reset")
        return {'FINISHED'}

class RENDER_OT_export_stats(Operator):
    """Export render statistics to file"""
    bl_idname = "render.export_stats"
    bl_label = "Export Stats"
    bl_description = "Export render statistics to file"
    bl_options = {'REGISTER'}

    filepath: StringProperty(subtype='FILE_PATH')

    def execute(self, context):
        global render_stats
        props = context.scene.render_time_props

        try:
            filepath = bpy.path.abspath(self.filepath)

            if props.export_format == 'TXT':
                self.export_txt(filepath, context)
            elif props.export_format == 'CSV':
                self.export_csv(filepath, context)
            elif props.export_format == 'JSON':
                self.export_json(filepath, context)

            self.report({'INFO'}, f"Stats exported to {filepath}")
        except Exception as e:
            self.report({'ERROR'}, str(e))
        return {'FINISHED'}

    def export_txt(self, filepath, context):
        with open(filepath, 'w') as f:
            f.write("=" * 50 + "\n")
            f.write("     RENDER TIME STATISTICS\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"Export Time: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Scene: {bpy.path.basename(bpy.data.filepath)}\n\n")
            f.write(f"Total Time:       {format_time(render_stats['total_time'])}\n")
            f.write(f"Frames Rendered:  {render_stats['frame_count']}\n")
            f.write(f"Average/Frame:    {format_time(render_stats['average_time'])}\n")
            f.write(f"Last Frame Time:  {format_time(render_stats['current_frame_time'])}\n")
            f.write(f"Estimated Remain: {format_time(render_stats['estimated_remaining'])}\n\n")
            f.write("Frame History:\n")
            f.write("-" * 30 + "\n")
            for item in context.scene.render_time_props.history:
                f.write(f"Frame {item.frame:4d}: {format_time(item.time)}\n")

    def export_csv(self, filepath, context):
        with open(filepath, 'w') as f:
            f.write("Frame,Time_Seconds,Timestamp\n")
            for item in context.scene.render_time_props.history:
                f.write(f"{item.frame},{item.time},{item.timestamp}\n")

    def export_json(self, filepath, context):
        import json
        data = {
            "summary": {
                "total_time": render_stats["total_time"],
                "frame_count": render_stats["frame_count"],
                "average_time": render_stats["average_time"],
                "estimated_remaining": render_stats["estimated_remaining"],
            },
            "frames": [
                {"frame": item.frame, "time": item.time, "timestamp": item.timestamp}
                for item in context.scene.render_time_props.history
            ]
        }
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)

    def invoke(self, context, event):
        props = context.scene.render_time_props

        if props.export_format == 'TXT':
            self.filepath = "//render_stats.txt"
        elif props.export_format == 'CSV':
            self.filepath = "//render_stats.csv"
        elif props.export_format == 'JSON':
            self.filepath = "//render_stats.json"

        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

class RENDER_OT_time_tracker_notification(Operator):
    """Show notification"""
    bl_idname = "render.time_tracker_notification"
    bl_label = "Notification"
    bl_options = {'REGISTER', 'INTERNAL'}

    message: StringProperty()
    type: StringProperty(default='INFO')

    def execute(self, context):
        self.report({self.type}, self.message)
        return {'FINISHED'}

class RENDER_OT_clear_history(Operator):
    """Clear render history"""
    bl_idname = "render.clear_history"
    bl_label = "Clear History"
    bl_description = "Clear all frame history"
    bl_options = {'REGISTER'}

    def execute(self, context):
        context.scene.render_time_props.history.clear()
        self.report({'INFO'}, "History cleared")
        return {'FINISHED'}

# Panels
class RENDER_PT_time_tracker_main(Panel):
    """Main Render Time Tracker Panel"""
    bl_label = "Render Time Tracker"
    bl_idname = "RENDER_PT_time_tracker_main"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Render Time"

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        props = scene.render_time_props

        # Render Buttons
        box = layout.box()
        box.label(text="Render", icon='RENDER_ANIMATION')
        row = box.row(align=True)
        row.scale_y = 1.5
        row.operator("render.start_with_tracker", text="Image", icon='RENDER_STILL').animation = False
        row.operator("render.start_with_tracker", text="Animation", icon='RENDER_ANIMATION').animation = True

        # Live Stats Display
        box = layout.box()
        box.label(text="Live Statistics", icon='TIME')

        col = box.column(align=True)

        # Status with color
        row = col.row(align=True)
        if render_stats["is_rendering"]:
            row.alert = True
            row.label(text="🔴 RENDERING", icon='RENDER_ANIMATION')
        else:
            row.label(text="⚪ IDLE", icon='SNAP_FACE')

        col.separator()

        # Stats grid
        if props.show_total_time:
            row = col.row(align=True)
            row.label(text="⏱️ Total:")
            row.label(text=format_time(render_stats["total_time"]))

        if props.show_per_frame:
            row = col.row(align=True)
            row.label(text="⚡ Last Frame:")
            row.label(text=format_time(render_stats["current_frame_time"]))

            row = col.row(align=True)
            row.label(text="📊 Average:")
            row.label(text=format_time(render_stats["average_time"]))

        if props.show_eta and render_stats["is_rendering"]:
            row = col.row(align=True)
            row.label(text="⏳ ETA:")
            row.label(text=format_time(render_stats["estimated_remaining"]))

        # Progress bar
        if props.show_progress_bar and render_stats["end_frame"] > render_stats["start_frame"]:
            total_frames = render_stats["end_frame"] - render_stats["start_frame"] + 1
            if total_frames > 0:
                progress = render_stats["frame_count"] / total_frames
                col.separator()
                col.progress(factor=progress, text=f"{int(progress*100)}% ({render_stats['frame_count']}/{total_frames})")

        col.separator()
        col.label(text=f"🎬 Frames: {render_stats['frame_count']}")

class RENDER_PT_time_tracker_settings(Panel):
    """Settings Panel"""
    bl_label = "Settings"
    bl_idname = "RENDER_PT_time_tracker_settings"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Render Time"
    bl_parent_id = "RENDER_PT_time_tracker_main"

    def draw(self, context):
        layout = self.layout
        props = context.scene.render_time_props

        # Display settings
        box = layout.box()
        box.label(text="Display", icon='PREFERENCES')
        col = box.column(align=True)
        col.prop(props, "show_total_time")
        col.prop(props, "show_per_frame")
        col.prop(props, "show_eta")
        col.prop(props, "show_progress_bar")

        # Notifications
        box = layout.box()
        box.label(text="Notifications", icon='INFO')
        col = box.column(align=True)
        col.prop(props, "notify_complete")
        col.prop(props, "notify_sound")

        # Export
        box = layout.box()
        box.label(text="Auto Export", icon='EXPORT')
        col = box.column(align=True)
        col.prop(props, "auto_export")
        if props.auto_export:
            col.prop(props, "export_path")
            col.prop(props, "export_format")

class RENDER_PT_time_tracker_history(Panel):
    """History Panel"""
    bl_label = "Frame History"
    bl_idname = "RENDER_PT_time_tracker_history"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Render Time"
    bl_parent_id = "RENDER_PT_time_tracker_main"

    def draw(self, context):
        layout = self.layout
        props = context.scene.render_time_props

        # History list
        box = layout.box()
        row = box.row()
        row.label(text="Frame")
        row.label(text="Time")
        row.label(text="Timestamp")

        for i, item in enumerate(props.history):
            row = box.row()
            row.label(text=str(item.frame))
            row.label(text=format_time(item.time))
            row.label(text=item.timestamp)

        if len(props.history) == 0:
            box.label(text="No frames rendered yet", icon='INFO')

        # Actions
        row = layout.row(align=True)
        row.operator("render.clear_history", icon='TRASH')
        row.operator("render.export_stats", icon='EXPORT')

class RENDER_PT_time_tracker_render_window(Panel):
    """Render Time Tracker in Image Editor (Render Window)"""
    bl_label = "Render Stats"
    bl_idname = "RENDER_PT_time_tracker_render_window"
    bl_space_type = 'IMAGE_EDITOR'
    bl_region_type = 'UI'
    bl_category = "Render Stats"

    def draw(self, context):
        layout = self.layout
        props = context.scene.render_time_props

        # Main stats display in render window
        box = layout.box()

        # Status
        col = box.column(align=True)
        col.scale_y = 1.2

        if render_stats["is_rendering"]:
            col.alert = True
            col.label(text="🔴 RENDERING", icon='RENDER_ANIMATION')
        else:
            col.label(text="⚪ IDLE", icon='SNAP_FACE')

        col.separator()

        # Time display with icons
        row = col.row(align=True)
        row.label(text="⏱️ Total Time:", icon='TIME')
        row.label(text=format_time(render_stats["total_time"]))

        row = col.row(align=True)
        row.label(text="⚡ Last Frame:", icon='FRAME_NEXT')
        row.label(text=format_time(render_stats["current_frame_time"]))

        row = col.row(align=True)
        row.label(text="📊 Average:", icon='GRAPH')
        row.label(text=format_time(render_stats["average_time"]))

        if render_stats["is_rendering"]:
            row = col.row(align=True)
            row.label(text="⏳ ETA:", icon='PREVIEW_RANGE')
            row.label(text=format_time(render_stats["estimated_remaining"]))

        col.separator()

        # Frame info
        row = col.row(align=True)
        row.label(text=f"🎬 Frames: {render_stats['frame_count']}")

        if render_stats["end_frame"] > 0:
            total = render_stats["end_frame"] - render_stats["start_frame"] + 1
            row.label(text=f"Progress: {render_stats['frame_count']}/{total}")

        # Progress bar
        if render_stats["end_frame"] > render_stats["start_frame"]:
            total_frames = render_stats["end_frame"] - render_stats["start_frame"] + 1
            if total_frames > 0:
                progress = render_stats["frame_count"] / total_frames
                col.separator()
                col.progress(factor=progress, text=f"{int(progress*100)}%")

class RENDER_PT_time_tracker_node_editor(Panel):
    """Panel in Node Editor for compositor renders"""
    bl_label = "Render Time Stats"
    bl_idname = "RENDER_PT_time_tracker_node_editor"
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'
    bl_category = "Render Stats"

    def draw(self, context):
        layout = self.layout

        box = layout.box()
        col = box.column(align=True)

        row = col.row(align=True)
        row.label(text="Status:", icon='TIME')
        if render_stats["is_rendering"]:
            row.label(text="Rendering...", icon='RENDER_ANIMATION')
        else:
            row.label(text="Idle")

        col.separator()
        col.label(text=f"Total: {format_time(render_stats['total_time'])}")
        col.label(text=f"Last: {format_time(render_stats['current_frame_time'])}")
        col.label(text=f"Avg: {format_time(render_stats['average_time'])}")
        col.label(text=f"Frames: {render_stats['frame_count']}")

# Addon Preferences
class RenderTimeTrackerPreferences(AddonPreferences):
    bl_idname = __package__

    default_auto_export: BoolProperty(
        name="Default Auto Export",
        default=False
    )

    default_export_format: EnumProperty(
        name="Default Export Format",
        items=[
            ('TXT', "Text", ""),
            ('CSV', "CSV", ""),
            ('JSON', "JSON", ""),
        ],
        default='TXT'
    )

    show_in_header: BoolProperty(
        name="Show in Header",
        description="Show render stats in 3D viewport header",
        default=True
    )

    def draw(self, context):
        layout = self.layout
        layout.label(text="Render Time Tracker - Default Settings")
        layout.prop(self, "default_auto_export")
        layout.prop(self, "default_export_format")
        layout.prop(self, "show_in_header")

# Registration
classes = [
    RenderTimeItem,
    RenderTimeProperties,
    RenderTimeTrackerPreferences,
    RENDER_OT_start_with_tracker,
    RENDER_OT_reset_stats,
    RENDER_OT_export_stats,
    RENDER_OT_time_tracker_notification,
    RENDER_OT_clear_history,
    RENDER_PT_time_tracker_main,
    RENDER_PT_time_tracker_settings,
    RENDER_PT_time_tracker_history,
    RENDER_PT_time_tracker_render_window,
    RENDER_PT_time_tracker_node_editor,
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.render_time_props = bpy.props.PointerProperty(type=RenderTimeProperties)

    # Register render handlers
    bpy.app.handlers.render_init.append(on_render_init)
    bpy.app.handlers.render_complete.append(on_render_complete)
    bpy.app.handlers.render_cancel.append(on_render_cancel)
    bpy.app.handlers.render_pre.append(on_frame_pre)
    bpy.app.handlers.render_post.append(on_frame_post)

    print("[Render Time Tracker] Addon Registered Successfully")

def unregister():
    # Unregister render handlers
    bpy.app.handlers.render_init.remove(on_render_init)
    bpy.app.handlers.render_complete.remove(on_render_complete)
    bpy.app.handlers.render_cancel.remove(on_render_cancel)
    bpy.app.handlers.render_pre.remove(on_frame_pre)
    bpy.app.handlers.render_post.remove(on_frame_post)

    del bpy.types.Scene.render_time_props

    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

    print("[Render Time Tracker] Addon Unregistered")

if __name__ == "__main__":
    register()
