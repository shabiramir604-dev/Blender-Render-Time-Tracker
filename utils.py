import time
import bpy
import os

def format_time(seconds):
    """Format seconds to HH:MM:SS.ms"""
    if seconds < 0 or seconds is None:
        return "00:00:00.00"
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds % 1) * 100)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}.{millis:02d}"

def format_time_compact(seconds):
    """Format seconds to compact string"""
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        return f"{seconds/60:.1f}m"
    else:
        return f"{seconds/3600:.1f}h"

def get_scene_info():
    """Get current scene information"""
    scene = bpy.context.scene
    return {
        "frame_start": scene.frame_start,
        "frame_end": scene.frame_end,
        "frame_current": scene.frame_current,
        "total_frames": scene.frame_end - scene.frame_start + 1,
        "filepath": bpy.path.basename(bpy.data.filepath),
        "resolution": (scene.render.resolution_x, scene.render.resolution_y),
        "fps": scene.render.fps,
    }

def estimate_file_size():
    """Estimate output file size in MB"""
    scene = bpy.context.scene
    width = scene.render.resolution_x
    height = scene.render.resolution_y
    # Rough estimate: 4 bytes per pixel (RGBA)
    size_bytes = width * height * 4
    return size_bytes / (1024 * 1024)

def get_system_info():
    """Get system information"""
    import sys
    import platform
    return {
        "blender_version": bpy.app.version_string,
        "python_version": sys.version,
        "platform": platform.platform(),
        "cpu_count": os.cpu_count(),
    }

def ensure_dir(filepath):
    """Ensure directory exists"""
    directory = os.path.dirname(filepath)
    if directory and not os.path.exists(directory):
        os.makedirs(directory)

def get_addon_path():
    """Get addon installation path"""
    return os.path.dirname(os.path.realpath(__file__))
