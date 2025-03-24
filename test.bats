#!/usr/bin/env bats

# Load the script to test
setup() {
  # Source your script or create path to executable
  source "./script.sh"
  # Or for executables:
  # PATH="$PWD:$PATH"
}

@test "Testing addition function" {
  # Call function from your script
  result=$(add 2 3)
  # Check the result
  [ "$result" -eq 5 ]
}

@test "Script prints correct output" {
  # Run your script and capture output
  run ./script.sh
  # Check exit status
  [ "$status" -eq 0 ]
  # Check output
  [ "${lines[0]}" = "Expected output" ]
}
