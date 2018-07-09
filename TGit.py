import sublime
import sublime_plugin
import os
import os.path
import subprocess

class TGitCommand(sublime_plugin.WindowCommand):
    def run(self, cmd, paths = None, isHung = False):
        dir = self.getPath(paths)

        if not dir:
            return
            
        settings = sublime.load_settings('TGit.sublime-settings')
        TGitProc_path = settings.get('TGitProc_path')

        if not os.path.isfile(TGitProc_path):
            sublime.error_message(''.join(['can\'t find TortoiseGitProc.exe,',
                ' please config setting file', '\n   --sublime-TGit']))
            raise

        proce = subprocess.Popen('"%s" /command:%s /path:"%s"' % (TGitProc_path, cmd, dir), stdout = subprocess.PIPE)

        # This is required, cause of ST must wait TortoiseSVN update then revert
        # the file. Otherwise the file reverting occur before SVN update, if the
        # file changed the file content in ST is older.
        if isHung:
            proce.communicate()

    def getPath(self, paths):
        path = None
        if paths:
            path = '*'.join(paths)
        else:
            view = sublime.active_window().active_view()
            path = view.file_name() if view else None

        return path

class MutatingTGitCommand(TGitCommand):
    def run(self, cmd, paths = None):
        TGitCommand.run(self, cmd, paths, True)
        
        self.view = sublime.active_window().active_view()
        (row,col) = self.view.rowcol(self.view.sel()[0].begin())
        self.lastLine = str(row + 1)
        sublime.set_timeout(self.revert, 100)

    def revert(self):
        self.view.run_command('revert')
        sublime.set_timeout(self.revertPoint, 600)

    def revertPoint(self):
        self.view.window().run_command('goto_line', {'line': self.lastLine})

# class TGitUpdateCommand(MutatingTGitCommand):
#     def run(self, paths = None):
#         settings = sublime.load_settings('TGit.sublime-settings')
#         closeonend = '3' if True == settings.get('autoCloseUpdateDialog') else '0'
#         MutatingTGitCommand.run(self, 'update /closeonend:'+closeonend, paths)

class TGitSyncCommand(TGitCommand):
    def run(self, paths = None):
        TGitCommand.run(self, 'sync', paths)

class TGitPullCommand(MutatingTGitCommand):
    def run(self, paths = None):
        MutatingTGitCommand.run(self, 'pull', paths)

class TGitPushCommand(MutatingTGitCommand):
    def run(self, paths = None):
        MutatingTGitCommand.run(self, 'push', paths)

class TGitCommitCommand(TGitCommand):
    def run(self, paths = None):
        TGitCommand.run(self, 'commit', paths)

class TGitRevertCommand(MutatingTGitCommand):
    def run(self, paths = None):
        MutatingTGitCommand.run(self, 'revert', paths)

class TGitBlameCommand(TGitCommand):
    def run(self, paths = None):
        TGitCommand.run(self, 'blame', paths)

class TGitLogCommand(TGitCommand):
    def run(self, paths = None):
        TGitCommand.run(self, 'log', paths)

class TGitDiffCommand(TGitCommand):
    def run(self, paths = None):
        TGitCommand.run(self, 'diff', paths)
