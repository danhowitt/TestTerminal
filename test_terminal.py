import os, subprocess
import sublime, sublime_plugin, io

class TestTerminalCommand(sublime_plugin.WindowCommand):

  def run(self, **args):
    self.testall          = self.set_test_all(args)
    self.settings         = sublime.load_settings('TestTerminal.sublime-settings')
    self.terminal         = self.settings.get('terminal')
    self.devpath          = self.settings.get('devpath')
    self.filepath         = self.window.active_view().file_name()
    self.projectpath      = self.set_project_path()
    self.command          = self.set_command()

    if self.command == 'unknown':
      self.exit_with_alert()

    self.run_test();

  def run_test(self):
    applescript = self.terminal_script()
    if self.terminal == "iTerm":
      applescript = self.iterm_script()
    
    self.execute_cmd(applescript, self.command)
    self.activate('Sublime Text 2')

  def execute_cmd(self, applescript, command):
    cmd = applescript.replace("$cmd", command)
    cmd = cmd.replace("$dir", self.projectpath)
    cmd = "osascript -e '%s'" % cmd
    os.system(cmd)

  def set_command(self):
    if (self.testall):
       return self.settings.get('test_all_command');
    if 'specs.js' in self.filepath:
      return self.settings.get('test_file_command').replace('$file', self.filepath)
    elif '.js' in self.filepath:
      testPath = self.projectpath + '/test' + self.filepath[self.projectpath.__len__(): ]
      testPathSpec = testPath.replace('.js', '-specs.js');
      return self.settings.get('test_file_command').replace('$file', testPathSpec)
    else:
      return 'unknown'

  def set_test_all(self, args):
    return args.get('test-all') == 'true'

  def set_project_path(self):
    projectRoot = self.filepath[self.devpath.__len__():]
    return self.devpath + projectRoot[:projectRoot.find('/')]

  def exit_with_alert(self):
    sublime.error_message('Cannot find a valid -specs.js file.')

  def iterm_script(self):
    return """
      tell application "iTerm"
        tell current session of terminal 1
          write text "$dir"
          write text "$cmd"
        end tell
      end tell
    """

  def terminal_script(self):
    return """
      tell application "Terminal"
        tell window 1
          do script "$cmd" in selected tab
        end tell
      end tell
    """

  def activate(self, app):
    subprocess.Popen("""osascript -e 'tell app "{0}" to activate'""".format(app), shell=True)