from jarvis.tools.fs_tool import FsTool
from jarvis.tools.shell_tool import ShellTool

# Test file system tool
fs_tool = FsTool()
print('Testing FS tool...')
result = fs_tool.run(action='list', path='.')
print('List result:', result.success, result.output[:100] if result.output else 'None')

# Test creating a file
print('\nTesting file creation...')
result = fs_tool.run(action='write', path='test_from_tool.txt', content='Hello from Jarvis FS tool!')
print('Write result:', result.success)
if not result.success:
    print('Error:', result.error)

# Test reading the file
print('\nTesting file read...')
result = fs_tool.run(action='read', path='test_from_tool.txt')
print('Read result:', result.success)
if result.success:
    print('Content:', result.output)
else:
    print('Error:', result.error)

# Test shell tool
print('\nTesting shell tool...')
shell_tool = ShellTool()
result = shell_tool.run(command='echo "Hello from shell tool"')
print('Shell result:', result.success)
if result.success:
    print('Output:', result.output.strip())
else:
    print('Error:', result.error)