#!/usr/bin/env python3
"""
Shizuku Android App Optimization TUI
Interactive tool to optimize Android apps using Shizuku from a Python script.
Uses Textual for a modern, interactive terminal UI with Flexoki theme.
"""

import pexpect
import sys
import re
from typing import List, Dict, Tuple, Optional, Set
from dataclasses import dataclass
from enum import Enum
from functools import lru_cache

try:
    from textual.app import ComposeResult, Screen
    from textual.containers import Container, Vertical, Horizontal, ScrollableContainer
    from textual.widgets import (
        Static, Input, Label, Button, Checkbox, DataTable,
        Footer, Header, ProgressBar, RichLog
    )
    from textual.binding import Binding
    from textual.message import Message
    from textual.events import Click
    from rich.console import Console
    from rich.text import Text as RichText
    from rich.panel import Panel
    from rich.table import Table
    import logging

    # Clear log file at startup to prevent bloat
    try:
        open('shizuku_optimizer.log', 'w').close()
    except:
        pass

    # Set up file logging
    logging.basicConfig(
        filename='shizuku_optimizer.log',
        level=logging.DEBUG,
        format='%(asctime)s - %(message)s'
    )
except ImportError:
    print("Error: Required packages not installed.")
    print("Install with: pip install textual rich pexpect")
    sys.exit(1)


# Flexoki Theme Colors
class FlexokiColors:
    """Flexoki theme color palette."""
    # Background & UI
    BG_DARK = "#1c1b19"
    BG_LIGHT = "#f2f0ed"
    SURFACE = "#ede0d8"

    # Text
    TEXT_PRIMARY = "#100f0f"
    TEXT_SECONDARY = "#6f6e69"

    # Accent colors (custom per status)
    STATUS_EVERYTHING = "#06b6d4"      # Light green/cyan
    STATUS_SPEED = "#0ea5e9"            # Cyan
    STATUS_SPACE = "#8b5cf6"            # Purple
    STATUS_VERIFY = "#6366f1"           # Indigo
    STATUS_UNKNOWN = "#ef4444"          # Red


class OptimizationStatus(Enum):
    """Enum for optimization statuses with color mapping."""
    EVERYTHING = ("everything", STATUS_EVERYTHING := "light_green")
    EVERYTHING_PROFILE = ("everything-profile", STATUS_EVERYTHING)
    SPEED = ("speed", STATUS_SPEED := "cyan")
    SPEED_PROFILE = ("speed-profile", STATUS_SPEED)
    SPACE = ("space", STATUS_SPACE := "magenta")
    SPACE_PROFILE = ("space-profile", STATUS_SPACE)
    VERIFY = ("verify", STATUS_VERIFY := "blue")
    QUICKEN = ("quicken", STATUS_VERIFY)
    EXTRACT = ("extract", "yellow")
    UNKNOWN = ("unknown", "red")

    def get_color(self) -> str:
        """Return the Textual color name for this status."""
        return self.value[1]

    def get_status_name(self) -> str:
        """Return the status name string."""
        return self.value[0]

    def get_group_name(self) -> str:
        """Return the group this status belongs to."""
        if self in (OptimizationStatus.EVERYTHING, OptimizationStatus.EVERYTHING_PROFILE):
            return "Fully Optimized"
        elif self in (OptimizationStatus.SPEED, OptimizationStatus.SPEED_PROFILE,
                     OptimizationStatus.SPACE, OptimizationStatus.SPACE_PROFILE):
            return "Partially Optimized"
        elif self in (OptimizationStatus.VERIFY, OptimizationStatus.QUICKEN):
            return "Minimally Optimized"
        else:
            return "Unknown Status"

    @classmethod
    def from_string(cls, status: str) -> 'OptimizationStatus':
        """Convert status string to enum."""
        status = status.lower().strip()
        for item in cls:
            if item.value[0] == status:
                return item
        return cls.UNKNOWN


@dataclass
class AppInfo:
    """Data class for app information."""
    package_name: str
    optimization_status: OptimizationStatus

    def __repr__(self) -> str:
        return f"{self.package_name} [{self.optimization_status.value[0]}]"


