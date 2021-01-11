import subprocess

def raised(func, *args,**kwargs):
    res = False
    try:
        func(*args,**kwargs)
    except Exception as e:
        res = [type(e), f"{e}"]
        print(f"Raised {type(e)}: {e}")
    return res

def run(command, merge=False):
    if merge:
        res = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        stdout = res.stdout.decode().split('\n')
        if stdout[-1]=='':
            stdout = stdout[:-1]
        return res.returncode, stdout
    else:
        res = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout = res.stdout.decode().split('\n')
        if stdout[-1]=='':
            stdout = stdout[:-1]
        stderr = res.stderr.decode().split('\n')
        if stderr[-1]=='':
            stderr = stderr[:-1]
        return res.returncode, stdout, stderr

