#!/usr/bin/bats

# Load helper libraries
load "bats-test/test_helper/bats-support/load"
load "bats-test/test_helper/bats-assert/load"
load "bats-test/test_helper/bats-file/load"

# Path to the script being tested
SCRIPT="/workspaces/LedgerLink/scripts/file-validator-optimized.sh"

# Ensure script is executable
setup() {
  chmod +x "$SCRIPT"
  # Create test directory
  TEST_DIR="${BATS_TMPDIR}/file_validator_test"
  mkdir -p "$TEST_DIR"
  
  # Create files with valid names
  echo "Content" > "${TEST_DIR}/valid-file.txt"
  echo "Content" > "${TEST_DIR}/another_valid_file.md"
  
  # Create subdirectories for depth testing
  mkdir -p "${TEST_DIR}/subdir1/subdir2/subdir3"
  echo "Content" > "${TEST_DIR}/subdir1/valid.txt"
  echo "Content" > "${TEST_DIR}/subdir1/subdir2/valid.txt"
  echo "Content" > "${TEST_DIR}/subdir1/subdir2/subdir3/valid.txt"
  
  # Create files with unsupported characters
  echo "Content" > "${TEST_DIR}/file<with>unsupported.txt"
  echo "Content" > "${TEST_DIR}/file:with\"chars.md"
  echo "Content" > "${TEST_DIR}/file?with*chars.log"
  echo "Content" > "${TEST_DIR}/file|with\\chars.conf"
  echo "Content" > "${TEST_DIR}/subdir1/sub<file>.txt"
  echo "Content" > "${TEST_DIR}/subdir1/subdir2/another>file.txt"
  echo "Content" > "${TEST_DIR}/subdir1/subdir2/subdir3/deep|file.txt"
}

teardown() {
  # Clean up test directory
  rm -rf "${TEST_DIR}"
}

# Test showing help with no parameters
@test "Show help when run without parameters" {
  run "$SCRIPT"
  
  assert_success
  assert_output --partial "FILE CHARACTER VALIDATOR"
  assert_output --partial "SYNTAX:"
  assert_output --partial "OPTIONS:"
}

# Test invalid option
@test "Show help with invalid option" {
  run "$SCRIPT" "-invalid"
  
  assert_success
  assert_output --partial "FILE CHARACTER VALIDATOR"
}

# Test the -us option with default values
@test "Run with -us option uses current directory and depth 1 by default" {
  cd "$TEST_DIR"
  run "$SCRIPT" "-us"
  
  assert_success
  assert_output --partial "Searching for files with unsupported Windows characters in: ."
  assert_output --partial "Search depth: 1"
}

# Test with non-existent directory
@test "Error when directory doesn't exist" {
  run "$SCRIPT" "-us" "/nonexistent/directory"
  
  assert_failure 1
  assert_output --partial "Error: Directory '/nonexistent/directory' does not exist."
}

# Test with invalid depth (too low)
@test "Error when depth is less than 1" {
  run "$SCRIPT" "-us" "0"
  
  assert_failure 2
  assert_output --partial "Error: Depth level must be between 1 and 6."
}

# Test with invalid depth (too high)
@test "Error when depth is greater than 6" {
  run "$SCRIPT" "-us" "7"
  
  assert_failure 2
  assert_output --partial "Error: Depth level must be between 1 and 6."
}

# Test with invalid depth type
@test "Error when depth is not a number" {
  run "$SCRIPT" "-us" "$TEST_DIR" "abc"
  
  assert_failure 2
  assert_output --partial "Error: Depth level must be a number between 1 and 6."
}

# Test with directory path followed by depth
@test "Accept directory path and depth" {
  run "$SCRIPT" "-us" "$TEST_DIR" "2"
  
  assert_success
  assert_output --partial "Searching for files with unsupported Windows characters in: $TEST_DIR"
  assert_output --partial "Search depth: 2"
}

# Test no unsupported files found
@test "Report when no unsupported files are found" {
  # Create a clean directory with no unsupported filenames
  CLEAN_DIR="${BATS_TMPDIR}/clean_dir"
  mkdir -p "$CLEAN_DIR"
  echo "Content" > "${CLEAN_DIR}/valid-file.txt"
  
  run "$SCRIPT" "-us" "$CLEAN_DIR"
  
  assert_success
  assert_output --partial "No files with unsupported Windows characters found."
  
  # Clean up
  rm -rf "$CLEAN_DIR"
}

# Test finding unsupported files at depth 1
@test "Find unsupported files at depth 1" {
  run "$SCRIPT" "-us" "$TEST_DIR" "1"
  
  assert_success
  assert_output --partial "${TEST_DIR}/file<with>unsupported.txt"
  assert_output --partial "${TEST_DIR}/file:with\"chars.md"
  assert_output --partial "${TEST_DIR}/file?with*chars.log"
  assert_output --partial "${TEST_DIR}/file|with\\chars.conf"
  
  # Should not find files at deeper levels
  refute_output --partial "${TEST_DIR}/subdir1/subdir2/another>file.txt"
  refute_output --partial "${TEST_DIR}/subdir1/subdir2/subdir3/deep|file.txt"
}

# Test finding unsupported files at depth 2
@test "Find unsupported files at depth 2" {
  run "$SCRIPT" "-us" "$TEST_DIR" "2"
  
  assert_success
  # Should find files at root and depth 1
  assert_output --partial "${TEST_DIR}/file<with>unsupported.txt"
  assert_output --partial "${TEST_DIR}/subdir1/sub<file>.txt"
  
  # Should not find files at deeper levels
  refute_output --partial "${TEST_DIR}/subdir1/subdir2/subdir3/deep|file.txt"
}

