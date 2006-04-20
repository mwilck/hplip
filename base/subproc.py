# -*- coding: utf-8 -*-
# subprocess - Subprocesses with accessible I/O streams
#
# For more information about this module, see PEP 324.
#
# Copyright (c) 2003-2004 by Peter Astrand <astrand@lysator.liu.se>
#
# By obtaining, using, and/or copying this software and/or its
# associated documentation, you agree that you have read, understood,
# and will comply with the following terms and conditions:
#
# Permission to use, copy, modify, and distribute this software and
# its associated documentation for any purpose and without fee is
# hereby granted, provided that the above copyright notice appears in
# all copies, and that both that copyright notice and this permission
# notice appear in supporting documentation, and that the name of the
# author not be used in advertising or publicity pertaining to
# distribution of the software without specific, written prior
# permission.
#
# THE AUTHOR DISCLAIMS ALL WARRANTIES WITH REGARD TO THIS SOFTWARE,
# INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS.
# IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL, INDIRECT OR
# CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS
# OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT,
# NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION
# WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

"""subprocess - Subprocesses with accessible I/O streams
This copy has been modified from the original in the Python std lib.
Its been edited to be Linux-only. Used for compatibility with Python < v2.4"""

import sys
import os
import types
import traceback
import select
import errno
import fcntl
import pickle

__all__ = ["Popen", "PIPE", "STDOUT", "call"]

try:
    MAXFD = os.sysconf("SC_OPEN_MAX")
except:
    MAXFD = 256

# True/False does not exist on 2.2.0
try:
    False
except NameError:
    False = 0
    True = 1

_active = []

def _cleanup():
    for inst in _active[:]:
        inst.poll()

PIPE = -1
STDOUT = -2


def call(*args, **kwargs):
    return Popen(*args, **kwargs).wait()

