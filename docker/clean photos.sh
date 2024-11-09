#!/bin/bash

# Define the directory and the date
echo "This script will remove all files in the target directory after the date given."
read -p "Target Directory: " TARGET_DIR
read -p "Starting Date: " START_DATE
read -p "End Date": END_DATE

# Find and delete files modified after the specified date
find "$TARGET_DIR" -type f -newermt "$START_DATE" ! -newermt "$END_DATE" -exec rm -f {} \;

echo "Files deleted between $START_DATE and $END_DATE in $TARGET_DIR."