# Test finding all unsupported files at max depth
@test "Find all unsupported files at max depth" {
  run "$SCRIPT" "-us" "$TEST_DIR" "6"
  
  assert_success
  # Should find files at all levels
  assert_output --partial "${TEST_DIR}/file<with>unsupported.txt"
  assert_output --partial "${TEST_DIR}/subdir1/sub<file>.txt"
  assert_output --partial "${TEST_DIR}/subdir1/subdir2/another>file.txt"
  assert_output --partial "${TEST_DIR}/subdir1/subdir2/subdir3/deep|file.txt"
}

# Test check_unsupported_characters function directly
@test "check_unsupported_characters function identifies all problematic characters" {
  # Create test files with each problematic character
  CHARS_DIR="${BATS_TMPDIR}/chars_test"
  mkdir -p "$CHARS_DIR"
  
  # Create files with each problematic character
  touch "$CHARS_DIR/file<.txt"
  touch "$CHARS_DIR/file>.txt"
  touch "$CHARS_DIR/file:.txt"
  touch "$CHARS_DIR/file\".txt"
  touch "$CHARS_DIR/file\\.txt"
  touch "$CHARS_DIR/file|.txt"
  touch "$CHARS_DIR/file?.txt"
  touch "$CHARS_DIR/file*.txt"
  
  # Run the script on this directory
  run "$SCRIPT" "-us" "$CHARS_DIR"
  
  assert_success
  # Check that all problematic files are found
  assert_output --partial "$CHARS_DIR/file<.txt"
  assert_output --partial "$CHARS_DIR/file>.txt"
  assert_output --partial "$CHARS_DIR/file:.txt"
  assert_output --partial "$CHARS_DIR/file\".txt"
  assert_output --partial "$CHARS_DIR/file\\.txt"
  assert_output --partial "$CHARS_DIR/file|.txt"
  assert_output --partial "$CHARS_DIR/file?.txt"
  assert_output --partial "$CHARS_DIR/file*.txt"
  
  # Clean up
  rm -rf "$CHARS_DIR"
}

# Test with numeric directory name
@test "Correctly handle numeric directory name" {
  # Create a directory with a numeric name
  NUM_DIR="${BATS_TMPDIR}/123"
  mkdir -p "$NUM_DIR"
  touch "$NUM_DIR/valid.txt"
  touch "$NUM_DIR/in<valid>.txt"
  
  run "$SCRIPT" "-us" "$NUM_DIR"
  
  assert_success
  assert_output --partial "$NUM_DIR/in<valid>.txt"
  
  # Clean up
  rm -rf "$NUM_DIR"
}

# Test exit codes
@test "Script returns correct exit code for successful execution" {
  run "$SCRIPT" "-us" "$TEST_DIR"
  assert_success
}

@test "Ask to delete files with unsupported characters" {
  # Create a test directory with problematic files
  TEST_DELETE_DIR="${BATS_TMPDIR}/delete_test"
  mkdir -p "$TEST_DELETE_DIR"
  
  # Create some files with unsupported characters
  touch "$TEST_DELETE_DIR/file<1>.txt"
  touch "$TEST_DELETE_DIR/file>2.txt"
  touch "$TEST_DELETE_DIR/normal.txt"
  
  # First verify the files exist
  [ -f "$TEST_DELETE_DIR/file<1>.txt" ]
  [ -f "$TEST_DELETE_DIR/file>2.txt" ]
  [ -f "$TEST_DELETE_DIR/normal.txt" ]
  
  # Test with 'y' response to delete files (skip testing 'n' to simplify)
  echo "y" > "$BATS_TMPDIR/response.txt"
  run bash -c "cat \"$BATS_TMPDIR/response.txt\" | \"$SCRIPT\" \"-us\" \"$TEST_DELETE_DIR\""
  
  # Verify problematic files are deleted and normal file remains
  [ ! -f "$TEST_DELETE_DIR/file<1>.txt" ]
  [ ! -f "$TEST_DELETE_DIR/file>2.txt" ]
  [ -f "$TEST_DELETE_DIR/normal.txt" ]
  
  # Clean up
  rm -rf "$TEST_DELETE_DIR"
  rm -f "$BATS_TMPDIR/response.txt"
}


# Test performance with depth limit
@test "Depth limit effectively restricts the search scope" {
  # This is a more subjective test - we want to ensure the depth parameter works
  # Create a deep directory structure
  DEEP_DIR="${BATS_TMPDIR}/deep_test"
  mkdir -p "$DEEP_DIR/1/2/3/4/5/6"
  touch "$DEEP_DIR/normal.txt"
  touch "$DEEP_DIR/1/file<1>.txt"
  touch "$DEEP_DIR/1/2/file<2>.txt"
  touch "$DEEP_DIR/1/2/3/file<3>.txt"
  touch "$DEEP_DIR/1/2/3/4/file<4>.txt"
  touch "$DEEP_DIR/1/2/3/4/5/file<5>.txt"
  touch "$DEEP_DIR/1/2/3/4/5/6/file<6>.txt"
  
  # Test with depth 3
  run "$SCRIPT" "-us" "$DEEP_DIR" "4"
  
  assert_success
  # Should find files up to depth 3
  assert_output --partial "$DEEP_DIR/1/file<1>.txt"
  assert_output --partial "$DEEP_DIR/1/2/file<2>.txt"
  assert_output --partial "$DEEP_DIR/1/2/3/file<3>.txt"
  
  # Should not find deeper files
  refute_output --partial "$DEEP_DIR/1/2/3/4/file<4>.txt"
  refute_output --partial "$DEEP_DIR/1/2/3/4/5/file<5>.txt"
  
  # Clean up
  rm -rf "$DEEP_DIR"
}