class Popen(object):
    def __init__(self, args, bufsize=0, executable=None,
                 stdin=None, stdout=None, stderr=None,
                 preexec_fn=None, close_fds=False, shell=False,
                 cwd=None, env=None, universal_newlines=False,
                 startupinfo=None, creationflags=0):
        """Create new Popen instance."""
        _cleanup()

        if not isinstance(bufsize, (int, long)):
            raise TypeError("bufsize must be an integer")

        if startupinfo is not None:
            raise ValueError("startupinfo is only supported on Windows "
                             "platforms")
        if creationflags != 0:
            raise ValueError("creationflags is only supported on Windows "
                             "platforms")

        self.stdin = None
        self.stdout = None
        self.stderr = None
        self.pid = None
        self.returncode = None
        self.universal_newlines = universal_newlines

        (p2cread, p2cwrite,
         c2pread, c2pwrite,
         errread, errwrite) = self._get_handles(stdin, stdout, stderr)

        self._execute_child(args, executable, preexec_fn, close_fds,
                            cwd, env, universal_newlines,
                            startupinfo, creationflags, shell,
                            p2cread, p2cwrite,
                            c2pread, c2pwrite,
                            errread, errwrite)

        if p2cwrite:
            self.stdin = os.fdopen(p2cwrite, 'wb', bufsize)
        if c2pread:
            if universal_newlines:
                self.stdout = os.fdopen(c2pread, 'rU', bufsize)
            else:
                self.stdout = os.fdopen(c2pread, 'rb', bufsize)
        if errread:
            if universal_newlines:
                self.stderr = os.fdopen(errread, 'rU', bufsize)
            else:
                self.stderr = os.fdopen(errread, 'rb', bufsize)

        _active.append(self)


    def _translate_newlines(self, data):
        data = data.replace("\r\n", "\n")
        data = data.replace("\r", "\n")
        return data

    def _get_handles(self, stdin, stdout, stderr):
        """Construct and return tupel with IO objects:
        p2cread, p2cwrite, c2pread, c2pwrite, errread, errwrite
        """
        p2cread, p2cwrite = None, None
        c2pread, c2pwrite = None, None
        errread, errwrite = None, None

        if stdin == None:
            pass
        elif stdin == PIPE:
            p2cread, p2cwrite = os.pipe()
        elif type(stdin) == types.IntType:
            p2cread = stdin
        else:
            # Assuming file-like object
            p2cread = stdin.fileno()

        if stdout == None:
            pass
        elif stdout == PIPE:
            c2pread, c2pwrite = os.pipe()
        elif type(stdout) == types.IntType:
            c2pwrite = stdout
        else:
            # Assuming file-like object
            c2pwrite = stdout.fileno()

        if stderr == None:
            pass
        elif stderr == PIPE:
            errread, errwrite = os.pipe()
        elif stderr == STDOUT:
            errwrite = c2pwrite
        elif type(stderr) == types.IntType:
            errwrite = stderr
        else:
            # Assuming file-like object
            errwrite = stderr.fileno()

        return (p2cread, p2cwrite,
                c2pread, c2pwrite,
                errread, errwrite)


    def _set_cloexec_flag(self, fd):
        try:
            cloexec_flag = fcntl.FD_CLOEXEC
        except AttributeError:
            cloexec_flag = 1

        old = fcntl.fcntl(fd, fcntl.F_GETFD)
        fcntl.fcntl(fd, fcntl.F_SETFD, old | cloexec_flag)


    def _close_fds(self, but):
        for i in range(3, MAXFD):
            if i == but:
                continue
            try:
                os.close(i)
            except:
                pass


    def _execute_child(self, args, executable, preexec_fn, close_fds,
                       cwd, env, universal_newlines,
                       startupinfo, creationflags, shell,
                       p2cread, p2cwrite,
                       c2pread, c2pwrite,
                       errread, errwrite):
        """Execute program (POSIX version)"""

        if isinstance(args, types.StringTypes):
            args = [args]

        if shell:
            args = ["/bin/sh", "-c"] + args

        if executable == None:
            executable = args[0]

        # For transferring possible exec failure from child to parent
        # The first char specifies the exception type: 0 means
        # OSError, 1 means some other error.
        errpipe_read, errpipe_write = os.pipe()
        self._set_cloexec_flag(errpipe_write)

        self.pid = os.fork()
        if self.pid == 0:
            # Child
            try:
                # Close parent's pipe ends
                if p2cwrite:
                    os.close(p2cwrite)
                if c2pread:
                    os.close(c2pread)
                if errread:
                    os.close(errread)
                os.close(errpipe_read)

                # Dup fds for child
                if p2cread:
                    os.dup2(p2cread, 0)
                if c2pwrite:
                    os.dup2(c2pwrite, 1)
                if errwrite:
                    os.dup2(errwrite, 2)

                # Close pipe fds.  Make sure we doesn't close the same
                # fd more than once.
                if p2cread:
                    os.close(p2cread)
                if c2pwrite and c2pwrite not in (p2cread,):
                    os.close(c2pwrite)
                if errwrite and errwrite not in (p2cread, c2pwrite):
                    os.close(errwrite)

                # Close all other fds, if asked for
                if close_fds:
                    self._close_fds(but=errpipe_write)

                if cwd != None:
                    os.chdir(cwd)

                if preexec_fn:
                    apply(preexec_fn)

                if env == None:
                    os.execvp(executable, args)
                else:
                    os.execvpe(executable, args, env)

            except:
                exc_type, exc_value, tb = sys.exc_info()
                # Save the traceback and attach it to the exception object
                exc_lines = traceback.format_exception(exc_type,
                                                       exc_value,
                                                       tb)
                exc_value.child_traceback = ''.join(exc_lines)
                os.write(errpipe_write, pickle.dumps(exc_value))

            # This exitcode won't be reported to applications, so it
            # really doesn't matter what we return.
            os._exit(255)

        # Parent
        os.close(errpipe_write)
        if p2cread and p2cwrite:
            os.close(p2cread)
        if c2pwrite and c2pread:
            os.close(c2pwrite)
        if errwrite and errread:
            os.close(errwrite)

        # Wait for exec to fail or succeed; possibly raising exception
        data = os.read(errpipe_read, 1048576) # Exceptions limited to 1 MB
        os.close(errpipe_read)
        if data != "":
            os.waitpid(self.pid, 0)
            child_exception = pickle.loads(data)
            raise child_exception


    def _handle_exitstatus(self, sts):
        if os.WIFSIGNALED(sts):
            self.returncode = -os.WTERMSIG(sts)
        elif os.WIFEXITED(sts):
            self.returncode = os.WEXITSTATUS(sts)
        else:
            # Should never happen
            raise RuntimeError("Unknown child exit status!")

        _active.remove(self)


    def poll(self):
        """Check if child process has terminated.  Returns returncode
        attribute."""
        if self.returncode == None:
            try:
                pid, sts = os.waitpid(self.pid, os.WNOHANG)
                if pid == self.pid:
                    self._handle_exitstatus(sts)
            except os.error:
                pass
        return self.returncode


    def wait(self):
        """Wait for child process to terminate.  Returns returncode
        attribute."""
        if self.returncode == None:
            pid, sts = os.waitpid(self.pid, 0)
            self._handle_exitstatus(sts)
        return self.returncode


    def communicate(self, input=None):
        read_set = []
        write_set = []
        stdout = None # Return
        stderr = None # Return

        if self.stdin:
            # Flush stdio buffer.  This might block, if the user has
            # been writing to .stdin in an uncontrolled fashion.
            self.stdin.flush()
            if input:
                write_set.append(self.stdin)
            else:
                self.stdin.close()
        if self.stdout:
            read_set.append(self.stdout)
            stdout = []
        if self.stderr:
            read_set.append(self.stderr)
            stderr = []

        while read_set or write_set:
            rlist, wlist, xlist = select.select(read_set, write_set, [])

            if self.stdin in wlist:
                # When select has indicated that the file is writable,
                # we can write up to PIPE_BUF bytes without risk
                # blocking.  POSIX defines PIPE_BUF >= 512
                bytes_written = os.write(self.stdin.fileno(), input[:512])
                input = input[bytes_written:]
                if not input:
                    self.stdin.close()
                    write_set.remove(self.stdin)

            if self.stdout in rlist:
                data = os.read(self.stdout.fileno(), 1024)
                if data == "":
                    self.stdout.close()
                    read_set.remove(self.stdout)
                stdout.append(data)

            if self.stderr in rlist:
                data = os.read(self.stderr.fileno(), 1024)
                if data == "":
                    self.stderr.close()
                    read_set.remove(self.stderr)
                stderr.append(data)

        # All data exchanged.  Translate lists into strings.
        if stdout != None:
            stdout = ''.join(stdout)
        if stderr != None:
            stderr = ''.join(stderr)

        # Translate newlines, if requested.  We cannot let the file
        # object do the translation: It is based on stdio, which is
        # impossible to combine with select (unless forcing no
        # buffering).
        if self.universal_newlines and hasattr(open, 'newlines'):
            if stdout:
                stdout = self._translate_newlines(stdout)
            if stderr:
                stderr = self._translate_newlines(stderr)

        self.wait()
        return (stdout, stderr)
