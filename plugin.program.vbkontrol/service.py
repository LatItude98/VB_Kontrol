#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
VB Kontrol - Universal Video Background Service
Background service that manages video background window properties for skins
"""

import xbmc
import xbmcaddon
import xbmcgui
import xbmcvfs
import os
import time

class VBKontrolService:
    def __init__(self):
        self.addon = xbmcaddon.Addon()
        self.addon_name = self.addon.getAddonInfo('name')
        self.addon_version = self.addon.getAddonInfo('version')
        self.monitor = xbmc.Monitor()
        self.running = False
        self.num_slots = 20
        
        # Set up folders
        self.setup_folders()
        
        self.log(f"VB Kontrol v{self.addon_version} - Universal Video Background Service")
    
    def log(self, message, level=xbmc.LOGINFO):
        """Log messages with VBKontrol prefix"""
        xbmc.log(f"[VBKontrol Service] {message}", level)
    
    def setup_folders(self):
        """Create necessary folders"""
        try:
            # Create video_backgrounds folder using special:// path
            video_folder_path = "special://home/userdata/addon_data/plugin.program.vbkontrol/video_backgrounds/"
            video_folder = xbmcvfs.translatePath(video_folder_path)
            
            if not xbmcvfs.exists(video_folder):
                xbmcvfs.mkdirs(video_folder)
                self.log("Created video_backgrounds folder")
            
            self.video_folder = video_folder
        except Exception as e:
            self.log(f"Error setting up folders: {e}", xbmc.LOGERROR)
    
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
    
    def update_window_properties(self):
        """Update all window properties for skins to use"""
        try:
            window = xbmcgui.Window(10000)
            
            # Service status
            window.setProperty('VBKontrol.Service.Running', 'true')
            window.setProperty('VBKontrol.Service.Version', self.addon_version)
            
            # Update all slot properties
            for i in range(1, self.num_slots + 1):
                slot_name = self.get_slot_name(i)
                slot_video = self.get_slot_video(i)
                
                if slot_video:
                    # Set properties for both slot name and slot number
                    window.setProperty(f'VBKontrol.{slot_name}.Video', slot_video)
                    window.setProperty(f'VBKontrol.Slot{i}.Video', slot_video)
                    
                    # Additional properties for convenience
                    video_filename = os.path.basename(slot_video)
                    window.setProperty(f'VBKontrol.{slot_name}.VideoFilename', video_filename)
                    window.setProperty(f'VBKontrol.Slot{i}.VideoFilename', video_filename)
                    
                    # Check if file exists
                    exists = "true" if xbmcvfs.exists(slot_video) else "false"
                    window.setProperty(f'VBKontrol.{slot_name}.VideoExists', exists)
                    window.setProperty(f'VBKontrol.Slot{i}.VideoExists', exists)
                else:
                    # Clear properties if no video
                    window.clearProperty(f'VBKontrol.{slot_name}.Video')
                    window.clearProperty(f'VBKontrol.Slot{i}.Video')
                    window.clearProperty(f'VBKontrol.{slot_name}.VideoFilename')
                    window.clearProperty(f'VBKontrol.Slot{i}.VideoFilename')
                    window.clearProperty(f'VBKontrol.{slot_name}.VideoExists')
                    window.clearProperty(f'VBKontrol.Slot{i}.VideoExists')
                
                # Always set the slot name property
                window.setProperty(f'VBKontrol.Slot{i}.Name', slot_name)
            
            # Set total slots property
            window.setProperty('VBKontrol.TotalSlots', str(self.num_slots))
            
        except Exception as e:
            self.log(f"Error updating window properties: {e}", xbmc.LOGERROR)
    
    def start(self):
        """Start the service"""
        self.log("Starting VB Kontrol service...")
        self.running = True
        
        # Initial property update
        self.update_window_properties()
        
        self.log("VB Kontrol service started - monitoring for changes")
        
        # Main service loop
        last_update = 0
        update_interval = 10  # Update every 10 seconds
        
        while self.running and not self.monitor.abortRequested():
            try:
                current_time = time.time()
                
                # Update window properties periodically
                if current_time - last_update >= update_interval:
                    self.update_window_properties()
                    last_update = current_time
                
                # Wait 1 second before next check
                if self.monitor.waitForAbort(1):
                    break
                    
            except Exception as e:
                self.log(f"Error in service loop: {e}", xbmc.LOGERROR)
                # Wait a bit longer on error to prevent spam
                if self.monitor.waitForAbort(5):
                    break
        
        self.stop()
    
    def stop(self):
        """Stop the service and cleanup"""
        self.log("Stopping VB Kontrol service...")
        self.running = False
        
        try:
            # Clear all window properties
            window = xbmcgui.Window(10000)
            window.clearProperty('VBKontrol.Service.Running')
            window.clearProperty('VBKontrol.Service.Version')
            window.clearProperty('VBKontrol.TotalSlots')
            
            # Clear all slot properties
            for i in range(1, self.num_slots + 1):
                slot_name = self.get_slot_name(i)
                window.clearProperty(f'VBKontrol.{slot_name}.Video')
                window.clearProperty(f'VBKontrol.Slot{i}.Video')
                window.clearProperty(f'VBKontrol.{slot_name}.VideoFilename')
                window.clearProperty(f'VBKontrol.Slot{i}.VideoFilename')
                window.clearProperty(f'VBKontrol.{slot_name}.VideoExists')
                window.clearProperty(f'VBKontrol.Slot{i}.VideoExists')
                window.clearProperty(f'VBKontrol.Slot{i}.Name')
            
        except Exception as e:
            self.log(f"Error during cleanup: {e}", xbmc.LOGERROR)
        
        self.log("VB Kontrol service stopped")

def main():
    """Main entry point for the service"""
    service = None
    
    try:
        service = VBKontrolService()
        service.start()
        
    except Exception as e:
        if service:
            service.log(f"Service crashed: {e}", xbmc.LOGERROR)
        else:
            xbmc.log(f"[VBKontrol Service] Critical startup error: {e}", xbmc.LOGERROR)
    
    finally:
        if service:
            service.stop()

if __name__ == '__main__':
    main()