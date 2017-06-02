# -*- coding: utf-8 -*-
"""
Created on Fri Jun  2 11:05:38 2017

@author: crosby
"""
import os, shutil

# Remove all files from folder (leave directories, uncomment below if want to remove subdirectories)
def clean_folder(folder):    
    for the_file in os.listdir(folder):
        file_path = os.path.join(folder, the_file)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
            #elif os.path.isdir(file_path): shutil.rmtree(file_path)
        except Exception as e:
            print(e)