class ShizukuWrapper:
    """Wrapper class to handle Shizuku command execution via pexpect."""

    def __init__(self, timeout: int = 30):
        self.timeout = timeout
        self.child = None

    def connect(self) -> bool:
        """Initialize Shizuku connection."""
        try:
            self.child = pexpect.spawn('shizuku', encoding='utf-8', timeout=self.timeout)
            self.child.expect(r'\$ ', timeout=5)
            return True
        except Exception as e:
            print(f"Error connecting to Shizuku: {str(e)}")
            return False

    def execute_command(self, command: str) -> str:
        """Execute a command through Shizuku and return output."""
        if not self.child:
            return "Error: Not connected to Shizuku"

        try:
            self.child.sendline(command)
            self.child.expect(r'\$ ', timeout=self.timeout)
            output = self.child.before

            # Remove echoed command line
            lines = output.split('\n')
            if lines and command in lines[0]:
                lines = lines[1:]

            return '\n'.join(lines).strip()
        except pexpect.TIMEOUT:
            return "Command timed out"
        except Exception as e:
            return f"Error: {str(e)}"

    def close(self):
        """Close Shizuku connection."""
        if self.child:
            try:
                self.child.sendline('exit')
                self.child.wait()
            except:
                pass


class AppListItem(Static):
    """Clickable app item widget."""

    def __init__(self, app: AppInfo, is_selected: bool = False, parent_screen: 'AppSelectionScreen' = None):
        super().__init__()
        self.app = app
        self.is_selected = is_selected
        self.parent_screen = parent_screen

    def render(self) -> RichText:
        """Render the app item."""
        checkbox = "☑" if self.is_selected else "☐"
        status = self.app.optimization_status.get_status_name()
        color = self.app.optimization_status.get_color()

        text_str = f"  {checkbox} [{color}]{self.app.package_name:<40}[/] [{color}]{status}[/]"
        return RichText.from_markup(text_str)

    def on_click(self) -> None:
        """Handle click to toggle selection."""
        if self.parent_screen:
            if self.app.package_name in self.parent_screen.selected_packages:
                self.parent_screen.selected_packages.remove(self.app.package_name)
            else:
                self.parent_screen.selected_packages.add(self.app.package_name)
            self.is_selected = not self.is_selected
            self.refresh()


