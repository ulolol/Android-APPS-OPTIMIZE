#!/bin/sh
# Script to list all user-installed apps and their compilation status
# Usage: sh list_app_compile_status.sh
# NOTE: This script is designed to run INSIDE the Android shell (via Shizuku/Termux)


echo "Needs to be run inside the SHIZUKU SHELL in Termux"
echo "Running this script might BREAK STORAGE ACCESS for OPTIMIZED APPS"
echo "You will need to REBOOT the device to get ACCESS working again"
echo "The Optimizations WILL PERSIST across reboots, so you dont have to worry"
echo "Fetching user-installed apps and compilation status..."
echo "========================================================"
echo ""

# Get list of user-installed packages (excluding system apps)
packages=$(pm list packages -3 | sed 's/package://')

if [ -z "$packages" ]; then
    echo "No user-installed apps found."
    exit 1
fi

# Temporary files (Android shell compatible paths)
temp_packages="/data/local/tmp/packages_$$.txt"
temp_dexopt="/data/local/tmp/dexopt_$$.txt"
temp_results="/data/local/tmp/results_$$.txt"

# Save packages to file
echo "$packages" > "$temp_packages"

# Get full dexopt output once
dumpsys package dexopt > "$temp_dexopt"

# Process each package
while read -r pkg; do
    # Use awk to find the package and extract status from next arm64/arm line
    status=$(awk -v pkg="$pkg" '
        $0 ~ "\\[" pkg "\\]" { found=1; next }
        found && /arm64:|arm:/ {
            match($0, /\[status=[^]]*\]/)
            if (RSTART > 0) {
                status = substr($0, RSTART+8, RLENGTH-9)
                print status
                exit
            }
        }
    ' "$temp_dexopt")
    
    # Default to unknown
    if [ -z "$status" ]; then
        status="unknown"
    fi
    
    echo "$pkg|$status" >> "$temp_results"
done < "$temp_packages"

# Display results
echo "Package Name                                    | Compilation Status"
echo "------------------------------------------------|-------------------"
sort "$temp_results" | while IFS='|' read -r package compile_status; do
    printf "%-47s | %s\n" "$package" "$compile_status"
done

# Count different statuses
everything_count=$(grep -c "|everything$" "$temp_results" 2>/dev/null || echo )
everything_profile_count=$(grep -c "|everything-profile$" "$temp_results" 2>/dev/null || echo )
speed_count=$(grep -c "|speed$" "$temp_results" 2>/dev/null || echo )
speed_profile_count=$(grep -c "|speed-profile" "$temp_results" 2>/dev/null || echo )
space_count=$(grep -c "|space$" "$temp_results" 2>/dev/null || echo )
space_profile_count=$(grep -c "|space-profile$" "$temp_results" 2>/dev/null || echo )
verify_count=$(grep -c "|verify" "$temp_results" 2>/dev/null || echo )
quicken_count=$(grep -c "|quicken" "$temp_results" 2>/dev/null || echo )
extract_count=$(grep -c "|extract" "$temp_results" 2>/dev/null || echo )
unknown_count=$(grep -c "|unknown" "$temp_results" 2>/dev/null || echo )

# Cleanup
rm -f "$temp_packages" "$temp_dexopt" "$temp_results"

echo ""
echo "========================================================"
echo "Summary:"
echo "  everything:    $everything_count apps (Fully AOT compiled - fastest)"
echo "  every-profile: $everything_profile_count apps (Profile guided - almost full AOT)"
echo "  speed:         $speed_count apps (Full speed optimization without profiles)"
echo "  speed-profile: $speed_profile_count apps (Profile-guided speed AOT)"
echo "  space:         $space_count apps (Space-efficient full-ish compile)"
echo "  space-profile: $space_profile_count apps (Profile-guided for storage efficiency)"
echo "  verify:        $verify_count apps (Verified only)"
echo "  quicken:       $quicken_count apps (DEX optimized)"
echo "  extract:       $extract_count apps (Minimal optimization)"
echo "  unknown:       $unknown_count apps (Status not available)"
echo ""
echo "Total user-installed apps: $(echo "$packages" | wc -l)"
