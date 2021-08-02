def add_num(d):
    def e_time(func):
        def warp(*argv, **kwargs):
            print 123+d
            data = func(*argv, **kwargs)
            print 456
            return data
        return warp
    return e_time
def e_time(func):
    def warp(*argv, **kwargs):
        print 123
        data = func(*argv, **kwargs)
        print 456
        return data
    return warp


def print_time(d):
    def sec_wrapper(func):
        def wrapper(*argv, **kw):
            result = func(*argv, **kw)
            print("After execute " + str(d))
            return result
        return wrapper
    return sec_wrapper


@print_time(123)
def test(a):
    print "inside"
    return a+1

print test(1)
#print e_time(test, d=1)(1)