class AppSelectionScreen(Screen):
    """Screen for selecting apps to optimize with real-time filtering and grouping."""

    BINDINGS = [
        Binding("escape", "exit_no_selection()", "Back"),
        Binding("a", "select_all()", "Select All"),
        Binding("d", "deselect_all()", "Deselect All"),
        Binding("space", "toggle_row()", "Toggle", priority=True),
        Binding("enter", "confirm_selection()", "Confirm"),
        Binding("tab", "focus_table()", "Focus Table"),
    ]

    def __init__(self, apps: List[AppInfo]):
        super().__init__()
        self.apps = apps
        self.filtered_apps = apps
        self.selected_packages: Set[str] = set()
        self.search_query = ""
        self.row_to_app: Dict[int, str] = {}  # Map row index to package name
        self.row_keys: Dict[int, str] = {}  # Map row index to DataTable RowKey
        self.column_keys = []  # Store ColumnKey objects: [checkbox_col, name_col, status_col]

    def compose(self) -> ComposeResult:
        """Compose the screen layout."""
        yield Header(show_clock=False)
        yield Label("[bold]Select Apps to Optimize[/bold]")
        yield Label("[dim]Space=Toggle • A=Select All • D=Deselect All • Search to filter[/dim]")
        yield Input(id="search_input", placeholder="Search apps...", classes="search-box")
        yield DataTable(id="apps_table", classes="app-list-container")
        yield Horizontal(
            Button("Confirm Selection", id="confirm_btn", variant="primary"),
            Button("Cancel", id="cancel_btn"),
            id="button_row"
        )
        yield Footer()

    def on_mount(self) -> None:
        """Initialize the screen."""
        table = self.query_one("#apps_table", DataTable)
        # Store column keys returned by add_columns
        self.column_keys = table.add_columns("", "Package Name", "Status")
        logging.debug(f"Column keys: {self.column_keys}")
        table.cursor_type = "row"  # Enable row cursor
        self.update_apps_display()
        logging.debug(f"AppSelectionScreen mounted. Total apps: {len(self.apps)}")
        self.query_one("#search_input", Input).focus()

    def on_input_changed(self, event: Input.Changed) -> None:
        """Handle search input changes."""
        self.search_query = event.value.lower()
        self.filter_apps()
        self.update_apps_display()

    def filter_apps(self) -> None:
        """Filter apps based on search query."""
        if not self.search_query:
            self.filtered_apps = self.apps
        else:
            self.filtered_apps = [
                app for app in self.apps
                if self.search_query in app.package_name.lower()
                or self.search_query in app.optimization_status.get_status_name()
            ]

    def update_apps_display(self) -> None:
        """Update the apps list display grouped by status."""
        table = self.query_one("#apps_table", DataTable)
        table.clear()
        self.row_to_app = {}
        self.row_keys = {}

        # Group apps by optimization status
        grouped: Dict[str, List[AppInfo]] = {}
        for app in self.filtered_apps:
            group = app.optimization_status.get_group_name()
            if group not in grouped:
                grouped[group] = []
            grouped[group].append(app)

        # Sort groups and apps within groups
        group_order = ["Fully Optimized", "Partially Optimized", "Minimally Optimized", "Unknown Status"]

        if not self.filtered_apps:
            table.add_row("[dim]No apps found[/dim]", "", "")
            logging.debug("No filtered apps to display")
            return

        # Add grouped content
        row_idx = 0
        for group in group_order:
            if group not in grouped:
                continue

            # Add group header (not selectable)
            row_key = table.add_row(f"[bold cyan]{group}[/bold cyan]", "", "")
            self.row_keys[row_idx] = row_key
            logging.debug(f"Added header row {row_idx} for group: {group}")
            row_idx += 1

            apps_in_group = sorted(grouped[group], key=lambda x: x.package_name)
            for app in apps_in_group:
                checkbox = "☑" if app.package_name in self.selected_packages else "☐"
                status = app.optimization_status.get_status_name()
                color = app.optimization_status.get_color()

                row_key = table.add_row(
                    checkbox,
                    app.package_name,
                    f"[{color}]{status}[/]"
                )
                # Store mapping from row index to package name and row key
                self.row_to_app[row_idx] = app.package_name
                self.row_keys[row_idx] = row_key
                logging.debug(f"Mapped row {row_idx} -> {app.package_name} (key: {row_key})")
                row_idx += 1

        logging.debug(f"Total rows added: {row_idx}, row_to_app mapping has {len(self.row_to_app)} entries, row_keys has {len(self.row_keys)} entries")

    def action_select_all(self) -> None:
        """Select all apps in filtered list."""
        for app in self.filtered_apps:
            self.selected_packages.add(app.package_name)
        self.update_apps_display()

    def action_deselect_all(self) -> None:
        """Deselect all apps."""
        self.selected_packages.clear()
        self.update_apps_display()

    def on_key(self, event) -> None:
        """Log all key presses for debugging."""
        logging.debug(f"Key pressed: {event.key}")

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        """Handle row selection (clicking on row)."""
        logging.debug(f"Row selected event: row_key={event.row_key}, cursor_row={event.cursor_row}")
        self.toggle_row_by_index(event.cursor_row)

    def toggle_row_by_index(self, row_idx: int) -> None:
        """Toggle selection for a specific row index."""
        table = self.query_one("#apps_table", DataTable)
        try:
            logging.debug(f"Toggling row {row_idx}")
            logging.debug(f"row_to_app mapping: {self.row_to_app}")
            logging.debug(f"row_keys mapping: {self.row_keys}")

            # Check if this row corresponds to an app (not a header)
            if row_idx in self.row_to_app and row_idx in self.row_keys:
                package_name = self.row_to_app[row_idx]
                row_key = self.row_keys[row_idx]
                logging.debug(f"Found package: {package_name}, row_key: {row_key}")

                # Toggle selection
                if package_name in self.selected_packages:
                    self.selected_packages.remove(package_name)
                    logging.debug(f"Deselected {package_name}")
                else:
                    self.selected_packages.add(package_name)
                    logging.debug(f"Selected {package_name}")

                # Update just this row's checkbox using the row_key and column_key
                checkbox = "☑" if package_name in self.selected_packages else "☐"
                table.update_cell(row_key, self.column_keys[0], checkbox)
                logging.debug(f"Updated checkbox to {checkbox} at row_key={row_key}, col_key={self.column_keys[0]}")
            else:
                logging.debug(f"Row {row_idx} is not an app row (likely header)")

        except Exception as e:
            import traceback
            logging.error(f"Toggle error: {e}")
            logging.error(traceback.format_exc())

    def action_toggle_row(self) -> None:
        """Toggle selection of current row (spacebar)."""
        table = self.query_one("#apps_table", DataTable)
        cursor_row = table.cursor_row
        logging.debug(f"action_toggle_row called, cursor at {cursor_row}")
        self.toggle_row_by_index(cursor_row)

    def action_focus_table(self) -> None:
        """Focus the table widget."""
        logging.debug("Focusing table")
        table = self.query_one("#apps_table", DataTable)
        table.focus()

    def action_exit_no_selection(self) -> None:
        """Exit without selection."""
        self.app.exit()

    def action_confirm_selection(self) -> None:
        """Confirm selection and move to profile screen."""
        logging.debug(f"Confirm called. Selected packages: {len(self.selected_packages)}")
        if not self.selected_packages:
            logging.debug("No packages selected, returning")
            return
        selected_apps = [app for app in self.apps if app.package_name in self.selected_packages]
        logging.debug(f"Selected {len(selected_apps)} apps: {[a.package_name for a in selected_apps]}")
        self.app.selected_apps = selected_apps
        # Push profile selection screen
        logging.debug("Pushing ProfileSelectionScreen")
        self.app.push_screen(ProfileSelectionScreen())

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press."""
        if event.button.id == "confirm_btn":
            self.action_confirm_selection()
        elif event.button.id == "cancel_btn":
            self.app.exit()


class ProfileItem(Static):
    """Clickable profile item widget."""

    def __init__(self, profile: str, description: str, parent_screen: 'ProfileSelectionScreen'):
        super().__init__()
        self.profile = profile
        self.description = description
        self.parent_screen = parent_screen

    def render(self) -> RichText:
        """Render the profile item."""
        marker = "→" if self.parent_screen.selected_profile == self.profile else " "
        text_str = f"{marker} [cyan]●[/cyan] [bold]{self.profile:<20}[/bold] - {self.description}"
        return RichText.from_markup(text_str)

    def on_click(self) -> None:
        """Handle click to select profile."""
        self.parent_screen.selected_profile = self.profile
        self.refresh()
        self.parent_screen.update_profiles_display()


class ProfileSelectionScreen(Screen):
    """Screen for selecting optimization profile."""

    BINDINGS = [
        Binding("escape", "back()", "Back"),
        Binding("space", "select_profile()", "Select", priority=True),
        Binding("enter", "confirm_profile()", "Confirm"),
    ]

    PROFILES = [
        ("everything", "Fully AOT compiled - fastest"),
        ("everything-profile", "Profile guided - almost full AOT"),
        ("speed", "Full speed optimization without profiles"),
        ("speed-profile", "Profile-guided speed AOT"),
        ("space", "Space-efficient full-ish compile"),
        ("space-profile", "Profile-guided for storage efficiency"),
        ("verify", "Verified only"),
        ("quicken", "DEX optimized"),
    ]

    def __init__(self):
        super().__init__()
        self.selected_profile: Optional[str] = None
        self.row_to_profile: Dict[int, str] = {}  # Map row index to profile name
        self.row_keys: Dict[int, str] = {}  # Map row index to DataTable RowKey
        self.column_keys = []  # Store ColumnKey objects: [marker_col, profile_col, desc_col]

    def compose(self) -> ComposeResult:
        """Compose the screen layout."""
        yield Header(show_clock=False)
        yield Label("[bold]Select Optimization Profile[/bold]")
        yield Label("[dim]Space=Select • Confirm to proceed[/dim]")
        yield DataTable(id="profiles_table", classes="profiles-container")
        yield Horizontal(
            Button("Confirm", id="confirm_profile_btn", variant="primary"),
            Button("Back", id="back_profile_btn"),
            id="profile_buttons"
        )
        yield Footer()

    def on_mount(self) -> None:
        """Initialize the screen."""
        table = self.query_one("#profiles_table", DataTable)
        # Store column keys returned by add_columns
        self.column_keys = table.add_columns("", "Profile", "Description")
        logging.debug(f"Profile column keys: {self.column_keys}")
        self.update_profiles_display()

    def update_profiles_display(self) -> None:
        """Update profiles display."""
        table = self.query_one("#profiles_table", DataTable)
        table.clear()
        self.row_to_profile = {}
        self.row_keys = {}

        for idx, (profile, description) in enumerate(self.PROFILES):
            marker = "→" if self.selected_profile == profile else " "
            row_key = table.add_row(
                marker,
                f"[cyan]{profile}[/cyan]",
                description
            )
            self.row_to_profile[idx] = profile
            self.row_keys[idx] = row_key
            logging.debug(f"Profile row {idx}: {profile}, row_key: {row_key}")

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        """Handle row selection (clicking on row)."""
        logging.debug(f"Profile row selected: {event.cursor_row}")
        self.select_profile_by_index(event.cursor_row)

    def select_profile_by_index(self, row_idx: int) -> None:
        """Select profile at specific row index."""
        table = self.query_one("#profiles_table", DataTable)
        try:
            logging.debug(f"Selecting profile at row {row_idx}")
            logging.debug(f"row_to_profile mapping: {self.row_to_profile}")
            logging.debug(f"row_keys mapping: {self.row_keys}")

            # Check if this row corresponds to a profile
            if row_idx in self.row_to_profile and row_idx in self.row_keys:
                profile = self.row_to_profile[row_idx]
                row_key = self.row_keys[row_idx]
                logging.debug(f"Selected profile: {profile}, row_key: {row_key}")

                # Clear previous selection marker
                if self.selected_profile and self.selected_profile != profile:
                    for idx, prof in self.row_to_profile.items():
                        if prof == self.selected_profile and idx in self.row_keys:
                            prev_row_key = self.row_keys[idx]
                            table.update_cell(prev_row_key, self.column_keys[0], " ")
                            logging.debug(f"Cleared marker from previous profile at row {idx}")
                            break

                # Set new selection
                self.selected_profile = profile
                table.update_cell(row_key, self.column_keys[0], "→")
                logging.debug(f"Updated marker to arrow at row_key={row_key}")

        except Exception as e:
            import traceback
            logging.error(f"Select profile error: {e}")
            logging.error(traceback.format_exc())

    def action_select_profile(self) -> None:
        """Select profile from current row (spacebar)."""
        table = self.query_one("#profiles_table", DataTable)
        cursor_row = table.cursor_row
        logging.debug(f"action_select_profile called, cursor at {cursor_row}")
        self.select_profile_by_index(cursor_row)

    def action_back(self) -> None:
        """Go back to app selection."""
        self.app.pop_screen()

    def action_confirm_profile(self) -> None:
        """Confirm profile selection and start optimization."""
        logging.debug(f"Confirm profile called. Selected: {self.selected_profile}")
        if not self.selected_profile:
            logging.debug("No profile selected, returning")
            return
        logging.debug(f"Apps to optimize: {len(self.app.selected_apps)}")
        # Move to optimization screen
        logging.debug("Pushing OptimizationProgressScreen")
        self.app.push_screen(
            OptimizationProgressScreen(
                self.app.selected_apps,
                self.selected_profile,
                self.app.shizuku
            )
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press."""
        if event.button.id == "confirm_profile_btn":
            self.action_confirm_profile()
        elif event.button.id == "back_profile_btn":
            self.app.pop_screen()


