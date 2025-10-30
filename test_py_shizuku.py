import pexpect

def run_shizuku_command(command):
    """
    Run command through Shizuku interactive shell
    """
    try:
        # Start shizuku
        child = pexpect.spawn('shizuku', encoding='utf-8', timeout=30)
        
        # Wait for the shell prompt
        child.expect(r'\$ ')
        
        # Send the command
        child.sendline(command)
        
        # Wait for the prompt again (command completed)
        child.expect(r'\$ ')
        
        # Get the output (everything before the prompt)
        output = child.before
        
        # Send exit to close properly
        child.sendline('exit')
        child.wait()
        
        # Clean up the output (remove the echoed command line)
        lines = output.split('\n')
        # Remove first line (the echoed command)
        if lines and command in lines[0]:
            lines = lines[1:]
        
        return '\n'.join(lines).strip()
        
    except pexpect.TIMEOUT:
        return "Command timed out"
    except Exception as e:
        return f"Error: {str(e)}"

# Install pexpect first: pkg install python-pexpect
print("Listing user-installed packages:")
output = run_shizuku_command("pm list packages -3")
print(output)

print("\n" + "="*50 + "\n")

print("Getting Android version:")
output = run_shizuku_command("getprop ro.build.version.release")
print(output)
