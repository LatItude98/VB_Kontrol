#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
VB Kontrol - Universal Video Background Interface
20 configurable video background slots for any skin
"""

import xbmc
import xbmcaddon
import xbmcgui
import xbmcplugin
import xbmcvfs
import sys
import os
from urllib.parse import parse_qsl

class VBKontrol:
    def __init__(self):
        self.addon = xbmcaddon.Addon()
        self.addon_handle = int(sys.argv[1])
        self.num_slots = 20  # 20 slots for maximum skin compatibility
        
        # Create video_backgrounds folder if it doesn't exist
        self.video_folder = self.get_video_backgrounds_folder()
        if not xbmcvfs.exists(self.video_folder):
            xbmcvfs.mkdirs(self.video_folder)
            self.log("Created video_backgrounds folder")
    
    def log(self, message, level=xbmc.LOGINFO):
        """Log messages with VBKontrol prefix"""
        xbmc.log(f"[VBKontrol] {message}", level)
    
    def get_video_backgrounds_folder(self):
        """Get the video_backgrounds folder path using special:// paths"""
        # Use special://home/userdata/addon_data/plugin.program.vbkontrol/video_backgrounds/
        video_folder = "special://home/userdata/addon_data/plugin.program.vbkontrol/video_backgrounds/"
        
        # Translate to real path for existence check and creation
        real_path = xbmcvfs.translatePath(video_folder)
        
        # Ensure it exists
        if not xbmcvfs.exists(real_path):
            xbmcvfs.mkdirs(real_path)
            self.log("Created video_backgrounds folder")
            
        return video_folder  # Return the special:// path for file browser
    
    def get_slot_name(self, slot_num):
        """Get the name for a slot - with universal defaults"""
        try:
            # Try to get custom name first using special:// path
            custom_name_path = f"special://home/userdata/addon_data/plugin.program.vbkontrol/slot_{slot_num}_name.txt"
            custom_name = xbmcvfs.translatePath(custom_name_path)
            if xbmcvfs.exists(custom_name):
                with open(custom_name, 'r', encoding='utf-8') as f:
                    name = f.read().strip()
                    if name:
                        return name
        except:
            pass
        
        # Return universal defaults if no custom name
        defaults = [
            "Home", "Movies", "TV Shows", "Music", "Pictures", 
            "Videos", "Favourites", "Add-ons", "Settings", "Weather",
            "Programs", "Games", "System", "Live TV", "Radio",
            "Files", "Playlists", "Custom 1", "Custom 2", "Custom 3"
        ]
        
        if 1 <= slot_num <= len(defaults):
            return defaults[slot_num - 1]
        else:
            return f"Slot {slot_num}"
    
    def get_slot_video(self, slot_num):
        """Get the video file for a slot"""
        try:
            video_file_path = f"special://home/userdata/addon_data/plugin.program.vbkontrol/slot_{slot_num}_video.txt"
            video_file = xbmcvfs.translatePath(video_file_path)
            if xbmcvfs.exists(video_file):
                with open(video_file, 'r', encoding='utf-8') as f:
                    video_path = f.read().strip()
                    if video_path and xbmcvfs.exists(video_path):
                        return video_path
        except:
            pass
        return None
    
    def set_slot_name(self, slot_num, name):
        """Save custom name for a slot"""
        try:
            name_file_path = f"special://home/userdata/addon_data/plugin.program.vbkontrol/slot_{slot_num}_name.txt"
            name_file = xbmcvfs.translatePath(name_file_path)
            # Create directory if needed
            dir_path = os.path.dirname(name_file)
            if not xbmcvfs.exists(dir_path):
                xbmcvfs.mkdirs(dir_path)
            
            with open(name_file, 'w', encoding='utf-8') as f:
                f.write(name)
            return True
        except Exception as e:
            self.log(f"Error saving slot name: {e}", xbmc.LOGERROR)
            return False
    
    def set_slot_video(self, slot_num, video_path):
        """Save video file for a slot"""
        try:
            video_file_path = f"special://home/userdata/addon_data/plugin.program.vbkontrol/slot_{slot_num}_video.txt"
            video_file = xbmcvfs.translatePath(video_file_path)
            # Create directory if needed
            dir_path = os.path.dirname(video_file)
            if not xbmcvfs.exists(dir_path):
                xbmcvfs.mkdirs(dir_path)
            
            with open(video_file, 'w', encoding='utf-8') as f:
                f.write(video_path)
            
            # Update window property for skins
            slot_name = self.get_slot_name(slot_num)
            window = xbmcgui.Window(10000)
            window.setProperty(f'VBKontrol.{slot_name}.Video', video_path)
            window.setProperty(f'VBKontrol.Slot{slot_num}.Video', video_path)
            
            self.log(f"Set video for {slot_name}: {os.path.basename(video_path)}")
            return True
        except Exception as e:
            self.log(f"Error saving slot video: {e}", xbmc.LOGERROR)
            return False
    
    def show_main_menu(self):
        """Show the main VBKontrol menu"""
        listing = []
        
        # Add header
        item = xbmcgui.ListItem("=== VB Kontrol - Universal Video Backgrounds ===")
        item.setInfo('video', {'title': "VB Kontrol", 'plot': "Configure video backgrounds for any skin"})
        listing.append((None, item, False))
        
        # Global video option
        item = xbmcgui.ListItem("🌍 Global Video Background")
        item.setInfo('video', {'title': "Global Video", 'plot': "Set one video for all menus"})
        url = f"plugin://plugin.program.vbkontrol/?action=global_video"
        listing.append((url, item, False))
        
        # Separator
        item = xbmcgui.ListItem("--- Video Background Slots (20 Total) ---")
        listing.append((None, item, False))
        
        # Show all 20 configurable slots
        for i in range(1, self.num_slots + 1):
            slot_name = self.get_slot_name(i)
            slot_video = self.get_slot_video(i)
            
            if slot_video:
                video_name = os.path.basename(slot_video)
                label = f"📹 {slot_name} → {video_name}"
                plot = f"Current video: {video_name}\nClick to change or clear"
            else:
                label = f"⭕ {slot_name}"
                plot = "No video selected\nClick to select video file"
            
            item = xbmcgui.ListItem(label)
            item.setInfo('video', {'title': slot_name, 'plot': plot})
            url = f"plugin://plugin.program.vbkontrol/?action=configure_slot&slot={i}"
            listing.append((url, item, False))
        
        # Separator and utilities
        item = xbmcgui.ListItem("--- Utilities ---")
        listing.append((None, item, False))
        
        # Clear all
        item = xbmcgui.ListItem("🗑️ Clear All Video Backgrounds")
        item.setInfo('video', {'title': "Clear All", 'plot': "Remove all video background assignments"})
        url = f"plugin://plugin.program.vbkontrol/?action=clear_all"
        listing.append((url, item, False))
        
        # Service status
        window = xbmcgui.Window(10000)
        service_running = window.getProperty('VBKontrol.Service.Running') == 'true'
        status = "✅ Service Running" if service_running else "❌ Service Stopped"
        
        item = xbmcgui.ListItem(f"ℹ️ {status}")
        item.setInfo('video', {'title': "Service Status", 'plot': f"Background service status: {status}"})
        listing.append((None, item, False))
        
        # Add items to directory
        xbmcplugin.addDirectoryItems(self.addon_handle, listing, len(listing))
        xbmcplugin.endOfDirectory(self.addon_handle)
    
    def configure_slot(self, slot_num):
        """Configure a specific slot"""
        slot_name = self.get_slot_name(slot_num)
        slot_video = self.get_slot_video(slot_num)
        
        # Create menu for slot configuration
        dialog = xbmcgui.Dialog()
        
        options = ["Select Video File", "Rename Slot"]
        if slot_video:
            options.insert(1, "Clear Video")
        
        choice = dialog.select(f"Configure: {slot_name}", options)
        
        if choice == 0:  # Select Video File
            self.select_video_for_slot(slot_num)
        elif choice == 1 and slot_video:  # Clear Video (if video exists)
            self.clear_slot_video(slot_num)
        elif choice == 1 and not slot_video or choice == 2:  # Rename Slot
            self.rename_slot(slot_num)
    
    def select_video_for_slot(self, slot_num):
        """Select a video file for a specific slot"""
        dialog = xbmcgui.Dialog()
        
        # Open file browser in video_backgrounds folder
        video_path = dialog.browse(
            1,  # Browse for file
            f"Select video for {self.get_slot_name(slot_num)}",
            'video',
            '.mp4|.mkv|.avi|.mov|.wmv|.flv|.webm|.m4v',
            False,  # Use thumbs
            False,  # Treat as folder
            self.video_folder  # Default path
        )
        
        if video_path:
            if self.set_slot_video(slot_num, video_path):
                dialog.notification(
                    "VB Kontrol",
                    f"Video set for {self.get_slot_name(slot_num)}",
                    xbmcgui.NOTIFICATION_INFO,
                    3000
                )
            else:
                dialog.notification(
                    "VB Kontrol",
                    "Error setting video file",
                    xbmcgui.NOTIFICATION_ERROR,
                    3000
                )
    
    def clear_slot_video(self, slot_num):
        """Clear video for a slot"""
        try:
            video_file_path = f"special://home/userdata/addon_data/plugin.program.vbkontrol/slot_{slot_num}_video.txt"
            video_file = xbmcvfs.translatePath(video_file_path)
            if xbmcvfs.exists(video_file):
                xbmcvfs.delete(video_file)
            
            # Clear window properties
            slot_name = self.get_slot_name(slot_num)
            window = xbmcgui.Window(10000)
            window.clearProperty(f'VBKontrol.{slot_name}.Video')
            window.clearProperty(f'VBKontrol.Slot{slot_num}.Video')
            
            dialog = xbmcgui.Dialog()
            dialog.notification(
                "VB Kontrol",
                f"Video cleared for {slot_name}",
                xbmcgui.NOTIFICATION_INFO,
                3000
            )
        except Exception as e:
            self.log(f"Error clearing slot video: {e}", xbmc.LOGERROR)
    
    def rename_slot(self, slot_num):
        """Rename a slot"""
        dialog = xbmcgui.Dialog()
        current_name = self.get_slot_name(slot_num)
        
        new_name = dialog.input(
            f"Rename slot (currently: {current_name})",
            current_name,
            type=xbmcgui.INPUT_ALPHANUM
        )
        
        if new_name and new_name != current_name:
            if self.set_slot_name(slot_num, new_name):
                # Update window property with new name
                slot_video = self.get_slot_video(slot_num)
                if slot_video:
                    window = xbmcgui.Window(10000)
                    # Clear old property
                    window.clearProperty(f'VBKontrol.{current_name}.Video')
                    # Set new property
                    window.setProperty(f'VBKontrol.{new_name}.Video', slot_video)
                
                dialog.notification(
                    "VB Kontrol",
                    f"Renamed to: {new_name}",
                    xbmcgui.NOTIFICATION_INFO,
                    3000
                )
    
    def set_global_video(self):
        """Set global video for all slots"""
        dialog = xbmcgui.Dialog()
        
        video_path = dialog.browse(
            1,  # Browse for file
            "Select global video file",
            'video',
            '.mp4|.mkv|.avi|.mov|.wmv|.flv|.webm|.m4v',
            False,
            False,
            self.video_folder
        )
        
        if video_path:
            # Set for all slots
            count = 0
            for i in range(1, self.num_slots + 1):
                if self.set_slot_video(i, video_path):
                    count += 1
            
            dialog.notification(
                "VB Kontrol",
                f"Global video set for {count} slots",
                xbmcgui.NOTIFICATION_INFO,
                3000
            )
    
    def clear_all_videos(self):
        """Clear all video backgrounds"""
        dialog = xbmcgui.Dialog()
        
        if dialog.yesno("VB Kontrol", "Clear all video backgrounds?"):
            count = 0
            for i in range(1, self.num_slots + 1):
                try:
                    video_file_path = f"special://home/userdata/addon_data/plugin.program.vbkontrol/slot_{i}_video.txt"
                    video_file = xbmcvfs.translatePath(video_file_path)
                    if xbmcvfs.exists(video_file):
                        xbmcvfs.delete(video_file)
                        count += 1
                    
                    # Clear window properties
                    slot_name = self.get_slot_name(i)
                    window = xbmcgui.Window(10000)
                    window.clearProperty(f'VBKontrol.{slot_name}.Video')
                    window.clearProperty(f'VBKontrol.Slot{i}.Video')
                except:
                    pass
            
            dialog.notification(
                "VB Kontrol",
                f"Cleared {count} video backgrounds",
                xbmcgui.NOTIFICATION_INFO,
                3000
            )
    
    def router(self, paramstring):
        """Route addon calls to appropriate functions"""
        params = dict(parse_qsl(paramstring))
        action = params.get('action')
        
        if action == 'configure_slot':
            slot_num = int(params.get('slot', 1))
            self.configure_slot(slot_num)
        elif action == 'global_video':
            self.set_global_video()
        elif action == 'clear_all':
            self.clear_all_videos()
        else:
            # Show main menu
            self.show_main_menu()

def main():
    """Main entry point"""
    try:
        vbk = VBKontrol()
        vbk.router(sys.argv[2][1:])  # Remove the leading '?'
    except Exception as e:
        xbmc.log(f"[VBKontrol] Error: {e}", xbmc.LOGERROR)

if __name__ == '__main__':
    main()