class OptimizationProgressScreen(Screen):
    """Screen showing optimization progress."""

    def __init__(self, apps: List[AppInfo], profile: str, shizuku: ShizukuWrapper):
        super().__init__()
        self.apps = apps
        self.profile = profile
        self.shizuku = shizuku
        self.success_count = 0
        self.failed_count = 0
        self.current_app_idx = 0

    def compose(self) -> ComposeResult:
        """Compose the screen layout."""
        yield Header(show_clock=False)
        yield Label(f"[bold]Optimizing {len(self.apps)} Apps with Profile: {self.profile}[/bold]")

        # Show selected apps and profile summary
        apps_list = "\n".join([f"  • {app.package_name}" for app in self.apps])
        summary = f"""[bold cyan]Selected Apps ({len(self.apps)}):[/bold cyan]
{apps_list}

[bold cyan]Profile:[/bold cyan] [yellow]{self.profile}[/yellow]
"""
        yield Static(summary, id="optimization_summary")

        yield Label(id="status_label", classes="status-label")
        yield ProgressBar(total=len(self.apps), id="progress")
        yield ScrollableContainer(
            RichLog(id="optimization_log", classes="optimization-log"),
            id="log_scroll"
        )
        yield Footer()

    def on_mount(self) -> None:
        """Start optimization process."""
        logging.debug(f"OptimizationProgressScreen mounted. Apps: {len(self.apps)}, Profile: {self.profile}")
        self.update_status("Starting optimization...")
        self.call_later(self.optimize)

    def update_status(self, message: str) -> None:
        """Update status label."""
        try:
            status = self.query_one("#status_label", Label)
            status.update(f"[cyan]{message}[/cyan]")
        except:
            pass

    def optimize(self) -> None:
        """Run optimization process."""
        logging.debug("optimize() called")
        log = self.query_one("#optimization_log", RichLog)
        progress = self.query_one("#progress", ProgressBar)

        for idx, app in enumerate(self.apps):
            logging.debug(f"Optimizing {idx+1}/{len(self.apps)}: {app.package_name}")
            self.update_status(f"Processing {idx+1}/{len(self.apps)}: {app.package_name}")
            log.write(f"[cyan][{idx+1}/{len(self.apps)}][/cyan] Optimizing {app.package_name}...")

            command = f'cmd package compile -m "{self.profile}" -f "{app.package_name}"'
            logging.debug(f"Executing: {command}")
            result = self.shizuku.execute_command(command)
            logging.debug(f"Result: {result[:200]}...")

            if "Error" not in result and "error" not in result.lower():
                log.write("[green]✓ Done[/green]")
                self.success_count += 1
            else:
                log.write("[red]✗ Failed[/red]")
                self.failed_count += 1

            progress.update(advance=1)

        # Move to summary screen
        logging.debug(f"Optimization complete. Success: {self.success_count}, Failed: {self.failed_count}")
        self.update_status("Optimization complete! Loading results...")
        self.call_later(self.show_summary)

    def show_summary(self) -> None:
        """Show the summary screen after a brief delay."""
        self.app.pop_screen()
        self.app.push_screen(
            SummaryScreen(self.success_count, self.failed_count, self.shizuku, self.app)
        )


