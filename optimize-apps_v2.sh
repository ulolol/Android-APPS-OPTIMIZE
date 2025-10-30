#!/bin/sh

# Script: List user-installed apps, allow selection, and optimize using cmd package compile.
# Designed for Shizuku in Termux, compatible with sh, no ADB required.
# Enhancements: support verbose output for the optimization process (enabled with -v/--verbose).

# Parse optional verbose flag (first argument)
VERBOSE=1
if [ "$1" = "-v" ] || [ "$1" = "--verbose" ]; then
    VERBOSE=1
    shift
fi

verbose_log() {
    if [ "$VERBOSE" -eq 1 ]; then
        printf "%s\n" "$1"
    fi
}

# Check if pm command is available
if ! command -v pm >/dev/null 2>&1; then
    echo "Package manager (pm) not found. Ensure Shizuku is running and Termux is authorized."
    exit 1
fi

# Fetch list of user-installed packages (third-party apps)
# Output: one package per line, e.g., com.example.app
packages=$(pm list packages -3 | sed 's/package://g' | tr -d '\r')

# Validate result
if [ -z "$packages" ]; then
    echo "No user-installed apps found or error accessing package list."
    exit 1
fi

# Build a list of packages as positional parameters for easier processing
set -- $packages
total_apps=$#
if [ "$total_apps" -eq 0 ]; then
    echo "No apps found in the list."
    exit 1
fi

echo ""
echo "User-installed apps:"

# Print numbered list
i=1
for pkg in "$@"; do
    echo "  $i: $pkg"
    i=$((i + 1))
done

# Available optimization profiles
profiles="everything everything-profile speed speed-profile space space-profile verify quicken"

echo ""
echo "Enter the number of the app to optimize, or 'all' to optimize all user apps:"
read selection

if [ "$selection" = "all" ]; then
    # Choose a profile for all apps
    echo "Select optimization profile ($profiles):"
    read profile
    # Validate profile
    case " $profiles " in
        *" $profile "*) ;;
        *) echo "Invalid profile. Available: $profiles"; exit 1 ;;
    esac
    echo "Optimizing all user apps with profile '$profile'..."
    for pkg in "$@"; do
        echo "Optimizing $pkg..."
        # Verbose path: show command, duration, and results
        start=$(date +%s)
        if [ "$VERBOSE" -eq 1 ]; then
            verbose_log "Running: cmd package compile -m \"$profile\" -f \"$pkg\""
            if cmd package compile -m "$profile" -f "$pkg"; then
                end=$(date +%s)
                duration=$((end - start))
                verbose_log "OK: $pkg (duration ${duration}s)"
            else
                end=$(date +%s)
                duration=$((end - start))
                verbose_log "ERROR: $pkg (duration ${duration}s)"
            fi
        else
            if cmd package compile -m "$profile" -f "$pkg" >/dev/null 2>&1; then
                end=$(date +%s)
                duration=$((end - start))
                printf "Optimized %s with profile '%s' (duration %ss).\n" "$pkg" "$profile" "$duration"
            else
                end=$(date +%s)
                duration=$((end - start))
                printf "Failed to optimize %s (duration %ss).\n" "$pkg" "$duration"
            fi
        fi
    done
    echo "Optimization complete for all user apps."
    exit 0
fi

# Non-all path: ensure numeric selection and within range
# Strip whitespace
selection=$(echo "$selection" | tr -d '[:space:]')

# Validate numeric
if ! printf "%s" "$selection" | grep -qE '^[0-9]+$' || [ "$selection" -lt 1 ] || [ "$selection" -gt "$total_apps" ]; then
    echo "Error: Please enter a number between 1 and $total_apps"
    exit 1
fi

# Get the selected app (nth item from the list)
selected_app=$(printf "%s\n" "$@" | sed -n "${selection}p")
if [ -z "$selected_app" ]; then
    echo "Error: Could not determine the selected app."
    exit 1
fi

echo "Selected app: $selected_app"
echo "Select optimization profile ($profiles):"
read profile
case " $profiles " in
    *" $profile "*) ;;
    *) echo "Invalid profile. Available: $profiles"; exit 1 ;;
esac

echo "Optimizing $selected_app with profile '$profile'..."
start=$(date +%s)
if [ "$VERBOSE" -eq 1 ]; then
    verbose_log "Running: cmd package compile -m \"$profile\" -f \"$selected_app\""
    if cmd package compile -m "$profile" -f "$selected_app"; then
        end=$(date +%s)
        duration=$((end - start))
        verbose_log "OK: $selected_app (duration ${duration}s)"
    else
        end=$(date +%s)
        duration=$((end - start))
        verbose_log "ERROR: $selected_app (duration ${duration}s)"
    fi
else
    if cmd package compile -m "$profile" -f "$selected_app" >/dev/null 2>&1; then
        end=$(date +%s)
        duration=$((end - start))
        printf "Optimized %s with profile '%s' (duration %ss).\n" "$selected_app" "$profile" "$duration"
    else
        end=$(date +%s)
        duration=$((end - start))
        printf "Failed to optimize %s (duration %ss).\n" "$selected_app" "$duration"
    fi
fi
echo "Optimization complete."
