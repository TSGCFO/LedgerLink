#!/usr/bin/bash

# Check for required dependencies
command -v find >/dev/null 2>&1 || { echo "Error: find command is required but not found"; exit 3; }

# Function to display comprehensive help information
show_help() {
  echo "==================================================================="
  echo "                    FILE CHARACTER VALIDATOR"
  echo "==================================================================="
  echo
  echo "DESCRIPTION:"
  echo "  This script identifies and lists files with characters that are"
  echo "  unsupported in Windows file systems. It provides a comprehensive"
  echo "  way to detect files that might cause compatibility issues when"
  echo "  transferring data between Unix/Linux and Windows systems."
  echo
  echo "SYNTAX:"
  echo "  $0 -us [directory_path] [depth_level]"
  echo
  echo "OPTIONS:"
  echo "  -us                 Activate unsupported character search mode."
  echo "                      This is required to start the search process."
  echo
  echo "PARAMETERS:"
  echo "  directory_path      Optional: Specifies the directory to search."
  echo "                      If omitted, the current directory is used."
  echo "                      The path can be absolute or relative."
  echo "                      Examples: ~/Documents, /home/user/files, ./data"
  echo
  echo "  depth_level         Optional: Specifies how deep the search should go"
  echo "                      into subdirectories. Accepts values from 1 to 6:"
  echo "                      1: Current directory and immediate subdirectories (default)"
  echo "                      2: Includes subdirectories of immediate subdirectories"
  echo "                      ...and so on up to level 6"
  echo "                      Higher values may significantly increase search time."
  echo
  echo "UNSUPPORTED CHARACTERS:"
  echo "  The following characters are not supported in Windows filenames:"
  echo "  < (less than)             - ASCII 60"
  echo "  > (greater than)          - ASCII 62"
  echo "  : (colon)                 - ASCII 58"
  echo "  \" (double quote)          - ASCII 34"
  echo "  / (forward slash)         - ASCII 47"
  echo "  \\ (backslash)             - ASCII 92"
  echo "  | (vertical bar/pipe)     - ASCII 124"
  echo "  ? (question mark)         - ASCII 63"
  echo "  * (asterisk)              - ASCII 42"
  echo
  echo "  Additionally, Windows has these filename restrictions:"
  echo "  - Filenames cannot end with a space or period"
  echo "  - Cannot use reserved names: CON, PRN, AUX, NUL, COM1-COM9, LPT1-LPT9"
  echo
  echo "OUTPUT:"
  echo "  The script will display the full path of each file containing"
  echo "  one or more unsupported characters. If no files are found,"
  echo "  a message indicating this will be shown."
  echo
  echo "EXAMPLES:"
  echo "  $0 -us"
  echo "    Searches the current directory and immediate subdirectories"
  echo "    (depth level 1) for files with unsupported characters."
  echo
  echo "  $0 -us ~/Documents"
  echo "    Searches the Documents directory and its immediate subdirectories"
  echo "    for files with unsupported characters."
  echo
  echo "  $0 -us ~/Documents 3"
  echo "    Searches the Documents directory and its subdirectories up to"
  echo "    depth level 3 for files with unsupported characters."
  echo
  echo "  $0 -us 4"
  echo "    Searches the current directory and its subdirectories up to"
  echo "    depth level 4 for files with unsupported characters."
  echo
  echo "EXIT CODES:"
  echo "  0 - Successful execution"
  echo "  1 - Invalid directory path"
  echo "  2 - Invalid depth level (must be between 1 and 6)"
  echo "  3 - Required dependency not found"
  echo
  echo "NOTES:"
  echo "  - Symbolic links are not followed to prevent infinite loops"
  echo "  - Hidden files (starting with .) are included in the search"
  echo "  - The script may take longer to run on large directories or with"
  echo "    higher depth levels"
  echo "  - Error messages from inaccessible directories are suppressed"
  echo
  echo "AUTHOR:"
  echo "  Created by Script Generator"
  echo
  echo "VERSION:"
  echo "  1.0.0 - Initial release"
  echo
  echo "==================================================================="
}

# Function to check for unsupported Windows characters
check_unsupported_characters() {
  local file="${1}"
  local filename
  filename=$(basename "${file}")
  
  # Check for Windows unsupported characters: < > : " / \ | ? *
  if [[ "${filename}" =~ [\\/:*?\"\<\>|] ]]; then
    echo "${file}"
  fi
}

# Main script logic
if [[ "$1" == "-us" ]]; then
  # Default values
  local_dir="."
  depth=1
  
  # Check parameters
  if [[ -n "$2" ]]; then
    # Check if second parameter is a number (depth) or a path
    if [[ "$2" =~ ^[0-9]+$ ]]; then
      # It's a number, use it as depth
      depth="$2"
      if [ "${depth}" -lt 1 ] || [ "${depth}" -gt 6 ]; then
        echo "Error: Depth level must be between 1 and 6."
        exit 2
      fi
    else
      # It's a path
      local_dir="$2"
      
      # Check if the directory exists
      if [[ ! -d "${local_dir}" ]]; then
        echo "Error: Directory '${local_dir}' does not exist."
        exit 1
      fi
      
      # Check if there's a third parameter for depth
      if [[ -n "$3" ]]; then
        if [[ "$3" =~ ^[0-9]+$ ]]; then
          depth="$3"
          if [ "${depth}" -lt 1 ] || [ "${depth}" -gt 6 ]; then
            echo "Error: Depth level must be between 1 and 6."
            exit 2
          fi
        else
          echo "Error: Depth level must be a number between 1 and 6."
          exit 2
        fi
      fi
    fi
  fi
  
  echo "Searching for files with unsupported Windows characters in: ${local_dir}"
  echo "Search depth: ${depth}"
  echo "----------------------------------------"
  
  # Array to store problematic files
  declare -a problematic_files=()

  # Find files and check for unsupported characters
  found=false
  while IFS= read -r file; do
    result=$(check_unsupported_characters "${file}")
    if [[ -n "${result}" ]]; then
      echo "${result}"
      problematic_files+=("${result}")
      found=true
    fi
  done < <(find "${local_dir}" -maxdepth "${depth}" -type f 2>/dev/null)
  echo "----------------------------------------"

  if [[ "${found}" == false ]]; then
    echo "No files with unsupported Windows characters found."
    echo "Search complete."
    exit 0
  fi
  
  # Ask user if they want to delete the files
  files_count=${#problematic_files[@]}
  echo "Found ${files_count} file(s) with unsupported windows characters."
  read -r -p "Do you want to delete these files? (y/n): " answer
  
  if [[ "${answer}" == "y" || "${answer}" == "Y" ]]; then
    echo "Deleting files..."
    deleted_count=0
    for file in "${problematic_files[@]}"; do
      if rm -f "${file}"; then
        ((deleted_count++))
        echo "Deleted: ${file}"
      else
        echo "Failed to delete: ${file}"
      fi
    done
    echo "----------------------------------------"
    echo "Deleted ${deleted_count} of ${files_count} files."
  else
    echo "No files were deleted."
  fi

  echo "Search complete."
  exit 0    
else
  show_help
  exit 0
fi