class SummaryScreen(Screen):
    """Screen showing optimization summary and options."""

    def __init__(self, success_count: int, failed_count: int, shizuku: ShizukuWrapper, app: 'OptimizerApp'):
        super().__init__()
        self.success_count = success_count
        self.failed_count = failed_count
        self.shizuku = shizuku
        self.parent_app = app

    def compose(self) -> ComposeResult:
        """Compose the screen layout."""
        yield Header(show_clock=False)
        yield Label("[bold]Optimization Complete[/bold]")
        yield ScrollableContainer(
            Static(id="summary_content"),
            id="summary_scroll"
        )
        yield Horizontal(
            Button("Optimize More", id="continue_btn", variant="primary"),
            Button("Reboot Device", id="reboot_btn", variant="warning"),
            Button("Exit", id="exit_btn"),
            id="action_buttons"
        )
        yield Footer()

    def on_mount(self) -> None:
        """Initialize the screen."""
        self.update_summary()

    def update_summary(self) -> None:
        """Update summary display."""
        summary = self.query_one("#summary_content", Static)
        content = f"""
[bold green]✓ Successfully optimized: {self.success_count} app(s)[/bold green]
"""
        if self.failed_count > 0:
            content += f"[bold red]✗ Failed to optimize: {self.failed_count} app(s)[/bold red]\n"

        content += """
[bold yellow]⚠️  IMPORTANT NOTICE[/bold yellow]

[yellow]The device needs to be REBOOTED to fix the scoped storage
permissions for the optimized apps.[/yellow]

[cyan]Without rebooting, the apps may have broken storage access.[/cyan]

[yellow]The optimizations will persist across reboots.[/yellow]
"""
        summary.update(content)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press."""
        if event.button.id == "continue_btn":
            # Reset and go back to app selection
            self.parent_app.pop_screen()
            self.parent_app.fetch_apps_and_show_selection()
        elif event.button.id == "reboot_btn":
            self.shizuku.execute_command("reboot")
            self.parent_app.exit()
        elif event.button.id == "exit_btn":
            self.parent_app.exit()


class ShizukuOptimizerApp:
    """Main Textual application for Shizuku app optimizer."""

    CSS = """
    Screen {
        background: $panel;
        color: $text;
    }

    #apps_table {
        height: 20;
        border: solid $accent;
        background: $boost;
    }

    #profiles_table {
        height: 12;
        border: solid $accent;
        background: $boost;
    }

    #optimization_summary {
        height: auto;
        border: solid $accent;
        background: $boost;
        padding: 1 2;
        margin-bottom: 1;
    }

    #summary_content {
        height: 1fr;
        padding: 1 2;
        border: solid $accent;
        background: $boost;
    }

    #optimization_log {
        height: 1fr;
        border: solid $accent;
        background: $boost;
    }

    #search_input {
        margin: 1 0;
        height: 3;
    }

    #progress {
        margin: 1 0;
    }

    #status_label {
        margin: 1 0;
        height: 1;
    }

    #button_row, #profile_buttons, #action_buttons {
        height: auto;
        margin: 1 0;
    }

    Button {
        margin: 0 1;
    }

    Label {
        margin: 1 0;
    }
    """

    def __init__(self):
        self.shizuku = ShizukuWrapper()
        self.apps: List[AppInfo] = []
        self.selected_apps: List[AppInfo] = []

    def run(self) -> None:
        """Run the main application."""
        from textual.app import App

        optimizer = self

        class OptimizerApp(App):
            CSS = ShizukuOptimizerApp.CSS
            TITLE = "Shizuku App Optimizer"

            def __init__(self):
                super().__init__()
                self.optimizer = optimizer
                self.selected_apps: List[AppInfo] = []
                self.shizuku = optimizer.shizuku

            def on_mount(self) -> None:
                """Initialize application."""
                # Set Flexoki theme
                self.theme = "flexoki"

                # Connect to Shizuku
                if not self.shizuku.connect():
                    self.title = "Failed to connect to Shizuku"
                    self.call_later(self.exit)
                    return

                # Fetch apps
                self.fetch_apps_and_show_selection()

            def fetch_apps_and_show_selection(self) -> None:
                """Fetch apps and show selection screen."""
                # Get list of user-installed packages
                packages_output = self.shizuku.execute_command(
                    "pm list packages -3 | sed 's/package://'"
                )

                if not packages_output or "Error" in packages_output:
                    self.title = "Error fetching packages"
                    return

                packages = [pkg.strip() for pkg in packages_output.split('\n') if pkg.strip()]

                # Get dexopt status for all apps
                dexopt_output = self.shizuku.execute_command("dumpsys package dexopt")
                if not dexopt_output or "Error" in dexopt_output:
                    dexopt_output = ""

                # Parse and create AppInfo objects
                self.optimizer.apps = []
                for package in packages:
                    status = self._parse_optimization_status(package, dexopt_output)
                    self.optimizer.apps.append(AppInfo(package, status))

                # Sort by status and name
                self.optimizer.apps.sort(
                    key=lambda x: (x.optimization_status.value[0], x.package_name)
                )

                # Show app selection screen
                self.push_screen(AppSelectionScreen(self.optimizer.apps))

            def _parse_optimization_status(self, package: str, dexopt_output: str) -> OptimizationStatus:
                """Parse optimization status from dexopt output."""
                try:
                    pattern = rf'\[{re.escape(package)}\].*?(?:arm64:|arm:).*?\[status=([^\]]+)\]'
                    match = re.search(pattern, dexopt_output, re.DOTALL)
                    if match:
                        status = match.group(1).lower().strip()
                        return OptimizationStatus.from_string(status)
                except:
                    pass
                return OptimizationStatus.UNKNOWN

        app = OptimizerApp()
        app.run()


def main():
    """Entry point."""
    optimizer = ShizukuOptimizerApp()
    optimizer.run()


if __name__ == "__main__":
    main()
