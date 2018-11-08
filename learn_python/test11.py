import time
def echoRuntime(func):
    def wrapper(*args, **kwargs):
        startTime = time.time()
        result = func(*args, **kwargs)
        endTime = time.time()
        msecs = (endTime - startTime)
        print(func.__name__+" running time is %.2f s" %msecs)
        return result
    return wrapper

@echoRuntime
def test():
    return 1

print test()
