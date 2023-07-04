import subprocess
import typing
from functools import lru_cache


class ShellResult:

    def __init__(self, code, stdout: str, stderr: str):
        self.code = code
        self.stdout = stdout
        self.stderr = stderr


def _shell(cmd):
    try:
        p = subprocess.run(cmd, shell=True, capture_output=True)
        return ShellResult(p.returncode,
                           bytes.decode(p.stdout),
                           bytes.decode(p.stderr))
    except:
        return None


def shell(path, use_cache=True):
    def f(*args, **kw) -> typing.Union[ShellResult, None]:
        params = ''
        if args:
            params = ' '.join([str(arg) for arg in args])
        if kw:
            params = params + ' '.join(['%s=%s' % (str(key), str(value)) for key, value in kw.items()])

        cmd = '%s %s' % (path, params)

        if use_cache:
            return _shell(cmd)
        else:
            print('hello')
            try:
                p = subprocess.run(cmd, shell=True, capture_output=True)
                return ShellResult(p.returncode,
                                   bytes.decode(p.stdout),
                                   bytes.decode(p.stderr))
            except:
                return None

    return f


if __name__ == '__main__':
    for i in range(20):
        result = shell('ls')('.')
        print(result.stdout)
