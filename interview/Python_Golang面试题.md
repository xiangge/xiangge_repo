# 全栈开发工程师面试题大全

**生成日期**: 2026-04-25  
**适用对象**: 后端开发工程师、全栈工程师、DevOps工程师、云计算工程师

---

## 目录

### Python篇
1. [Python基础](#python基础)
2. [数据结构与算法](#python数据结构与算法)
3. [面向对象](#python面向对象)
4. [并发编程](#python并发编程)
5. [高级特性](#python高级特性)
6. [常见陷阱](#python常见陷阱)

### Golang篇
1. [Go基础](#go基础)
2. [并发编程](#go并发编程)
3. [接口与类型](#go接口与类型)
4. [内存管理](#go内存管理)
5. [常见模式](#go常见模式)
6. [性能优化](#go性能优化)

### Shell篇
1. [Shell基础](#shell基础)
2. [文本处理三剑客](#shell文本处理)
3. [脚本编程](#shell脚本编程)
4. [进程管理](#进程与系统管理)

### Node.js篇
1. [事件循环](#事件循环event-loop)
2. [模块系统](#模块系统)
3. [异步编程](#异步编程演进)
4. [Stream流](#stream-流)
5. [集群管理](#集群cluster和进程管理)

### Vue.js篇
1. [响应式原理](#响应式原理)
2. [生命周期](#生命周期钩子)
3. [组件通信](#组件通信)
4. [状态管理](#vuex-状态管理)
5. [Composition API](#vue-3-composition-api)

### GitOps篇
1. [GitOps核心概念](#gitops核心概念)
2. [Argo CD](#argo-cd实战)
3. [Flux](#flux实战)
4. [安全实践](#gitops安全和合规)

### DevOps篇
1. [CI/CD流程](#cicd流程)
2. [Docker容器化](#docker容器化)
3. [Kubernetes](#kubernetes部署)
4. [监控告警](#监控和告警)
5. [日志管理](#日志管理)

### 云计算篇
1. [云服务模型](#云服务模型)
2. [AWS核心服务](#aws核心服务)
3. [云原生架构](#kubernetes云原生架构)
4. [成本优化](#成本优化)
5. [安全最佳实践](#安全最佳实践)

---

# Python篇

## Python基础

### 1. Python2和Python3的主要区别

**问题**: 列举Python2和Python3的主要区别

**答案**:

| 特性 | Python 2 | Python 3 |
|-----|---------|---------|
| **print** | `print "hello"` (语句) | `print("hello")` (函数) |
| **整数除法** | `5/2 = 2` | `5/2 = 2.5`, `5//2 = 2` |
| **Unicode** | `str`是字节，`unicode`是文本 | `str`是文本，`bytes`是字节 |
| **range** | `range()`返回列表 | `range()`返回迭代器 |
| **异常语法** | `except Exception, e:` | `except Exception as e:` |
| **input** | `raw_input()` | `input()` |
| **dict方法** | `.keys()`, `.values()` 返回列表 | 返回视图对象 |

```python
# Python 2
print "Hello"
print 5/2  # 输出: 2

# Python 3
print("Hello")
print(5/2)   # 输出: 2.5
print(5//2)  # 输出: 2
```

---

### 2. 可变对象 vs 不可变对象

**问题**: 解释Python中的可变对象和不可变对象

**答案**:

**不可变对象** (Immutable):
- `int`, `float`, `str`, `tuple`, `frozenset`
- 修改会创建新对象

**可变对象** (Mutable):
- `list`, `dict`, `set`, `bytearray`
- 修改不会创建新对象，原地修改

```python
# 不可变对象示例
a = "hello"
print(id(a))  # 4312345678
a = a + " world"
print(id(a))  # 4387654321 (不同的ID，新对象)

# 可变对象示例
lst = [1, 2, 3]
print(id(lst))  # 4398765432
lst.append(4)
print(id(lst))  # 4398765432 (相同ID，原地修改)
```

**面试陷阱**:
```python
# 默认参数陷阱
def add_item(item, lst=[]):  # 危险！
    lst.append(item)
    return lst

print(add_item(1))  # [1]
print(add_item(2))  # [1, 2] ← 意外！

# 正确做法
def add_item(item, lst=None):
    if lst is None:
        lst = []
    lst.append(item)
    return lst
```

---

### 3. `is` vs `==`

**问题**: `is` 和 `==` 的区别

**答案**:

- `==`: 比较**值**是否相等
- `is`: 比较**身份**（内存地址）是否相同

```python
a = [1, 2, 3]
b = [1, 2, 3]
c = a

print(a == b)  # True (值相等)
print(a is b)  # False (不同对象)
print(a is c)  # True (同一对象)

# 小整数缓存（-5到256）
x = 256
y = 256
print(x is y)  # True (缓存)

x = 257
y = 257
print(x is y)  # False (超出缓存范围)

# None 始终用 is
if value is None:  # ✓ 正确
    pass

if value == None:  # ✗ 不推荐
    pass
```

---

### 4. 深拷贝 vs 浅拷贝

**问题**: 解释深拷贝和浅拷贝的区别

**答案**:

```python
import copy

# 浅拷贝
original = [[1, 2, 3], [4, 5, 6]]
shallow = copy.copy(original)
# 或
shallow = original[:]
# 或
shallow = list(original)

shallow[0][0] = 999
print(original)  # [[999, 2, 3], [4, 5, 6]] ← 被修改了！

# 深拷贝
original = [[1, 2, 3], [4, 5, 6]]
deep = copy.deepcopy(original)

deep[0][0] = 999
print(original)  # [[1, 2, 3], [4, 5, 6]] ← 未修改
print(deep)      # [[999, 2, 3], [4, 5, 6]]
```

**规则**:
- **浅拷贝**: 只复制顶层对象，内部对象仍是引用
- **深拷贝**: 递归复制所有层级

---

## Python数据结构与算法

### 5. 列表推导式 vs 生成器表达式

**问题**: 列表推导式和生成器表达式的区别

**答案**:

```python
# 列表推导式 - 立即创建整个列表
squares_list = [x**2 for x in range(1000000)]
# 内存占用: ~8MB

# 生成器表达式 - 惰性求值
squares_gen = (x**2 for x in range(1000000))
# 内存占用: ~88 bytes

# 使用
print(next(squares_gen))  # 0
print(next(squares_gen))  # 1
print(next(squares_gen))  # 4

# 迭代
for square in squares_gen:
    if square > 100:
        break
```

**何时使用**:
- **列表推导式**: 需要多次遍历、需要索引、数据量小
- **生成器表达式**: 只遍历一次、数据量大、内存受限

---

### 6. `*args` 和 `**kwargs`

**问题**: 解释 `*args` 和 `**kwargs` 的用法

**答案**:

```python
# *args - 可变位置参数（元组）
def sum_all(*args):
    return sum(args)

print(sum_all(1, 2, 3, 4, 5))  # 15

# **kwargs - 可变关键字参数（字典）
def print_info(**kwargs):
    for key, value in kwargs.items():
        print(f"{key}: {value}")

print_info(name="Alice", age=30, city="Beijing")
# name: Alice
# age: 30
# city: Beijing

# 组合使用
def func(a, b, *args, **kwargs):
    print(f"a={a}, b={b}")
    print(f"args={args}")
    print(f"kwargs={kwargs}")

func(1, 2, 3, 4, 5, x=10, y=20)
# a=1, b=2
# args=(3, 4, 5)
# kwargs={'x': 10, 'y': 20}

# 解包
def add(a, b, c):
    return a + b + c

nums = [1, 2, 3]
print(add(*nums))  # 6

params = {'a': 1, 'b': 2, 'c': 3}
print(add(**params))  # 6
```

---

### 7. 装饰器

**问题**: 实现一个计时装饰器和登录检查装饰器

**答案**:

```python
import time
from functools import wraps

# 计时装饰器
def timer(func):
    @wraps(func)  # 保留原函数元信息
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        print(f"{func.__name__} took {end - start:.4f} seconds")
        return result
    return wrapper

@timer
def slow_function():
    time.sleep(1)
    return "Done"

slow_function()
# slow_function took 1.0012 seconds

# 带参数的装饰器
def repeat(times):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for _ in range(times):
                result = func(*args, **kwargs)
            return result
        return wrapper
    return decorator

@repeat(3)
def say_hello(name):
    print(f"Hello, {name}!")

say_hello("Alice")
# Hello, Alice!
# Hello, Alice!
# Hello, Alice!

# 类装饰器
class LoginRequired:
    def __init__(self, func):
        self.func = func
        self.is_logged_in = False
    
    def __call__(self, *args, **kwargs):
        if not self.is_logged_in:
            raise Exception("Please login first")
        return self.func(*args, **kwargs)

@LoginRequired
def view_profile():
    return "Profile page"

# view_profile()  # 抛出异常
```

---

## Python面向对象

### 8. 类方法、静态方法、实例方法

**问题**: 解释三种方法的区别

**答案**:

```python
class MyClass:
    class_var = "I'm a class variable"
    
    def __init__(self, value):
        self.instance_var = value
    
    # 实例方法 - 第一个参数是 self
    def instance_method(self):
        return f"Instance: {self.instance_var}"
    
    # 类方法 - 第一个参数是 cls
    @classmethod
    def class_method(cls):
        return f"Class: {cls.class_var}"
    
    # 静态方法 - 无特殊参数
    @staticmethod
    def static_method(x, y):
        return x + y

obj = MyClass("hello")

# 调用方式
print(obj.instance_method())      # Instance: hello
print(MyClass.class_method())     # Class: I'm a class variable
print(MyClass.static_method(1, 2)) # 3

# 实例也可以调用类方法和静态方法
print(obj.class_method())         # Class: I'm a class variable
print(obj.static_method(3, 4))    # 7
```

**使用场景**:
- **实例方法**: 需要访问实例属性
- **类方法**: 需要访问类属性，工厂模式
- **静态方法**: 不需要访问类或实例，工具函数

```python
# 类方法作为工厂方法
class Date:
    def __init__(self, year, month, day):
        self.year = year
        self.month = month
        self.day = day
    
    @classmethod
    def from_string(cls, date_string):
        year, month, day = map(int, date_string.split('-'))
        return cls(year, month, day)
    
    @classmethod
    def today(cls):
        import datetime
        today = datetime.date.today()
        return cls(today.year, today.month, today.day)

d1 = Date(2026, 4, 25)
d2 = Date.from_string("2026-04-25")
d3 = Date.today()
```

---

### 9. `__new__` vs `__init__`

**问题**: `__new__` 和 `__init__` 的区别

**答案**:

```python
class MyClass:
    def __new__(cls, *args, **kwargs):
        print("__new__ called")
        instance = super().__new__(cls)
        return instance
    
    def __init__(self, value):
        print("__init__ called")
        self.value = value

obj = MyClass(42)
# __new__ called
# __init__ called

"""
区别:
1. __new__ 创建对象（返回实例）
2. __init__ 初始化对象（无返回值）
3. __new__ 先于 __init__ 调用
4. __new__ 是类方法（cls），__init__ 是实例方法（self）
"""

# 单例模式实现
class Singleton:
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self, value):
        self.value = value

s1 = Singleton(1)
s2 = Singleton(2)
print(s1 is s2)  # True
print(s1.value)  # 2 (被覆盖)
```

---

### 10. 魔法方法（Magic Methods）

**问题**: 实现一个支持上下文管理和比较的类

**答案**:

```python
class Vector:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    
    # 字符串表示
    def __repr__(self):
        return f"Vector({self.x}, {self.y})"
    
    def __str__(self):
        return f"({self.x}, {self.y})"
    
    # 算术运算
    def __add__(self, other):
        return Vector(self.x + other.x, self.y + other.y)
    
    def __sub__(self, other):
        return Vector(self.x - other.x, self.y - other.y)
    
    def __mul__(self, scalar):
        return Vector(self.x * scalar, self.y * scalar)
    
    # 比较运算
    def __eq__(self, other):
        return self.x == other.x and self.y == other.y
    
    def __lt__(self, other):
        return (self.x**2 + self.y**2) < (other.x**2 + other.y**2)
    
    # 长度
    def __len__(self):
        return int((self.x**2 + self.y**2) ** 0.5)
    
    # 索引访问
    def __getitem__(self, index):
        if index == 0:
            return self.x
        elif index == 1:
            return self.y
        else:
            raise IndexError("Index out of range")

v1 = Vector(3, 4)
v2 = Vector(1, 2)

print(v1 + v2)      # Vector(4, 6)
print(v1 * 2)       # Vector(6, 8)
print(v1 == v2)     # False
print(v1 > v2)      # True
print(len(v1))      # 5
print(v1[0], v1[1]) # 3 4

# 上下文管理器
class FileManager:
    def __init__(self, filename, mode):
        self.filename = filename
        self.mode = mode
        self.file = None
    
    def __enter__(self):
        self.file = open(self.filename, self.mode)
        return self.file
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.file:
            self.file.close()
        # 返回 True 抑制异常，False 传播异常
        return False

with FileManager('test.txt', 'w') as f:
    f.write('Hello, World!')
# 文件自动关闭
```

---

## Python并发编程

### 11. GIL（全局解释器锁）

**问题**: 解释GIL及其影响

**答案**:

**什么是GIL**:
- Global Interpreter Lock（全局解释器锁）
- 同一时刻只有一个线程执行Python字节码
- 保护CPython内存管理的线程安全

**影响**:
```python
import threading
import time

# CPU密集型任务 - 多线程无法提速
def cpu_bound(n):
    count = 0
    for i in range(n):
        count += i
    return count

# 单线程
start = time.time()
cpu_bound(10000000)
cpu_bound(10000000)
print(f"单线程: {time.time() - start:.2f}s")  # ~1.2s

# 多线程
start = time.time()
t1 = threading.Thread(target=cpu_bound, args=(10000000,))
t2 = threading.Thread(target=cpu_bound, args=(10000000,))
t1.start()
t2.start()
t1.join()
t2.join()
print(f"多线程: {time.time() - start:.2f}s")  # ~1.2s (无提速)

# I/O密集型任务 - 多线程有效
import requests

def io_bound(url):
    response = requests.get(url)
    return len(response.content)

# 多线程对I/O密集型任务有效，因为等待I/O时会释放GIL
```

**解决方案**:
1. **多进程** (`multiprocessing`) - CPU密集型
2. **异步IO** (`asyncio`) - I/O密集型
3. **C扩展** - 绕过GIL

```python
from multiprocessing import Pool

# 多进程
with Pool(2) as pool:
    results = pool.map(cpu_bound, [10000000, 10000000])
# 实际并行，速度提升
```

---

### 12. 多线程 vs 多进程 vs 协程

**问题**: 比较三种并发方式

**答案**:

```python
import threading
import multiprocessing
import asyncio
import time

# 1. 多线程 - 适合I/O密集型
def thread_task(n):
    print(f"Thread {n} starting")
    time.sleep(1)  # 模拟I/O
    print(f"Thread {n} done")

threads = []
for i in range(3):
    t = threading.Thread(target=thread_task, args=(i,))
    threads.append(t)
    t.start()

for t in threads:
    t.join()

# 2. 多进程 - 适合CPU密集型
def process_task(n):
    print(f"Process {n} starting")
    # CPU密集计算
    sum([i**2 for i in range(1000000)])
    print(f"Process {n} done")

processes = []
for i in range(3):
    p = multiprocessing.Process(target=process_task, args=(i,))
    processes.append(p)
    p.start()

for p in processes:
    p.join()

# 3. 协程 - 适合高并发I/O
async def async_task(n):
    print(f"Async {n} starting")
    await asyncio.sleep(1)  # 异步I/O
    print(f"Async {n} done")

async def main():
    tasks = [async_task(i) for i in range(3)]
    await asyncio.gather(*tasks)

asyncio.run(main())
```

**对比表**:

| 特性 | 多线程 | 多进程 | 协程 |
|-----|-------|-------|------|
| **并行性** | 伪并行（GIL） | 真并行 | 单线程并发 |
| **内存** | 共享内存 | 独立内存 | 共享内存 |
| **开销** | 低 | 高 | 极低 |
| **通信** | 简单 | 复杂（IPC） | 简单 |
| **适用** | I/O密集 | CPU密集 | 高并发I/O |
| **数量** | ~数百 | ~数十 | ~数万 |

---

### 13. asyncio 协程

**问题**: 实现异步爬虫

**答案**:

```python
import asyncio
import aiohttp
import time

async def fetch(session, url):
    async with session.get(url) as response:
        return await response.text()

async def fetch_all(urls):
    async with aiohttp.ClientSession() as session:
        tasks = [fetch(session, url) for url in urls]
        results = await asyncio.gather(*tasks)
        return results

urls = [
    'http://example.com',
    'http://example.org',
    'http://example.net'
] * 10

# 异步方式
start = time.time()
results = asyncio.run(fetch_all(urls))
print(f"异步: {time.time() - start:.2f}s")

# 同步方式对比
import requests

start = time.time()
for url in urls:
    requests.get(url)
print(f"同步: {time.time() - start:.2f}s")

# 常见模式
async def producer(queue):
    for i in range(5):
        await asyncio.sleep(1)
        await queue.put(i)
        print(f"Produced {i}")
    await queue.put(None)  # 结束信号

async def consumer(queue):
    while True:
        item = await queue.get()
        if item is None:
            break
        print(f"Consumed {item}")
        await asyncio.sleep(0.5)

async def main():
    queue = asyncio.Queue()
    await asyncio.gather(
        producer(queue),
        consumer(queue)
    )

asyncio.run(main())
```

---

## Python高级特性

### 14. 闭包和作用域

**问题**: 解释闭包和LEGB规则

**答案**:

```python
# LEGB规则: Local -> Enclosing -> Global -> Built-in

x = "global"

def outer():
    x = "enclosing"
    
    def inner():
        x = "local"
        print(x)  # local
    
    inner()
    print(x)  # enclosing

outer()
print(x)  # global

# 闭包
def make_multiplier(n):
    def multiplier(x):
        return x * n  # n 来自外层作用域
    return multiplier

times3 = make_multiplier(3)
times5 = make_multiplier(5)

print(times3(10))  # 30
print(times5(10))  # 50

# nonlocal 和 global
count = 0

def outer():
    count = 0
    
    def increment_local():
        count = 1  # 创建新的局部变量
        print(f"Local: {count}")
    
    def increment_nonlocal():
        nonlocal count  # 修改外层作用域
        count += 1
        print(f"Nonlocal: {count}")
    
    def increment_global():
        global count  # 修改全局变量
        count += 1
        print(f"Global: {count}")
    
    increment_local()      # Local: 1
    print(count)           # 0 (未修改)
    
    increment_nonlocal()   # Nonlocal: 1
    print(count)           # 1 (已修改)
    
    increment_global()     # Global: 1

outer()
print(count)  # 1 (全局被修改)
```

---

### 15. 生成器和迭代器

**问题**: 实现一个自定义迭代器和生成器

**答案**:

```python
# 迭代器协议
class Countdown:
    def __init__(self, start):
        self.current = start
    
    def __iter__(self):
        return self
    
    def __next__(self):
        if self.current <= 0:
            raise StopIteration
        self.current -= 1
        return self.current + 1

for num in Countdown(5):
    print(num)  # 5, 4, 3, 2, 1

# 生成器函数
def countdown_gen(start):
    while start > 0:
        yield start
        start -= 1

for num in countdown_gen(5):
    print(num)  # 5, 4, 3, 2, 1

# 生成器表达式
squares = (x**2 for x in range(10))

# yield from
def flatten(nested_list):
    for item in nested_list:
        if isinstance(item, list):
            yield from flatten(item)  # 递归展平
        else:
            yield item

nested = [1, [2, 3, [4, 5]], 6]
print(list(flatten(nested)))  # [1, 2, 3, 4, 5, 6]

# 生成器的 send 和 throw
def coroutine():
    print("Coroutine started")
    x = yield
    print(f"Received: {x}")
    y = yield x * 2
    print(f"Received: {y}")

gen = coroutine()
next(gen)  # 启动协程
gen.send(10)  # Received: 10, 返回 20
gen.send(5)   # Received: 5
```

---

### 16. 元类（Metaclass）

**问题**: 解释元类并实现一个单例元类

**答案**:

```python
# 类是对象，元类是类的类
class Meta(type):
    def __new__(cls, name, bases, attrs):
        print(f"Creating class {name}")
        attrs['class_id'] = id(cls)
        return super().__new__(cls, name, bases, attrs)

class MyClass(metaclass=Meta):
    pass
# Creating class MyClass

# 单例元类
class SingletonMeta(type):
    _instances = {}
    
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]

class Singleton(metaclass=SingletonMeta):
    def __init__(self, value):
        self.value = value

s1 = Singleton(1)
s2 = Singleton(2)
print(s1 is s2)  # True
print(s1.value)  # 1 (不会被覆盖，因为没创建新实例)

# ORM 示例
class ModelMeta(type):
    def __new__(cls, name, bases, attrs):
        if name == 'Model':
            return super().__new__(cls, name, bases, attrs)
        
        # 收集字段
        fields = {}
        for key, value in attrs.items():
            if isinstance(value, Field):
                fields[key] = value
        
        attrs['_fields'] = fields
        return super().__new__(cls, name, bases, attrs)

class Field:
    def __init__(self, field_type):
        self.field_type = field_type

class Model(metaclass=ModelMeta):
    pass

class User(Model):
    name = Field(str)
    age = Field(int)

print(User._fields)  # {'name': <Field object>, 'age': <Field object>}
```

---

## Python常见陷阱

### 17. 常见陷阱合集

**问题**: 识别以下代码的问题

**答案**:

```python
# 陷阱1: 可变默认参数
def append_to(element, lst=[]):
    lst.append(element)
    return lst

print(append_to(1))  # [1]
print(append_to(2))  # [1, 2] ← 问题！

# 正确做法
def append_to(element, lst=None):
    if lst is None:
        lst = []
    lst.append(element)
    return lst

# 陷阱2: 闭包中的延迟绑定
funcs = []
for i in range(3):
    funcs.append(lambda: i)

print([f() for f in funcs])  # [2, 2, 2] ← 都是最后的值

# 正确做法
funcs = []
for i in range(3):
    funcs.append(lambda x=i: x)  # 立即绑定

print([f() for f in funcs])  # [0, 1, 2]

# 陷阱3: 浅拷贝嵌套列表
matrix = [[0] * 3] * 3
matrix[0][0] = 1
print(matrix)  # [[1, 0, 0], [1, 0, 0], [1, 0, 0]] ← 问题！

# 正确做法
matrix = [[0] * 3 for _ in range(3)]
matrix[0][0] = 1
print(matrix)  # [[1, 0, 0], [0, 0, 0], [0, 0, 0]]

# 陷阱4: 异常处理中的变量作用域
try:
    1 / 0
except Exception as e:
    pass

# print(e)  # Python 3: NameError (e 被删除)

# 陷阱5: 字典迭代时修改
d = {'a': 1, 'b': 2, 'c': 3}
# for key in d:
#     if d[key] == 2:
#         del d[key]  # RuntimeError

# 正确做法
for key in list(d.keys()):
    if d[key] == 2:
        del d[key]

# 陷阱6: += 对不可变对象
a = (1, 2)
b = a
a += (3, 4)
print(a is b)  # False (创建新对象)

a = [1, 2]
b = a
a += [3, 4]
print(a is b)  # True (原地修改)
```

---

# Golang篇

## Go基础

### 1. 值传递 vs 指针传递

**问题**: 解释Go中的值传递和指针的使用

**答案**:

```go
package main

import "fmt"

// 值传递 - 复制
func modifyValue(x int) {
    x = 100
}

// 指针传递 - 引用
func modifyPointer(x *int) {
    *x = 100
}

// 切片是引用类型
func modifySlice(s []int) {
    s[0] = 100  // 修改会影响原切片
}

func appendSlice(s []int) {
    s = append(s, 100)  // 可能重新分配，不影响原切片
}

func appendSlicePointer(s *[]int) {
    *s = append(*s, 100)  // 影响原切片
}

func main() {
    // 值传递
    x := 10
    modifyValue(x)
    fmt.Println(x)  // 10 (未修改)
    
    // 指针传递
    modifyPointer(&x)
    fmt.Println(x)  // 100 (已修改)
    
    // 切片
    s := []int{1, 2, 3}
    modifySlice(s)
    fmt.Println(s)  // [100, 2, 3]
    
    appendSlice(s)
    fmt.Println(s)  // [100, 2, 3] (未添加)
    
    appendSlicePointer(&s)
    fmt.Println(s)  // [100, 2, 3, 100] (已添加)
}
```

**规则**:
- Go都是**值传递**
- 传指针是传递指针的**值**（地址的副本）
- 切片、map、channel是引用类型（内部包含指针）

---

### 2. defer 执行顺序

**问题**: 解释defer的执行时机和顺序

**答案**:

```go
package main

import "fmt"

func deferOrder() {
    defer fmt.Println("1")
    defer fmt.Println("2")
    defer fmt.Println("3")
    fmt.Println("Function body")
}

// 输出:
// Function body
// 3
// 2
// 1

// defer 参数立即求值
func deferEval() {
    i := 0
    defer fmt.Println("Deferred:", i)  // i=0 (立即求值)
    i++
    fmt.Println("Function:", i)
}

// 输出:
// Function: 1
// Deferred: 0

// defer 与闭包
func deferClosure() {
    i := 0
    defer func() {
        fmt.Println("Deferred:", i)  // i=1 (闭包捕获)
    }()
    i++
    fmt.Println("Function:", i)
}

// 输出:
// Function: 1
// Deferred: 1

// defer 与返回值
func deferReturn() (result int) {
    defer func() {
        result++  // 修改命名返回值
    }()
    return 5
}

func main() {
    fmt.Println(deferReturn())  // 6
}

// defer 常见用途
func fileOperation() error {
    f, err := os.Open("file.txt")
    if err != nil {
        return err
    }
    defer f.Close()  // 确保文件关闭
    
    // ... 操作文件
    return nil
}

// defer 与 panic/recover
func safeDivide(a, b int) (result int) {
    defer func() {
        if r := recover(); r != nil {
            fmt.Println("Recovered:", r)
            result = 0
        }
    }()
    return a / b
}
```

**要点**:
- defer按**LIFO**（后进先出）顺序执行
- defer参数**立即求值**
- defer在函数**返回前**执行
- defer可以修改**命名返回值**

---

### 3. slice vs array

**问题**: 解释切片和数组的区别

**答案**:

```go
package main

import "fmt"

func main() {
    // 数组 - 固定长度，值类型
    var arr1 [3]int = [3]int{1, 2, 3}
    arr2 := arr1
    arr2[0] = 100
    fmt.Println(arr1)  // [1 2 3] (未修改)
    fmt.Println(arr2)  // [100 2 3]
    
    // 切片 - 动态长度，引用类型
    slice1 := []int{1, 2, 3}
    slice2 := slice1
    slice2[0] = 100
    fmt.Println(slice1)  // [100 2 3] (已修改)
    
    // 切片底层结构
    /*
    type slice struct {
        array unsafe.Pointer  // 指向底层数组
        len   int             // 长度
        cap   int             // 容量
    }
    */
    
    // 切片扩容
    s := make([]int, 0, 3)
    fmt.Printf("len=%d cap=%d\n", len(s), cap(s))  // len=0 cap=3
    
    s = append(s, 1, 2, 3)
    fmt.Printf("len=%d cap=%d\n", len(s), cap(s))  // len=3 cap=3
    
    s = append(s, 4)  // 触发扩容
    fmt.Printf("len=%d cap=%d\n", len(s), cap(s))  // len=4 cap=6
    
    // 切片陷阱
    slice := []int{1, 2, 3, 4, 5}
    newSlice := slice[1:3]  // [2, 3]
    newSlice[0] = 100
    fmt.Println(slice)     // [1 100 3 4 5] (共享底层数组)
    
    // 避免陷阱 - 使用 copy
    slice3 := make([]int, len(newSlice))
    copy(slice3, newSlice)
    slice3[0] = 200
    fmt.Println(newSlice)  // [100 3] (未修改)
}
```

**扩容规则**（Go 1.18+）:
- cap < 256: 翻倍
- cap >= 256: 增长因子逐渐降低到 1.25

---

## Go并发编程

### 4. Goroutine vs Thread

**问题**: Goroutine和线程的区别

**答案**:

| 特性 | Goroutine | 线程 |
|-----|----------|------|
| **创建成本** | ~2KB 栈 | ~1MB 栈 |
| **调度** | M:N (用户态) | 1:1 (内核态) |
| **切换成本** | 极低 (~200ns) | 高 (~1-2μs) |
| **数量** | 数百万 | 数千 |
| **通信** | channel | 共享内存+锁 |

```go
package main

import (
    "fmt"
    "runtime"
    "sync"
    "time"
)

func main() {
    // 启动大量goroutine
    var wg sync.WaitGroup
    
    for i := 0; i < 100000; i++ {
        wg.Add(1)
        go func(n int) {
            defer wg.Done()
            time.Sleep(time.Second)
        }(i)
    }
    
    fmt.Println("Goroutines:", runtime.NumGoroutine())
    wg.Wait()
}

// GMP模型
/*
G (Goroutine): 用户态线程
M (Machine): 内核线程
P (Processor): 逻辑处理器（调度器）

一个M绑定一个P，P的本地队列存放G
M执行G，阻塞时解绑P，其他M接管P
*/

// 设置GOMAXPROCS
func setGOMAXPROCS() {
    runtime.GOMAXPROCS(4)  // 使用4个逻辑处理器
    fmt.Println("NumCPU:", runtime.NumCPU())
    fmt.Println("GOMAXPROCS:", runtime.GOMAXPROCS(0))
}
```

---

### 5. Channel 通信

**问题**: 实现生产者-消费者模式

**答案**:

```go
package main

import (
    "fmt"
    "sync"
    "time"
)

// 无缓冲channel - 同步
func unbuffered() {
    ch := make(chan int)
    
    go func() {
        ch <- 1  // 发送，阻塞直到接收
        fmt.Println("Sent")
    }()
    
    time.Sleep(time.Second)
    fmt.Println("Receiving...")
    x := <-ch  // 接收
    fmt.Println("Received:", x)
}

// 有缓冲channel - 异步
func buffered() {
    ch := make(chan int, 2)
    
    ch <- 1  // 不阻塞
    ch <- 2  // 不阻塞
    // ch <- 3  // 阻塞（缓冲满）
    
    fmt.Println(<-ch)  // 1
    fmt.Println(<-ch)  // 2
}

// 生产者-消费者
func producerConsumer() {
    jobs := make(chan int, 100)
    results := make(chan int, 100)
    
    // 3个worker
    var wg sync.WaitGroup
    for w := 1; w <= 3; w++ {
        wg.Add(1)
        go worker(w, jobs, results, &wg)
    }
    
    // 发送任务
    for j := 1; j <= 9; j++ {
        jobs <- j
    }
    close(jobs)  // 关闭发送端
    
    wg.Wait()
    close(results)
    
    // 收集结果
    for result := range results {
        fmt.Println("Result:", result)
    }
}

func worker(id int, jobs <-chan int, results chan<- int, wg *sync.WaitGroup) {
    defer wg.Done()
    for j := range jobs {  // 从channel读取直到关闭
        fmt.Printf("Worker %d processing job %d\n", id, j)
        time.Sleep(time.Second)
        results <- j * 2
    }
}

// select 多路复用
func selectDemo() {
    ch1 := make(chan string)
    ch2 := make(chan string)
    
    go func() {
        time.Sleep(1 * time.Second)
        ch1 <- "one"
    }()
    
    go func() {
        time.Sleep(2 * time.Second)
        ch2 <- "two"
    }()
    
    for i := 0; i < 2; i++ {
        select {
        case msg1 := <-ch1:
            fmt.Println("Received", msg1)
        case msg2 := <-ch2:
            fmt.Println("Received", msg2)
        case <-time.After(3 * time.Second):
            fmt.Println("Timeout")
        }
    }
}

// 关闭channel
func closeChannel() {
    ch := make(chan int, 2)
    ch <- 1
    ch <- 2
    close(ch)
    
    // 从已关闭channel接收
    fmt.Println(<-ch)  // 1
    fmt.Println(<-ch)  // 2
    fmt.Println(<-ch)  // 0 (零值)
    
    // 检查channel是否关闭
    val, ok := <-ch
    if !ok {
        fmt.Println("Channel closed")
    }
    
    // range自动检测关闭
    ch2 := make(chan int, 2)
    ch2 <- 1
    ch2 <- 2
    close(ch2)
    
    for val := range ch2 {
        fmt.Println(val)
    }
}

func main() {
    producerConsumer()
}
```

---

### 6. sync 包

**问题**: 使用sync包实现并发安全

**答案**:

```go
package main

import (
    "fmt"
    "sync"
    "sync/atomic"
    "time"
)

// 1. Mutex - 互斥锁
type SafeCounter struct {
    mu sync.Mutex
    count int
}

func (c *SafeCounter) Inc() {
    c.mu.Lock()
    defer c.mu.Unlock()
    c.count++
}

func (c *SafeCounter) Value() int {
    c.mu.Lock()
    defer c.mu.Unlock()
    return c.count
}

// 2. RWMutex - 读写锁
type SafeMap struct {
    mu sync.RWMutex
    data map[string]int
}

func (m *SafeMap) Get(key string) (int, bool) {
    m.mu.RLock()  // 读锁
    defer m.mu.RUnlock()
    val, ok := m.data[key]
    return val, ok
}

func (m *SafeMap) Set(key string, val int) {
    m.mu.Lock()  // 写锁
    defer m.mu.Unlock()
    m.data[key] = val
}

// 3. WaitGroup - 等待组
func waitGroupDemo() {
    var wg sync.WaitGroup
    
    for i := 0; i < 5; i++ {
        wg.Add(1)
        go func(n int) {
            defer wg.Done()
            fmt.Println("Goroutine", n)
            time.Sleep(time.Second)
        }(i)
    }
    
    wg.Wait()  // 等待所有goroutine完成
    fmt.Println("All done")
}

// 4. Once - 单次执行
var once sync.Once

func doOnce() {
    once.Do(func() {
        fmt.Println("Executed once")
    })
}

func onceDemo() {
    for i := 0; i < 3; i++ {
        go doOnce()
    }
    time.Sleep(time.Second)
}

// 5. atomic - 原子操作
func atomicDemo() {
    var counter int64
    var wg sync.WaitGroup
    
    for i := 0; i < 1000; i++ {
        wg.Add(1)
        go func() {
            defer wg.Done()
            atomic.AddInt64(&counter, 1)
        }()
    }
    
    wg.Wait()
    fmt.Println("Counter:", counter)  // 1000
}

// 6. Cond - 条件变量
func condDemo() {
    cond := sync.NewCond(&sync.Mutex{})
    queue := make([]int, 0)
    
    // 消费者
    go func() {
        for {
            cond.L.Lock()
            for len(queue) == 0 {
                cond.Wait()  // 等待条件
            }
            val := queue[0]
            queue = queue[1:]
            fmt.Println("Consumed:", val)
            cond.L.Unlock()
        }
    }()
    
    // 生产者
    for i := 0; i < 5; i++ {
        cond.L.Lock()
        queue = append(queue, i)
        cond.Signal()  // 通知一个等待者
        cond.L.Unlock()
        time.Sleep(time.Second)
    }
}

// 7. sync.Pool - 对象池
var pool = sync.Pool{
    New: func() interface{} {
        return new(bytes.Buffer)
    },
}

func poolDemo() {
    buf := pool.Get().(*bytes.Buffer)
    defer pool.Put(buf)
    
    buf.WriteString("Hello")
    fmt.Println(buf.String())
    buf.Reset()
}

func main() {
    waitGroupDemo()
}
```

---

## Go接口与类型

### 7. 接口实现

**问题**: 解释Go的隐式接口实现

**答案**:

```go
package main

import "fmt"

// 接口定义
type Speaker interface {
    Speak() string
}

type Mover interface {
    Move()
}

// 组合接口
type Animal interface {
    Speaker
    Mover
}

// Dog 隐式实现接口
type Dog struct {
    Name string
}

func (d Dog) Speak() string {
    return "Woof!"
}

func (d Dog) Move() {
    fmt.Println(d.Name, "is running")
}

// Cat 只实现部分接口
type Cat struct {
    Name string
}

func (c Cat) Speak() string {
    return "Meow!"
}

func main() {
    dog := Dog{Name: "Buddy"}
    
    // 类型断言
    var s Speaker = dog
    fmt.Println(s.Speak())
    
    // 接口赋值
    var a Animal = dog
    a.Move()
    
    // 类型断言
    if d, ok := s.(Dog); ok {
        fmt.Println("It's a dog:", d.Name)
    }
    
    // 类型 switch
    describe(dog)
    describe("hello")
    describe(42)
}

func describe(i interface{}) {
    switch v := i.(type) {
    case Dog:
        fmt.Printf("Dog: %s\n", v.Name)
    case string:
        fmt.Printf("String: %s\n", v)
    case int:
        fmt.Printf("Int: %d\n", v)
    default:
        fmt.Printf("Unknown type: %T\n", v)
    }
}

// 空接口
func printAny(v interface{}) {
    fmt.Println(v)
}

// 接口值 = (type, value)
func interfaceValue() {
    var i interface{}
    
    i = 42
    fmt.Printf("(%T, %v)\n", i, i)  // (int, 42)
    
    i = "hello"
    fmt.Printf("(%T, %v)\n", i, i)  // (string, hello)
    
    // nil 接口
    var s Speaker
    fmt.Printf("(%T, %v)\n", s, s)  // (<nil>, <nil>)
    
    // 接口类型不为nil，但值为nil
    var dog *Dog
    s = dog
    fmt.Printf("(%T, %v)\n", s, s)  // (*Dog, <nil>)
    fmt.Println(s == nil)  // false!
}
```

---

### 8. 类型嵌入（组合）

**问题**: 实现类型组合

**答案**:

```go
package main

import "fmt"

// 基础类型
type Engine struct {
    Power int
}

func (e Engine) Start() {
    fmt.Println("Engine started")
}

type Wheel struct {
    Size int
}

// 组合
type Car struct {
    Engine  // 嵌入（继承方法）
    *Wheel  // 嵌入指针
    Brand string
}

func main() {
    car := Car{
        Engine: Engine{Power: 200},
        Wheel:  &Wheel{Size: 18},
        Brand:  "Tesla",
    }
    
    // 直接访问嵌入类型的字段
    fmt.Println(car.Power)  // 200
    
    // 直接调用嵌入类型的方法
    car.Start()  // Engine started
    
    // 也可以显式访问
    fmt.Println(car.Engine.Power)
    car.Engine.Start()
}

// 方法覆盖
type SportsCar struct {
    Car
}

func (s SportsCar) Start() {
    fmt.Println("Sports car engine roaring!")
    s.Car.Start()  // 调用嵌入类型的方法
}

// 接口组合
type Reader interface {
    Read(p []byte) (n int, err error)
}

type Writer interface {
    Write(p []byte) (n int, err error)
}

type ReadWriter interface {
    Reader
    Writer
}
```

---

## Go内存管理

### 9. 内存逃逸分析

**问题**: 什么是内存逃逸？如何避免？

**答案**:

```go
package main

// 逃逸到堆
func escape() *int {
    x := 10
    return &x  // x 逃逸到堆
}

// 不逃逸（栈上）
func noEscape() int {
    x := 10
    return x
}

// 切片逃逸
func makeSlice() []int {
    s := make([]int, 0, 10)
    return s  // 逃逸到堆
}

// 闭包引用外部变量
func closure() func() int {
    x := 10
    return func() int {
        return x  // x 逃逸到堆
    }
}

// 接口类型
func interfaceEscape(i interface{}) {
    // i 逃逸到堆
}

// 逃逸分析
// go build -gcflags="-m" main.go

/*
逃逸场景:
1. 返回局部变量指针
2. 发送到channel
3. 切片/map扩容
4. 闭包引用
5. 接口类型赋值
*/

// 避免逃逸
func avoidEscape() {
    // 使用值类型而非指针
    var x int = 10
    
    // 预分配切片容量
    s := make([]int, 0, 100)
    
    // 使用sync.Pool重用对象
    // pool := sync.Pool{New: func() interface{} { return new(MyStruct) }}
}

func main() {
    escape()
}
```

**查看逃逸分析**:
```bash
go build -gcflags="-m -m" main.go
```

---

### 10. GC 垃圾回收

**问题**: 解释Go的GC机制

**答案**:

**Go GC特点**:
- **三色标记法** (Tri-color marking)
- **并发标记** (Concurrent marking)
- **写屏障** (Write barrier)
- **非分代** (Non-generational)

```go
package main

import (
    "runtime"
    "runtime/debug"
    "time"
)

func gcDemo() {
    // 手动触发GC
    runtime.GC()
    
    // 设置GC百分比（默认100）
    debug.SetGCPercent(50)  // 堆增长50%触发GC
    
    // 禁用GC
    debug.SetGCPercent(-1)
    
    // 获取GC统计
    var stats runtime.MemStats
    runtime.ReadMemStats(&stats)
    
    println("Alloc:", stats.Alloc)
    println("TotalAlloc:", stats.TotalAlloc)
    println("NumGC:", stats.NumGC)
}

// 三色标记法
/*
白色: 未扫描（可能是垃圾）
灰色: 已扫描，但子对象未扫描
黑色: 已扫描，且子对象已扫描（存活）

过程:
1. STW，标记根对象为灰色
2. 并发标记（写屏障保护）
3. 灰色对象变黑色，引用对象变灰色
4. 无灰色对象时，白色对象是垃圾
5. STW，清理白色对象
*/

// 减少GC压力
func optimizeGC() {
    // 1. 对象复用（sync.Pool）
    // 2. 减少指针使用
    // 3. 预分配容量
    // 4. 使用值类型
}

func main() {
    gcDemo()
}
```

---

## Go常见模式

### 11. 错误处理

**问题**: Go的错误处理最佳实践

**答案**:

```go
package main

import (
    "errors"
    "fmt"
)

// 1. 基本错误
func divide(a, b int) (int, error) {
    if b == 0 {
        return 0, errors.New("division by zero")
    }
    return a / b, nil
}

// 2. 格式化错误
func validateAge(age int) error {
    if age < 0 {
        return fmt.Errorf("invalid age: %d", age)
    }
    return nil
}

// 3. 自定义错误类型
type ValidationError struct {
    Field string
    Err   error
}

func (e *ValidationError) Error() string {
    return fmt.Sprintf("validation error on field %s: %v", e.Field, e.Err)
}

// 4. 错误包装（Go 1.13+）
func processFile(filename string) error {
    err := readFile(filename)
    if err != nil {
        return fmt.Errorf("process file %s: %w", filename, err)
    }
    return nil
}

func readFile(filename string) error {
    return errors.New("file not found")
}

// 5. 错误判断
func handleError() {
    err := processFile("test.txt")
    if err != nil {
        // 检查特定错误
        if errors.Is(err, os.ErrNotExist) {
            fmt.Println("File not found")
        }
        
        // 检查错误类型
        var valErr *ValidationError
        if errors.As(err, &valErr) {
            fmt.Println("Validation error:", valErr.Field)
        }
    }
}

// 6. panic 和 recover
func safeDivide(a, b int) (result int) {
    defer func() {
        if r := recover(); r != nil {
            fmt.Println("Recovered from:", r)
            result = 0
        }
    }()
    
    if b == 0 {
        panic("division by zero")
    }
    return a / b
}

func main() {
    // 错误处理模式
    result, err := divide(10, 2)
    if err != nil {
        fmt.Println("Error:", err)
        return
    }
    fmt.Println("Result:", result)
    
    // 链式错误
    handleError()
}
```

---

### 12. 上下文（Context）

**问题**: Context的使用场景

**答案**:

```go
package main

import (
    "context"
    "fmt"
    "time"
)

// 1. 超时控制
func timeoutDemo() {
    ctx, cancel := context.WithTimeout(context.Background(), 2*time.Second)
    defer cancel()
    
    select {
    case <-time.After(3 * time.Second):
        fmt.Println("Operation completed")
    case <-ctx.Done():
        fmt.Println("Timeout:", ctx.Err())
    }
}

// 2. 取消信号
func cancelDemo() {
    ctx, cancel := context.WithCancel(context.Background())
    
    go func() {
        select {
        case <-ctx.Done():
            fmt.Println("Goroutine canceled")
        }
    }()
    
    time.Sleep(1 * time.Second)
    cancel()  // 取消
    time.Sleep(1 * time.Second)
}

// 3. 传递值
func valueDemo() {
    type key string
    userKey := key("user")
    
    ctx := context.WithValue(context.Background(), userKey, "Alice")
    
    processRequest(ctx)
}

func processRequest(ctx context.Context) {
    type key string
    userKey := key("user")
    
    if user, ok := ctx.Value(userKey).(string); ok {
        fmt.Println("User:", user)
    }
}

// 4. HTTP请求示例
func httpRequest(ctx context.Context, url string) error {
    req, err := http.NewRequestWithContext(ctx, "GET", url, nil)
    if err != nil {
        return err
    }
    
    client := &http.Client{}
    resp, err := client.Do(req)
    if err != nil {
        return err
    }
    defer resp.Body.Close()
    
    return nil
}

// 5. 数据库查询示例
func queryWithContext(ctx context.Context) error {
    ctx, cancel := context.WithTimeout(ctx, 5*time.Second)
    defer cancel()
    
    // rows, err := db.QueryContext(ctx, "SELECT * FROM users")
    // ...
    return nil
}

func main() {
    timeoutDemo()
    cancelDemo()
    valueDemo()
}
```

---

## Go性能优化

### 13. 性能优化技巧

**问题**: Go性能优化的常见方法

**答案**:

```go
package main

import (
    "strings"
    "sync"
)

// 1. 字符串拼接优化
func stringConcat(strs []string) string {
    // 差: 多次内存分配
    result := ""
    for _, s := range strs {
        result += s
    }
    
    // 好: strings.Builder
    var builder strings.Builder
    for _, s := range strs {
        builder.WriteString(s)
    }
    return builder.String()
    
    // 最好: 预分配容量
    var builder2 strings.Builder
    builder2.Grow(100)  // 预分配
    for _, s := range strs {
        builder2.WriteString(s)
    }
    return builder2.String()
}

// 2. 切片预分配
func slicePrealloc(n int) []int {
    // 差: 多次扩容
    var s []int
    for i := 0; i < n; i++ {
        s = append(s, i)
    }
    
    // 好: 预分配容量
    s2 := make([]int, 0, n)
    for i := 0; i < n; i++ {
        s2 = append(s2, i)
    }
    return s2
}

// 3. map预分配
func mapPrealloc(n int) map[int]int {
    // 好
    m := make(map[int]int, n)
    for i := 0; i < n; i++ {
        m[i] = i
    }
    return m
}

// 4. sync.Pool 对象复用
var bufferPool = sync.Pool{
    New: func() interface{} {
        return new(bytes.Buffer)
    },
}

func usePool() {
    buf := bufferPool.Get().(*bytes.Buffer)
    defer bufferPool.Put(buf)
    
    buf.Reset()  // 重置
    buf.WriteString("Hello")
}

// 5. 避免不必要的指针
type SmallStruct struct {
    A int
    B int
}

// 小结构体用值传递
func processValue(s SmallStruct) {
    // ...
}

type LargeStruct struct {
    Data [1024]int
}

// 大结构体用指针传递
func processPointer(s *LargeStruct) {
    // ...
}

// 6. 使用sync.Once避免重复初始化
var (
    instance *Singleton
    once     sync.Once
)

type Singleton struct {
    // ...
}

func GetInstance() *Singleton {
    once.Do(func() {
        instance = &Singleton{}
    })
    return instance
}

// 7. 并发安全的缓存
type Cache struct {
    mu    sync.RWMutex
    items map[string]interface{}
}

func (c *Cache) Get(key string) (interface{}, bool) {
    c.mu.RLock()
    defer c.mu.RUnlock()
    val, ok := c.items[key]
    return val, ok
}

func (c *Cache) Set(key string, val interface{}) {
    c.mu.Lock()
    defer c.mu.Unlock()
    c.items[key] = val
}

// 8. 批量操作
func batchProcess(items []int) {
    const batchSize = 100
    
    for i := 0; i < len(items); i += batchSize {
        end := i + batchSize
        if end > len(items) {
            end = len(items)
        }
        batch := items[i:end]
        // 处理批次
        processBatch(batch)
    }
}

func processBatch(batch []int) {
    // ...
}

func main() {
    // 性能测试
    // go test -bench=. -benchmem
}
```

**基准测试**:
```go
package main

import "testing"

func BenchmarkStringConcat(b *testing.B) {
    strs := make([]string, 100)
    for i := range strs {
        strs[i] = "test"
    }
    
    b.ResetTimer()
    for i := 0; i < b.N; i++ {
        stringConcat(strs)
    }
}
```

---

## 总结

### Python面试重点

✅ **基础**: 可变/不可变、`is` vs `==`、深浅拷贝  
✅ **数据结构**: 列表推导式、生成器、装饰器  
✅ **OOP**: 类方法/静态方法、魔法方法、元类  
✅ **并发**: GIL、多线程/多进程/协程、asyncio  
✅ **高级**: 闭包、迭代器、上下文管理器  
✅ **陷阱**: 默认参数、闭包延迟绑定、浅拷贝

### Golang面试重点

✅ **基础**: 值传递/指针、defer、slice vs array  
✅ **并发**: Goroutine、Channel、select、sync包  
✅ **接口**: 隐式实现、类型断言、组合  
✅ **内存**: 逃逸分析、GC机制  
✅ **模式**: 错误处理、Context  
✅ **优化**: 预分配、sync.Pool、并发安全

---

**准备建议**:
1. **手写代码**: 不要只看，要亲自写
2. **理解原理**: 知其然，知其所以然
3. **实战经验**: 结合项目经历讲述
4. **性能意识**: 关注时间/空间复杂度
5. **最佳实践**: 了解社区推荐做法

**推荐资源**:
- Python: 《Fluent Python》《Effective Python》
- Golang: 《The Go Programming Language》《Go语言高级编程》
- Shell: 《Linux命令行与Shell脚本编程大全》
- Node.js: 《深入浅出Node.js》《Node.js设计模式》
- Vue.js: 《Vue.js设计与实现》官方文档
- 在线练习: LeetCode、牛客网、力扣

---

# Shell篇

## Shell基础

### 1. Shell变量与引号

**问题**: 单引号、双引号、反引号的区别

**答案**:

```bash
#!/bin/bash

# 单引号 - 字面值，不解析变量
name='World'
echo 'Hello $name'  # 输出: Hello $name

# 双引号 - 解析变量和转义字符
echo "Hello $name"  # 输出: Hello World
echo "Line1\nLine2" # 输出: Line1\nLine2 (需要 echo -e)

# 反引号 - 命令替换（已过时）
result=`ls -l`

# $() - 命令替换（推荐）
result=$(ls -l)
count=$(echo $result | wc -l)

# 数组
arr=(1 2 3 4 5)
echo ${arr[0]}      # 第一个元素
echo ${arr[@]}      # 所有元素
echo ${#arr[@]}     # 数组长度

# 字符串操作
str="Hello World"
echo ${str:0:5}     # Hello (截取)
echo ${str/World/Bash}  # Hello Bash (替换)
echo ${#str}        # 11 (长度)

# 变量默认值
echo ${var:-default}    # 如果var为空，返回default
echo ${var:=default}    # 如果var为空，赋值并返回default
echo ${var:?error}      # 如果var为空，输出error并退出
```

**常见陷阱**:
```bash
# 陷阱1: 空格敏感
var=value   # ✓ 正确
var = value # ✗ 错误（会被解释为命令）

# 陷阱2: 变量未加引号
file="my file.txt"
rm $file    # ✗ 删除 my 和 file.txt 两个文件
rm "$file"  # ✓ 删除 my file.txt

# 陷阱3: 比较运算
[ $a = $b ]   # 字符串比较
[ $a -eq $b ] # 数值比较
```

---

### 2. 条件判断与测试

**问题**: 实现文件检查和字符串比较

**答案**:

```bash
#!/bin/bash

# 文件测试
file="/etc/passwd"

if [ -f "$file" ]; then
    echo "File exists"
fi

# 常用文件测试
[ -e file ]  # 文件存在
[ -f file ]  # 普通文件
[ -d file ]  # 目录
[ -r file ]  # 可读
[ -w file ]  # 可写
[ -x file ]  # 可执行
[ -s file ]  # 文件非空
[ file1 -nt file2 ]  # file1 比 file2 新
[ file1 -ot file2 ]  # file1 比 file2 旧

# 字符串测试
str1="hello"
str2="world"

[ -z "$str" ]        # 字符串为空
[ -n "$str" ]        # 字符串非空
[ "$str1" = "$str2" ]   # 相等
[ "$str1" != "$str2" ]  # 不等

# 数值比较
a=10
b=20

[ $a -eq $b ]  # 等于
[ $a -ne $b ]  # 不等于
[ $a -lt $b ]  # 小于
[ $a -le $b ]  # 小于等于
[ $a -gt $b ]  # 大于
[ $a -ge $b ]  # 大于等于

# 逻辑运算
[ $a -lt 20 ] && [ $a -gt 5 ]   # AND
[ $a -lt 5 ] || [ $a -gt 15 ]   # OR
[ ! -f file ]                    # NOT

# [[ ]] 增强测试（推荐）
[[ $str =~ ^[0-9]+$ ]]  # 正则匹配
[[ $a < $b ]]           # 字符串比较
[[ $str1 == hello* ]]   # 模式匹配

# case 语句
case "$1" in
    start)
        echo "Starting..."
        ;;
    stop)
        echo "Stopping..."
        ;;
    restart)
        echo "Restarting..."
        ;;
    *)
        echo "Usage: $0 {start|stop|restart}"
        exit 1
        ;;
esac
```

---

### 3. 循环与迭代

**问题**: 实现各种循环

**答案**:

```bash
#!/bin/bash

# for 循环 - C风格
for ((i=0; i<10; i++)); do
    echo $i
done

# for 循环 - 列表
for item in apple banana orange; do
    echo $item
done

# for 循环 - 文件
for file in *.txt; do
    echo "Processing $file"
done

# for 循环 - 命令输出
for user in $(cat /etc/passwd | cut -d: -f1); do
    echo "User: $user"
done

# while 循环
count=0
while [ $count -lt 5 ]; do
    echo $count
    ((count++))
done

# until 循环
count=0
until [ $count -ge 5 ]; do
    echo $count
    ((count++))
done

# 读取文件（推荐方式）
while IFS= read -r line; do
    echo "$line"
done < file.txt

# 读取文件（处理每个字段）
while IFS=: read -r username password uid gid; do
    echo "User: $username, UID: $uid"
done < /etc/passwd

# break 和 continue
for i in {1..10}; do
    if [ $i -eq 5 ]; then
        continue  # 跳过5
    fi
    if [ $i -eq 8 ]; then
        break     # 在8处停止
    fi
    echo $i
done
```

---

## Shell文本处理

### 4. grep, sed, awk 三剑客

**问题**: 使用grep、sed、awk处理文本

**答案**:

```bash
#!/bin/bash

# ========== grep ==========
# 基本搜索
grep "pattern" file.txt

# 常用选项
grep -i "pattern" file.txt    # 忽略大小写
grep -v "pattern" file.txt    # 反向匹配（不包含）
grep -n "pattern" file.txt    # 显示行号
grep -c "pattern" file.txt    # 计数
grep -r "pattern" /path       # 递归搜索
grep -E "pattern1|pattern2"   # 扩展正则（或）
grep -A 3 "pattern" file      # 显示匹配行及后3行
grep -B 3 "pattern" file      # 显示匹配行及前3行
grep -C 3 "pattern" file      # 显示匹配行及前后3行

# 正则表达式
grep "^start" file            # 行首匹配
grep "end$" file              # 行尾匹配
grep "^$" file                # 空行
grep "[0-9]\{3\}" file        # 3个数字
grep -E "[0-9]{3}" file       # 扩展正则

# ========== sed ==========
# 替换
sed 's/old/new/' file             # 替换每行第一个
sed 's/old/new/g' file            # 替换所有
sed 's/old/new/2' file            # 替换每行第二个
sed -i 's/old/new/g' file         # 直接修改文件

# 删除
sed '3d' file                     # 删除第3行
sed '3,5d' file                   # 删除3-5行
sed '/pattern/d' file             # 删除匹配行

# 插入和追加
sed '3i\new line' file            # 在第3行前插入
sed '3a\new line' file            # 在第3行后追加

# 打印
sed -n '3p' file                  # 只打印第3行
sed -n '/pattern/p' file          # 只打印匹配行
sed -n '3,5p' file                # 打印3-5行

# 多个命令
sed -e 's/old/new/g' -e 's/foo/bar/g' file
sed 's/old/new/g; s/foo/bar/g' file

# ========== awk ==========
# 基本用法
awk '{print $1}' file             # 打印第一列
awk '{print $1, $3}' file         # 打印第1和第3列
awk '{print $NF}' file            # 打印最后一列

# 条件过滤
awk '$3 > 100' file               # 第3列大于100
awk '/pattern/' file              # 包含pattern的行
awk '$1 == "admin"' file          # 第1列等于admin

# 指定分隔符
awk -F: '{print $1}' /etc/passwd  # 以冒号分隔
awk 'BEGIN{FS=":"} {print $1}' /etc/passwd

# BEGIN 和 END
awk 'BEGIN{print "Start"} {print $0} END{print "End"}' file

# 内置变量
awk '{print NR, NF, $0}' file     # NR=行号, NF=字段数, $0=整行

# 计算
awk '{sum+=$3} END{print sum}' file        # 求和
awk '{sum+=$3; count++} END{print sum/count}' file  # 平均值

# 格式化输出
awk '{printf "%-10s %5d\n", $1, $2}' file

# 复杂示例：统计访问日志
# 统计每个IP的访问次数
awk '{ip[$1]++} END{for(i in ip) print i, ip[i]}' access.log | sort -k2 -nr

# 统计HTTP状态码分布
awk '{status[$9]++} END{for(s in status) print s, status[s]}' access.log
```

---

### 5. 文本处理实战

**问题**: 处理日志文件、CSV文件

**答案**:

```bash
#!/bin/bash

# 1. 提取日志中的IP地址
grep -oE '\b([0-9]{1,3}\.){3}[0-9]{1,3}\b' access.log | sort | uniq -c | sort -nr

# 2. 统计日志中最常见的URL
awk '{print $7}' access.log | sort | uniq -c | sort -nr | head -10

# 3. 找出最大的10个文件
find . -type f -exec du -h {} \; | sort -rh | head -10

# 4. CSV处理
# 提取CSV第2列
awk -F, '{print $2}' data.csv

# 过滤CSV（第3列大于100）
awk -F, '$3 > 100' data.csv

# CSV转JSON
awk -F, 'NR>1{printf "{\"name\":\"%s\",\"age\":%s}\n", $1, $2}' data.csv

# 5. 批量重命名
# 将所有.txt改为.log
for file in *.txt; do
    mv "$file" "${file%.txt}.log"
done

# 6. 提取所有邮箱地址
grep -oE '\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b' file.txt

# 7. 查找重复行
sort file.txt | uniq -d

# 8. 删除重复行（保留一个）
sort file.txt | uniq

# 9. 合并多个文件并去重
cat file1.txt file2.txt file3.txt | sort | uniq > merged.txt

# 10. 按第2列排序
sort -k2 -n file.txt  # 数值排序
sort -k2 file.txt     # 字符串排序
```

---

## Shell脚本编程

### 6. 函数与参数

**问题**: 实现可复用的Shell函数

**答案**:

```bash
#!/bin/bash

# 基本函数
function greet() {
    echo "Hello, $1!"
}

# 或
greet() {
    echo "Hello, $1!"
}

greet "World"  # Hello, World!

# 函数参数
function sum() {
    local result=$(($1 + $2))
    echo $result
}

result=$(sum 10 20)
echo "Sum: $result"  # Sum: 30

# 返回值
function is_even() {
    if [ $(($1 % 2)) -eq 0 ]; then
        return 0  # 成功（偶数）
    else
        return 1  # 失败（奇数）
    fi
}

if is_even 4; then
    echo "4 is even"
fi

# 局部变量
function test_scope() {
    local local_var="local"
    global_var="global"
    echo $local_var
}

test_scope
# echo $local_var  # 错误：未定义
echo $global_var   # global

# 特殊参数
function show_params() {
    echo "Script name: $0"
    echo "First param: $1"
    echo "Second param: $2"
    echo "All params: $@"
    echo "All params: $*"
    echo "Param count: $#"
    echo "Last exit code: $?"
    echo "Current PID: $$"
}

show_params arg1 arg2 arg3

# shift - 移动参数
function process_all() {
    while [ $# -gt 0 ]; do
        echo "Processing: $1"
        shift
    done
}

process_all a b c d

# 数组作为参数
function sum_array() {
    local arr=("$@")
    local sum=0
    for num in "${arr[@]}"; do
        ((sum += num))
    done
    echo $sum
}

numbers=(1 2 3 4 5)
total=$(sum_array "${numbers[@]}")
echo "Total: $total"  # Total: 15
```

---

### 7. 错误处理与调试

**问题**: 实现健壮的错误处理

**答案**:

```bash
#!/bin/bash

# 1. set 选项
set -e  # 遇到错误立即退出
set -u  # 使用未定义变量时报错
set -o pipefail  # 管道中任何命令失败都返回失败
set -x  # 打印执行的命令（调试）

# 组合使用
set -euo pipefail

# 2. 错误处理
function safe_command() {
    if ! command -v git &> /dev/null; then
        echo "Error: git is not installed" >&2
        exit 1
    fi
}

# 3. trap - 捕获信号
cleanup() {
    echo "Cleaning up..."
    rm -f /tmp/tempfile
}

trap cleanup EXIT  # 脚本退出时清理
trap 'echo "CTRL+C pressed"' INT  # 捕获CTRL+C

# 4. 错误日志
log_error() {
    echo "[ERROR] $(date '+%Y-%m-%d %H:%M:%S') $1" >&2
}

log_info() {
    echo "[INFO] $(date '+%Y-%m-%d %H:%M:%S') $1"
}

# 使用
if ! grep "pattern" file.txt; then
    log_error "Pattern not found"
    exit 1
fi

# 5. 带重试的命令执行
retry() {
    local max_attempts=$1
    shift
    local cmd="$@"
    local attempt=1
    
    until $cmd; do
        if [ $attempt -ge $max_attempts ]; then
            echo "Command failed after $max_attempts attempts"
            return 1
        fi
        echo "Attempt $attempt failed, retrying..."
        ((attempt++))
        sleep 2
    done
}

# 使用
retry 3 curl https://example.com

# 6. 检查命令是否成功
if ! mkdir /tmp/mydir 2>/dev/null; then
    echo "Failed to create directory"
fi

# 或
mkdir /tmp/mydir || { echo "Failed"; exit 1; }

# 7. 调试技巧
# 在脚本顶部添加
if [ "${DEBUG:-0}" = "1" ]; then
    set -x
fi

# 运行: DEBUG=1 ./script.sh

# 8. 完整示例
#!/bin/bash
set -euo pipefail

readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly LOG_FILE="/var/log/myscript.log"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG_FILE"
}

error_exit() {
    log "ERROR: $1"
    exit "${2:-1}"
}

cleanup() {
    log "Cleaning up..."
    # 清理代码
}

trap cleanup EXIT
trap 'error_exit "Script interrupted"' INT TERM

main() {
    log "Script started"
    
    # 主逻辑
    if ! some_command; then
        error_exit "Command failed"
    fi
    
    log "Script completed successfully"
}

main "$@"
```

---

### 8. 进程与系统管理

**问题**: 进程管理和系统监控

**答案**:

```bash
#!/bin/bash

# 1. 后台运行
command &             # 后台运行
nohup command &       # 后台运行，忽略HUP信号
nohup command > /dev/null 2>&1 &  # 后台运行，丢弃输出

# 2. 等待后台进程
command1 &
pid1=$!
command2 &
pid2=$!

wait $pid1
wait $pid2
# 或
wait  # 等待所有后台进程

# 3. 检查进程是否存在
if pgrep -x "nginx" > /dev/null; then
    echo "Nginx is running"
else
    echo "Nginx is not running"
fi

# 4. 杀死进程
pkill -f "process_name"
killall process_name

# 优雅停止
kill -TERM $pid
sleep 5
kill -KILL $pid

# 5. 监控资源
# CPU使用率最高的10个进程
ps aux | sort -nrk 3,3 | head -n 10

# 内存使用率最高的10个进程
ps aux | sort -nrk 4,4 | head -n 10

# 6. 检查磁盘空间
df -h | awk '$5+0 > 80 {print $0}'  # 使用率超过80%的分区

# 7. 监控日志文件
tail -f /var/log/syslog | grep --line-buffered "ERROR"

# 8. 定时任务（cron）
# 每天凌晨2点执行
# 0 2 * * * /path/to/script.sh

# 9. 系统信息
uptime                    # 系统运行时间和负载
free -h                   # 内存使用
df -h                     # 磁盘使用
iostat                    # I/O统计
netstat -tunlp            # 网络连接

# 10. 完整监控脚本
#!/bin/bash

THRESHOLD=80
EMAIL="admin@example.com"

check_disk() {
    df -h | awk -v threshold=$THRESHOLD '
        NR>1 && $5+0 > threshold {
            printf "WARNING: %s is %s full\n", $6, $5
        }'
}

check_memory() {
    free | awk 'NR==2 {
        used=$3; total=$2; pct=used*100/total;
        if(pct > '$THRESHOLD') {
            printf "WARNING: Memory usage is %.0f%%\n", pct
        }
    }'
}

check_cpu() {
    load=$(uptime | awk -F'load average:' '{print $2}' | awk '{print $1}' | sed 's/,//')
    if (( $(echo "$load > 2.0" | bc -l) )); then
        echo "WARNING: High CPU load: $load"
    fi
}

main() {
    {
        check_disk
        check_memory
        check_cpu
    } | tee /tmp/health_check.log
}

main
```

---

## Shell常见实战

### 9. 实用脚本示例

**问题**: 编写实用的运维脚本

**答案**:

```bash
# 1. 备份脚本
#!/bin/bash
set -euo pipefail

BACKUP_DIR="/backup"
SOURCE_DIR="/var/www"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/backup_$DATE.tar.gz"

# 创建备份
tar -czf "$BACKUP_FILE" "$SOURCE_DIR"

# 删除7天前的备份
find "$BACKUP_DIR" -name "backup_*.tar.gz" -mtime +7 -delete

echo "Backup completed: $BACKUP_FILE"

# 2. 日志轮转脚本
#!/bin/bash

LOG_FILE="/var/log/myapp.log"
MAX_SIZE=$((10 * 1024 * 1024))  # 10MB

if [ -f "$LOG_FILE" ]; then
    size=$(stat -f%z "$LOG_FILE" 2>/dev/null || stat -c%s "$LOG_FILE")
    
    if [ $size -gt $MAX_SIZE ]; then
        timestamp=$(date +%Y%m%d_%H%M%S)
        mv "$LOG_FILE" "${LOG_FILE}.$timestamp"
        gzip "${LOG_FILE}.$timestamp"
        touch "$LOG_FILE"
        echo "Log rotated"
    fi
fi

# 3. 服务健康检查
#!/bin/bash

check_service() {
    local service=$1
    local port=$2
    
    if nc -z localhost $port 2>/dev/null; then
        echo "✓ $service is running on port $port"
        return 0
    else
        echo "✗ $service is not responding on port $port"
        return 1
    fi
}

check_service "Nginx" 80
check_service "MySQL" 3306
check_service "Redis" 6379

# 4. 批量创建用户
#!/bin/bash

while IFS=, read -r username password; do
    if id "$username" &>/dev/null; then
        echo "User $username already exists"
    else
        useradd -m -s /bin/bash "$username"
        echo "$username:$password" | chpasswd
        echo "Created user: $username"
    fi
done < users.csv

# 5. 文件同步脚本
#!/bin/bash

SOURCE="/data/source"
DEST="/data/backup"
LOG="/var/log/sync.log"

rsync -avz --delete \
    --exclude '*.tmp' \
    --exclude '.cache' \
    "$SOURCE/" "$DEST/" \
    >> "$LOG" 2>&1

if [ $? -eq 0 ]; then
    echo "$(date): Sync completed successfully" >> "$LOG"
else
    echo "$(date): Sync failed" >> "$LOG"
fi

# 6. 端口扫描
#!/bin/bash

host=$1
start_port=${2:-1}
end_port=${3:-1024}

for port in $(seq $start_port $end_port); do
    timeout 1 bash -c "echo >/dev/tcp/$host/$port" 2>/dev/null &&
        echo "Port $port is open"
done

# 7. Git 仓库批量更新
#!/bin/bash

REPOS_DIR="/home/user/repos"

for repo in "$REPOS_DIR"/*; do
    if [ -d "$repo/.git" ]; then
        echo "Updating $(basename $repo)..."
        cd "$repo"
        git pull
    fi
done

# 8. 配置文件模板替换
#!/bin/bash

# template.conf:
# server_name = {{SERVER_NAME}}
# port = {{PORT}}

SERVER_NAME="myapp.com"
PORT="8080"

sed -e "s/{{SERVER_NAME}}/$SERVER_NAME/g" \
    -e "s/{{PORT}}/$PORT/g" \
    template.conf > app.conf
```

---

# Node.js篇

## Node.js基础

### 1. 事件循环（Event Loop）

**问题**: 解释Node.js的事件循环机制

**答案**:

**事件循环阶段**:
```
   ┌───────────────────────────┐
┌─>│           timers          │  setTimeout/setInterval
│  └─────────────┬─────────────┘
│  ┌─────────────┴─────────────┐
│  │     pending callbacks     │  I/O回调（除了close、timers、check）
│  └─────────────┬─────────────┘
│  ┌─────────────┴─────────────┐
│  │       idle, prepare       │  内部使用
│  └─────────────┬─────────────┘
│  ┌─────────────┴─────────────┐
│  │           poll            │  轮询I/O事件
│  └─────────────┬─────────────┘
│  ┌─────────────┴─────────────┐
│  │           check           │  setImmediate
│  └─────────────┬─────────────┘
│  ┌─────────────┴─────────────┐
└──┤      close callbacks      │  close事件回调
   └───────────────────────────┘
```

```javascript
// 微任务 vs 宏任务
console.log('1');

setTimeout(() => {
    console.log('2');  // 宏任务（timers阶段）
}, 0);

Promise.resolve().then(() => {
    console.log('3');  // 微任务（process.nextTick之后）
});

process.nextTick(() => {
    console.log('4');  // 微任务（最高优先级）
});

setImmediate(() => {
    console.log('5');  // 宏任务（check阶段）
});

console.log('6');

// 输出: 1 6 4 3 2 5

// 详细示例
setTimeout(() => console.log('timeout1'), 0);
setImmediate(() => console.log('immediate1'));

Promise.resolve().then(() => {
    console.log('promise1');
    process.nextTick(() => console.log('nextTick1'));
});

process.nextTick(() => {
    console.log('nextTick2');
    process.nextTick(() => console.log('nextTick3'));
});

// 输出顺序:
// nextTick2
// nextTick3
// promise1
// nextTick1
// timeout1
// immediate1

// 优先级: process.nextTick > Promise > setTimeout > setImmediate
```

**关键点**:
- **同步代码**先执行
- **process.nextTick**优先于Promise
- **微任务**在每个阶段之间执行
- **setTimeout vs setImmediate**顺序不确定（在I/O回调中setImmediate优先）

---

### 2. 模块系统

**问题**: CommonJS vs ES Modules

**答案**:

```javascript
// ========== CommonJS (CJS) ==========
// math.js
function add(a, b) {
    return a + b;
}

function subtract(a, b) {
    return a - b;
}

module.exports = {
    add,
    subtract
};

// 或单个导出
module.exports = add;

// 使用
const math = require('./math');
console.log(math.add(1, 2));

// 解构导入
const { add, subtract } = require('./math');

// ========== ES Modules (ESM) ==========
// math.mjs
export function add(a, b) {
    return a + b;
}

export function subtract(a, b) {
    return a - b;
}

// 默认导出
export default function multiply(a, b) {
    return a * b;
}

// 使用
import { add, subtract } from './math.mjs';
import multiply from './math.mjs';

// 导入所有
import * as math from './math.mjs';

// 对比
/*
| 特性 | CommonJS | ES Modules |
|-----|----------|-----------|
| 语法 | require/module.exports | import/export |
| 加载 | 同步 | 异步 |
| 时机 | 运行时 | 编译时 |
| 导入 | 动态（可在条件中） | 静态（顶层） |
| this | 指向module.exports | undefined |
| 文件扩展名 | .js | .mjs 或 package.json设置 |
*/

// package.json 配置 ES Modules
{
    "type": "module"
}

// 循环依赖
// a.js
const b = require('./b');
console.log('a:', b);
module.exports = 'a';

// b.js
const a = require('./a');
console.log('b:', a);  // b: {}  (未完成加载)
module.exports = 'b';

// 内置模块
const fs = require('fs');
const path = require('path');
const http = require('http');

// ESM导入内置模块
import fs from 'fs';
import { readFile } from 'fs/promises';
```

---

### 3. 异步编程演进

**问题**: Callback -> Promise -> Async/Await

**答案**:

```javascript
// 1. Callback（回调地狱）
fs.readFile('file1.txt', 'utf8', (err, data1) => {
    if (err) return console.error(err);
    fs.readFile('file2.txt', 'utf8', (err, data2) => {
        if (err) return console.error(err);
        fs.readFile('file3.txt', 'utf8', (err, data3) => {
            if (err) return console.error(err);
            console.log(data1 + data2 + data3);
        });
    });
});

// 2. Promise
const readFilePromise = (filename) => {
    return new Promise((resolve, reject) => {
        fs.readFile(filename, 'utf8', (err, data) => {
            if (err) reject(err);
            else resolve(data);
        });
    });
};

readFilePromise('file1.txt')
    .then(data1 => readFilePromise('file2.txt'))
    .then(data2 => readFilePromise('file3.txt'))
    .then(data3 => console.log(data3))
    .catch(err => console.error(err));

// Promise.all - 并行
Promise.all([
    readFilePromise('file1.txt'),
    readFilePromise('file2.txt'),
    readFilePromise('file3.txt')
])
.then(([data1, data2, data3]) => {
    console.log(data1 + data2 + data3);
})
.catch(err => console.error(err));

// 3. Async/Await
const readFiles = async () => {
    try {
        const data1 = await readFilePromise('file1.txt');
        const data2 = await readFilePromise('file2.txt');
        const data3 = await readFilePromise('file3.txt');
        console.log(data1 + data2 + data3);
    } catch (err) {
        console.error(err);
    }
};

// 并行
const readFilesParallel = async () => {
    try {
        const [data1, data2, data3] = await Promise.all([
            readFilePromise('file1.txt'),
            readFilePromise('file2.txt'),
            readFilePromise('file3.txt')
        ]);
        console.log(data1 + data2 + data3);
    } catch (err) {
        console.error(err);
    }
};

// util.promisify - 将callback转为Promise
const util = require('util');
const readFileAsync = util.promisify(fs.readFile);

const data = await readFileAsync('file.txt', 'utf8');

// fs.promises - 内置Promise API
const { readFile } = require('fs/promises');
const data = await readFile('file.txt', 'utf8');

// 错误处理
async function fetchData() {
    try {
        const response = await fetch('https://api.example.com/data');
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Error fetching data:', error);
        throw error;
    }
}

// Promise 高级用法
// Promise.race - 竞速
const timeout = (ms) => new Promise((_, reject) => 
    setTimeout(() => reject(new Error('Timeout')), ms)
);

Promise.race([
    fetch('https://slow-api.com'),
    timeout(5000)
])
.then(res => console.log('Success'))
.catch(err => console.error('Timeout or error'));

// Promise.allSettled - 等待所有（不管成功失败）
const results = await Promise.allSettled([
    Promise.resolve(1),
    Promise.reject('error'),
    Promise.resolve(3)
]);
// [
//   { status: 'fulfilled', value: 1 },
//   { status: 'rejected', reason: 'error' },
//   { status: 'fulfilled', value: 3 }
// ]
```

---

## Node.js进阶

### 4. Stream 流

**问题**: 使用Stream处理大文件

**答案**:

```javascript
const fs = require('fs');
const { Transform, pipeline } = require('stream');

// 1. 读取流
const readStream = fs.createReadStream('large-file.txt', {
    encoding: 'utf8',
    highWaterMark: 16 * 1024  // 缓冲区大小 16KB
});

readStream.on('data', (chunk) => {
    console.log('Received chunk:', chunk.length);
});

readStream.on('end', () => {
    console.log('Finished reading');
});

readStream.on('error', (err) => {
    console.error('Error:', err);
});

// 2. 写入流
const writeStream = fs.createWriteStream('output.txt');

writeStream.write('Line 1\n');
writeStream.write('Line 2\n');
writeStream.end('Last line\n');

// 3. 管道（pipe）
fs.createReadStream('input.txt')
    .pipe(fs.createWriteStream('output.txt'));

// 4. Transform 流
class UpperCaseTransform extends Transform {
    _transform(chunk, encoding, callback) {
        this.push(chunk.toString().toUpperCase());
        callback();
    }
}

fs.createReadStream('input.txt')
    .pipe(new UpperCaseTransform())
    .pipe(fs.createWriteStream('output.txt'));

// 5. pipeline - 处理错误
const { pipeline } = require('stream/promises');

async function processFile() {
    await pipeline(
        fs.createReadStream('input.txt'),
        new UpperCaseTransform(),
        fs.createWriteStream('output.txt')
    );
}

processFile().catch(console.error);

// 6. 实用示例：CSV处理
const csv = require('csv-parser');

fs.createReadStream('data.csv')
    .pipe(csv())
    .on('data', (row) => {
        console.log(row);
    })
    .on('end', () => {
        console.log('CSV file processed');
    });

// 7. 压缩文件
const zlib = require('zlib');

fs.createReadStream('input.txt')
    .pipe(zlib.createGzip())
    .pipe(fs.createWriteStream('input.txt.gz'));

// 8. HTTP响应流
const http = require('http');

http.createServer((req, res) => {
    fs.createReadStream('large-file.txt')
        .pipe(res);  // 直接流式传输，不占用内存
}).listen(3000);

// 9. 背压（Backpressure）处理
const readable = fs.createReadStream('input.txt');
const writable = fs.createWriteStream('output.txt');

readable.on('data', (chunk) => {
    const canContinue = writable.write(chunk);
    if (!canContinue) {
        readable.pause();  // 暂停读取
    }
});

writable.on('drain', () => {
    readable.resume();  // 恢复读取
});
```

---

### 5. Buffer 和内存管理

**问题**: Buffer的使用和内存优化

**答案**:

```javascript
// 1. 创建Buffer
const buf1 = Buffer.alloc(10);  // 分配10字节，填充0
const buf2 = Buffer.allocUnsafe(10);  // 不初始化（更快但不安全）
const buf3 = Buffer.from([1, 2, 3]);
const buf4 = Buffer.from('Hello', 'utf8');

// 2. 写入和读取
const buf = Buffer.alloc(10);
buf.write('Hello');
console.log(buf.toString());  // Hello

// 写入数值
buf.writeUInt8(255, 0);  // 在偏移0处写入
buf.writeUInt16BE(1000, 1);  // 在偏移1处写入16位大端序

// 读取
const value = buf.readUInt8(0);

// 3. Buffer 拼接
const buf1 = Buffer.from('Hello ');
const buf2 = Buffer.from('World');
const buf3 = Buffer.concat([buf1, buf2]);
console.log(buf3.toString());  // Hello World

// 4. Buffer 转换
// Buffer to String
const str = buf.toString('utf8');
const hex = buf.toString('hex');
const base64 = buf.toString('base64');

// String to Buffer
const buf = Buffer.from(str, 'utf8');

// 5. 内存泄漏预防
// 错误示例
const leaks = [];
setInterval(() => {
    leaks.push(new Buffer(1024 * 1024));  // 内存泄漏！
}, 100);

// 正确示例
const objectPool = [];
function getObject() {
    return objectPool.pop() || createNewObject();
}

function releaseObject(obj) {
    objectPool.push(obj);
}

// 6. 内存监控
console.log(process.memoryUsage());
/*
{
  rss: 物理内存占用
  heapTotal: 堆总大小
  heapUsed: 堆已使用
  external: C++对象绑定的内存
  arrayBuffers: ArrayBuffer和SharedArrayBuffer
}
*/

// 7. V8堆大小限制
// 默认: 64位系统约1.4GB
// 增加限制: node --max-old-space-size=4096 app.js

// 8. WeakMap/WeakSet - 避免内存泄漏
const cache = new WeakMap();

function process(obj) {
    if (!cache.has(obj)) {
        const result = expensiveOperation(obj);
        cache.set(obj, result);
    }
    return cache.get(obj);
}
```

---

### 6. 集群（Cluster）和进程管理

**问题**: 实现多进程负载均衡

**答案**:

```javascript
// cluster.js
const cluster = require('cluster');
const http = require('http');
const numCPUs = require('os').cpus().length;

if (cluster.isMaster) {
    console.log(`Master ${process.pid} is running`);
    
    // Fork workers
    for (let i = 0; i < numCPUs; i++) {
        cluster.fork();
    }
    
    cluster.on('exit', (worker, code, signal) => {
        console.log(`Worker ${worker.process.pid} died`);
        // 重启工作进程
        cluster.fork();
    });
    
    // 向所有worker发送消息
    Object.values(cluster.workers).forEach(worker => {
        worker.send('Hello from master');
    });
    
} else {
    // Worker进程
    http.createServer((req, res) => {
        res.writeHead(200);
        res.end(`Hello from worker ${process.pid}\n`);
    }).listen(8000);
    
    console.log(`Worker ${process.pid} started`);
    
    // 接收主进程消息
    process.on('message', (msg) => {
        console.log(`Worker ${process.pid} received: ${msg}`);
    });
}

// 优雅退出
process.on('SIGTERM', () => {
    console.log('SIGTERM received');
    server.close(() => {
        console.log('Server closed');
        process.exit(0);
    });
});

// 使用PM2管理进程
/*
// ecosystem.config.js
module.exports = {
    apps: [{
        name: 'app',
        script: './app.js',
        instances: 'max',  // 或具体数字
        exec_mode: 'cluster',
        max_memory_restart: '1G',
        env: {
            NODE_ENV: 'production'
        }
    }]
};

// 启动
pm2 start ecosystem.config.js

// 监控
pm2 monit

// 重启
pm2 reload app

// 停止
pm2 stop app
*/

// Child Process
const { spawn, exec, fork } = require('child_process');

// spawn - 流式输出
const ls = spawn('ls', ['-lh', '/usr']);

ls.stdout.on('data', (data) => {
    console.log(`stdout: ${data}`);
});

ls.stderr.on('data', (data) => {
    console.error(`stderr: ${data}`);
});

ls.on('close', (code) => {
    console.log(`child process exited with code ${code}`);
});

// exec - 缓冲输出
exec('ls -lh /usr', (error, stdout, stderr) => {
    if (error) {
        console.error(`error: ${error}`);
        return;
    }
    console.log(`stdout: ${stdout}`);
});

// fork - Node进程间通信
// parent.js
const child = fork('child.js');

child.on('message', (msg) => {
    console.log('Message from child:', msg);
});

child.send({ hello: 'world' });

// child.js
process.on('message', (msg) => {
    console.log('Message from parent:', msg);
    process.send({ received: true });
});
```

---

## Node.js Web开发

### 7. Express 框架

**问题**: Express的中间件和路由

**答案**:

```javascript
const express = require('express');
const app = express();

// 1. 中间件
// 内置中间件
app.use(express.json());  // 解析JSON
app.use(express.urlencoded({ extended: true }));  // 解析URL编码
app.use(express.static('public'));  // 静态文件

// 自定义中间件
app.use((req, res, next) => {
    console.log(`${req.method} ${req.url}`);
    req.requestTime = Date.now();
    next();
});

// 错误处理中间件
app.use((err, req, res, next) => {
    console.error(err.stack);
    res.status(500).send('Something broke!');
});

// 2. 路由
app.get('/', (req, res) => {
    res.send('Hello World');
});

app.post('/users', (req, res) => {
    const user = req.body;
    res.json({ success: true, user });
});

// 路由参数
app.get('/users/:id', (req, res) => {
    const { id } = req.params;
    res.json({ userId: id });
});

// 查询参数
app.get('/search', (req, res) => {
    const { q, page } = req.query;
    res.json({ query: q, page });
});

// 3. 路由模块化
// routes/users.js
const router = express.Router();

router.get('/', (req, res) => {
    res.json({ users: [] });
});

router.post('/', (req, res) => {
    res.json({ created: true });
});

router.get('/:id', (req, res) => {
    res.json({ userId: req.params.id });
});

module.exports = router;

// app.js
app.use('/api/users', require('./routes/users'));

// 4. 中间件链
const auth = (req, res, next) => {
    const token = req.headers.authorization;
    if (!token) {
        return res.status(401).json({ error: 'No token' });
    }
    // 验证token
    next();
};

const adminOnly = (req, res, next) => {
    if (!req.user.isAdmin) {
        return res.status(403).json({ error: 'Admin only' });
    }
    next();
};

app.delete('/users/:id', auth, adminOnly, (req, res) => {
    res.json({ deleted: true });
});

// 5. 异步错误处理
const asyncHandler = (fn) => (req, res, next) => {
    Promise.resolve(fn(req, res, next)).catch(next);
};

app.get('/users', asyncHandler(async (req, res) => {
    const users = await User.find();
    res.json(users);
}));

// 6. 请求验证
const { body, validationResult } = require('express-validator');

app.post('/users',
    body('email').isEmail(),
    body('password').isLength({ min: 6 }),
    (req, res) => {
        const errors = validationResult(req);
        if (!errors.isEmpty()) {
            return res.status(400).json({ errors: errors.array() });
        }
        res.json({ success: true });
    }
);

// 7. 完整示例
const express = require('express');
const morgan = require('morgan');
const helmet = require('helmet');
const cors = require('cors');

const app = express();

// 安全
app.use(helmet());
app.use(cors());

// 日志
app.use(morgan('combined'));

// 解析
app.use(express.json());

// 路由
app.use('/api/users', require('./routes/users'));
app.use('/api/posts', require('./routes/posts'));

// 404
app.use((req, res) => {
    res.status(404).json({ error: 'Not found' });
});

// 错误处理
app.use((err, req, res, next) => {
    console.error(err);
    res.status(err.status || 500).json({
        error: err.message || 'Internal server error'
    });
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
    console.log(`Server running on port ${PORT}`);
});
```

---

# Vue.js篇

## Vue.js基础

### 1. 响应式原理

**问题**: Vue 2和Vue 3的响应式实现

**答案**:

```javascript
// ========== Vue 2 - Object.defineProperty ==========
function defineReactive(obj, key, val) {
    const dep = [];  // 依赖收集
    
    Object.defineProperty(obj, key, {
        get() {
            console.log('get', key);
            // 收集依赖
            if (Dep.target) {
                dep.push(Dep.target);
            }
            return val;
        },
        set(newVal) {
            if (newVal === val) return;
            console.log('set', key, newVal);
            val = newVal;
            // 通知更新
            dep.forEach(watcher => watcher.update());
        }
    });
}

const data = {};
defineReactive(data, 'name', 'Alice');

// 局限性
// 1. 无法检测属性的添加和删除
const obj = { a: 1 };
obj.b = 2;  // 不是响应式

// 需要使用
Vue.set(obj, 'b', 2);
this.$set(this.obj, 'b', 2);

// 2. 无法检测数组索引和长度的变化
arr[0] = 100;  // 不是响应式
arr.length = 0;  // 不是响应式

// Vue 2 重写了数组方法
const arrayMethods = ['push', 'pop', 'shift', 'unshift', 'splice', 'sort', 'reverse'];

// ========== Vue 3 - Proxy ==========
function reactive(target) {
    return new Proxy(target, {
        get(target, key, receiver) {
            console.log('get', key);
            const result = Reflect.get(target, key, receiver);
            track(target, key);  // 依赖收集
            return result;
        },
        set(target, key, value, receiver) {
            console.log('set', key, value);
            const result = Reflect.set(target, key, value, receiver);
            trigger(target, key);  // 触发更新
            return result;
        },
        deleteProperty(target, key) {
            const result = Reflect.deleteProperty(target, key);
            trigger(target, key);
            return result;
        }
    });
}

// 优势
// 1. 可以检测属性的添加和删除
const state = reactive({ a: 1 });
state.b = 2;  // 响应式

// 2. 可以检测数组索引和长度
state.arr[0] = 100;  // 响应式
state.arr.length = 0;  // 响应式

// 3. 支持Map、Set等
const map = reactive(new Map());
map.set('key', 'value');  // 响应式

// ref vs reactive
import { ref, reactive } from 'vue';

// ref - 基本类型
const count = ref(0);
console.log(count.value);  // 需要.value
count.value++;

// reactive - 对象
const state = reactive({
    count: 0,
    name: 'Alice'
});
console.log(state.count);  // 不需要.value
state.count++;

// computed
const doubled = computed(() => count.value * 2);

// watch
watch(count, (newVal, oldVal) => {
    console.log(`count changed from ${oldVal} to ${newVal}`);
});

// watchEffect - 自动追踪依赖
watchEffect(() => {
    console.log(`count is ${count.value}`);
});
```

---

### 2. 生命周期钩子

**问题**: Vue生命周期及使用场景

**答案**:

```javascript
// Vue 2 生命周期
export default {
    // 创建阶段
    beforeCreate() {
        // data、methods未初始化
        // 用途: 加载loading
    },
    created() {
        // data、methods已初始化
        // 用途: 发起API请求、初始化非响应式数据
        this.fetchData();
    },
    
    // 挂载阶段
    beforeMount() {
        // 模板编译完成，未挂载到DOM
    },
    mounted() {
        // 已挂载到DOM
        // 用途: DOM操作、第三方库初始化、图表渲染
        this.initChart();
    },
    
    // 更新阶段
    beforeUpdate() {
        // 数据更新，DOM未更新
    },
    updated() {
        // DOM已更新
        // 注意: 避免在这里修改数据，可能导致无限循环
    },
    
    // 销毁阶段
    beforeDestroy() {
        // 用途: 清理定时器、解绑事件、清理第三方库
        clearInterval(this.timer);
        window.removeEventListener('resize', this.handleResize);
    },
    destroyed() {
        // 组件已销毁
    }
}

// Vue 3 Composition API
import { onBeforeMount, onMounted, onBeforeUpdate, onUpdated, 
         onBeforeUnmount, onUnmounted } from 'vue';

export default {
    setup() {
        onMounted(() => {
            console.log('Component mounted');
        });
        
        onBeforeUnmount(() => {
            console.log('Component about to unmount');
        });
        
        onUnmounted(() => {
            console.log('Component unmounted');
        });
    }
}

// 实用示例
export default {
    data() {
        return {
            timer: null,
            chart: null
        };
    },
    
    mounted() {
        // 1. 初始化图表
        this.chart = echarts.init(this.$refs.chart);
        this.chart.setOption(this.chartOptions);
        
        // 2. 添加事件监听
        window.addEventListener('resize', this.handleResize);
        
        // 3. 启动定时器
        this.timer = setInterval(() => {
            this.fetchData();
        }, 5000);
    },
    
    beforeDestroy() {
        // 清理
        if (this.chart) {
            this.chart.dispose();
        }
        
        window.removeEventListener('resize', this.handleResize);
        
        if (this.timer) {
            clearInterval(this.timer);
        }
    },
    
    methods: {
        handleResize() {
            this.chart.resize();
        },
        
        async fetchData() {
            const data = await api.getData();
            this.updateData(data);
        }
    }
}

// 父子组件生命周期顺序
// 父 beforeCreate
// 父 created
// 父 beforeMount
// 子 beforeCreate
// 子 created
// 子 beforeMount
// 子 mounted
// 父 mounted

// 更新时
// 父 beforeUpdate
// 子 beforeUpdate
// 子 updated
// 父 updated

// 销毁时
// 父 beforeDestroy
// 子 beforeDestroy
// 子 destroyed
// 父 destroyed
```

---

### 3. 组件通信

**问题**: 实现各种组件通信方式

**答案**:

```vue
<!-- 1. Props down, Events up -->
<!-- Parent.vue -->
<template>
    <Child 
        :message="parentMsg" 
        @update="handleUpdate"
    />
</template>

<script>
export default {
    data() {
        return {
            parentMsg: 'Hello from parent'
        };
    },
    methods: {
        handleUpdate(data) {
            console.log('Received from child:', data);
        }
    }
}
</script>

<!-- Child.vue -->
<template>
    <div>
        <p>{{ message }}</p>
        <button @click="sendToParent">Send to Parent</button>
    </div>
</template>

<script>
export default {
    props: {
        message: {
            type: String,
            required: true,
            default: ''
        }
    },
    methods: {
        sendToParent() {
            this.$emit('update', 'Data from child');
        }
    }
}
</script>

<!-- 2. v-model 双向绑定 -->
<!-- Vue 2 -->
<template>
    <input 
        :value="value" 
        @input="$emit('input', $event.target.value)"
    >
</template>

<script>
export default {
    props: ['value']
}
</script>

<!-- 使用 -->
<CustomInput v-model="text" />

<!-- Vue 3 -->
<template>
    <input 
        :value="modelValue" 
        @input="$emit('update:modelValue', $event.target.value)"
    >
</template>

<script>
export default {
    props: ['modelValue'],
    emits: ['update:modelValue']
}
</script>

<!-- 3. $attrs 和 $listeners (Vue 2) -->
<template>
    <div>
        <Child v-bind="$attrs" v-on="$listeners" />
    </div>
</template>

<!-- Vue 3 - $attrs包含了事件 -->
<template>
    <Child v-bind="$attrs" />
</template>

<!-- 4. provide / inject -->
<!-- Ancestor.vue -->
<script>
export default {
    provide() {
        return {
            theme: this.theme,
            updateTheme: this.updateTheme
        };
    },
    data() {
        return {
            theme: 'light'
        };
    },
    methods: {
        updateTheme(newTheme) {
            this.theme = newTheme;
        }
    }
}
</script>

<!-- Descendant.vue -->
<script>
export default {
    inject: ['theme', 'updateTheme'],
    mounted() {
        console.log(this.theme);  // 'light'
        this.updateTheme('dark');
    }
}
</script>

<!-- Vue 3 响应式 provide/inject -->
<script setup>
import { ref, provide, inject } from 'vue';

// Ancestor
const theme = ref('light');
provide('theme', theme);

// Descendant
const theme = inject('theme');
</script>

<!-- 5. Event Bus (Vue 2) -->
// eventBus.js
import Vue from 'vue';
export const EventBus = new Vue();

// Component A
import { EventBus } from './eventBus';

EventBus.$emit('event-name', data);

// Component B
import { EventBus } from './eventBus';

EventBus.$on('event-name', (data) => {
    console.log(data);
});

// 清理
beforeDestroy() {
    EventBus.$off('event-name');
}

<!-- Vue 3 使用 mitt -->
import mitt from 'mitt';
export const emitter = mitt();

// Component A
emitter.emit('event-name', data);

// Component B
emitter.on('event-name', (data) => {
    console.log(data);
});

// 清理
onUnmounted(() => {
    emitter.off('event-name');
});

<!-- 6. Vuex -->
// store/index.js
export default new Vuex.Store({
    state: {
        count: 0
    },
    mutations: {
        increment(state) {
            state.count++;
        }
    },
    actions: {
        async fetchData({ commit }) {
            const data = await api.getData();
            commit('setData', data);
        }
    },
    getters: {
        doubleCount: state => state.count * 2
    }
});

// Component
this.$store.commit('increment');
this.$store.dispatch('fetchData');
console.log(this.$store.state.count);
console.log(this.$store.getters.doubleCount);

<!-- 7. $refs -->
<template>
    <ChildComponent ref="child" />
    <button @click="callChildMethod">Call Child</button>
</template>

<script>
export default {
    methods: {
        callChildMethod() {
            this.$refs.child.childMethod();
        }
    }
}
</script>
```

---

### 4. Vuex 状态管理

**问题**: Vuex的核心概念和最佳实践

**答案**:

```javascript
// store/index.js
import Vue from 'vue';
import Vuex from 'vuex';

Vue.use(Vuex);

export default new Vuex.Store({
    // State - 单一状态树
    state: {
        count: 0,
        user: null,
        todos: []
    },
    
    // Getters - 派生状态
    getters: {
        doneTodos: state => {
            return state.todos.filter(todo => todo.done);
        },
        doneTodosCount: (state, getters) => {
            return getters.doneTodos.length;
        },
        getTodoById: (state) => (id) => {
            return state.todos.find(todo => todo.id === id);
        }
    },
    
    // Mutations - 同步修改状态
    mutations: {
        increment(state) {
            state.count++;
        },
        incrementBy(state, payload) {
            state.count += payload.amount;
        },
        setUser(state, user) {
            state.user = user;
        },
        addTodo(state, todo) {
            state.todos.push(todo);
        }
    },
    
    // Actions - 异步操作
    actions: {
        async login({ commit }, credentials) {
            try {
                const user = await api.login(credentials);
                commit('setUser', user);
                return user;
            } catch (error) {
                console.error('Login failed:', error);
                throw error;
            }
        },
        
        async fetchTodos({ commit, state }) {
            const todos = await api.getTodos();
            commit('setTodos', todos);
        },
        
        // 组合actions
        async initApp({ dispatch }) {
            await dispatch('login');
            await dispatch('fetchTodos');
        }
    },
    
    // Modules - 模块化
    modules: {
        user: {
            namespaced: true,
            state: () => ({
                profile: null
            }),
            mutations: {
                setProfile(state, profile) {
                    state.profile = profile;
                }
            },
            actions: {
                async fetchProfile({ commit }) {
                    const profile = await api.getProfile();
                    commit('setProfile', profile);
                }
            }
        },
        
        cart: {
            namespaced: true,
            state: () => ({
                items: []
            }),
            getters: {
                total: state => {
                    return state.items.reduce((sum, item) => sum + item.price, 0);
                }
            },
            mutations: {
                addItem(state, item) {
                    state.items.push(item);
                },
                clearCart(state) {
                    state.items = [];
                }
            }
        }
    }
});

// 在组件中使用
import { mapState, mapGetters, mapMutations, mapActions } from 'vuex';

export default {
    computed: {
        // 映射state
        ...mapState(['count', 'user']),
        ...mapState('user', ['profile']),
        
        // 映射getters
        ...mapGetters(['doneTodos', 'doneTodosCount']),
        ...mapGetters('cart', ['total']),
        
        // 自定义名称
        ...mapState({
            userCount: state => state.count,
            currentUser: 'user'
        })
    },
    
    methods: {
        // 映射mutations
        ...mapMutations(['increment', 'addTodo']),
        ...mapMutations('user', ['setProfile']),
        
        // 映射actions
        ...mapActions(['login', 'fetchTodos']),
        ...mapActions('user', ['fetchProfile']),
        
        // 使用
        async handleLogin() {
            await this.login({ username: 'user', password: 'pass' });
        }
    }
};

// Vue 3 + Pinia (推荐)
import { defineStore } from 'pinia';

export const useUserStore = defineStore('user', {
    state: () => ({
        user: null,
        token: null
    }),
    
    getters: {
        isLoggedIn: (state) => !!state.token,
        userName: (state) => state.user?.name
    },
    
    actions: {
        async login(credentials) {
            const { user, token } = await api.login(credentials);
            this.user = user;
            this.token = token;
        },
        
        logout() {
            this.user = null;
            this.token = null;
        }
    }
});

// 在组件中使用
<script setup>
import { useUserStore } from '@/stores/user';

const userStore = useUserStore();

// 直接访问
console.log(userStore.user);
console.log(userStore.isLoggedIn);

// 修改状态
userStore.user = newUser;

// 调用action
await userStore.login(credentials);
</script>
```

---

### 5. Vue 3 Composition API

**问题**: 对比Options API和Composition API

**答案**:

```vue
<!-- Options API (Vue 2风格) -->
<script>
export default {
    data() {
        return {
            count: 0,
            name: ''
        };
    },
    computed: {
        doubled() {
            return this.count * 2;
        }
    },
    methods: {
        increment() {
            this.count++;
        }
    },
    mounted() {
        console.log('mounted');
    }
}
</script>

<!-- Composition API (Vue 3) -->
<script setup>
import { ref, computed, onMounted } from 'vue';

const count = ref(0);
const name = ref('');

const doubled = computed(() => count.value * 2);

function increment() {
    count.value++;
}

onMounted(() => {
    console.log('mounted');
});
</script>

<!-- 可复用逻辑 - Composables -->
<!-- useCounter.js -->
import { ref, computed } from 'vue';

export function useCounter(initialValue = 0) {
    const count = ref(initialValue);
    const doubled = computed(() => count.value * 2);
    
    function increment() {
        count.value++;
    }
    
    function decrement() {
        count.value--;
    }
    
    return {
        count,
        doubled,
        increment,
        decrement
    };
}

<!-- 使用 -->
<script setup>
import { useCounter } from './composables/useCounter';

const { count, doubled, increment, decrement } = useCounter(10);
</script>

<!-- 更多Composables示例 -->
<!-- useMousePosition.js -->
import { ref, onMounted, onUnmounted } from 'vue';

export function useMousePosition() {
    const x = ref(0);
    const y = ref(0);
    
    function update(event) {
        x.value = event.pageX;
        y.value = event.pageY;
    }
    
    onMounted(() => {
        window.addEventListener('mousemove', update);
    });
    
    onUnmounted(() => {
        window.removeEventListener('mousemove', update);
    });
    
    return { x, y };
}

<!-- useFetch.js -->
import { ref } from 'vue';

export function useFetch(url) {
    const data = ref(null);
    const error = ref(null);
    const loading = ref(false);
    
    async function fetch() {
        loading.value = true;
        try {
            const response = await window.fetch(url);
            data.value = await response.json();
        } catch (e) {
            error.value = e;
        } finally {
            loading.value = false;
        }
    }
    
    return { data, error, loading, fetch };
}

<!-- 使用多个composables -->
<script setup>
import { useCounter } from './composables/useCounter';
import { useMousePosition } from './composables/useMousePosition';
import { useFetch } from './composables/useFetch';

const { count, increment } = useCounter();
const { x, y } = useMousePosition();
const { data, loading, fetch } = useFetch('/api/users');

fetch();
</script>

<template>
    <div>
        <p>Count: {{ count }}</p>
        <button @click="increment">Increment</button>
        
        <p>Mouse: {{ x }}, {{ y }}</p>
        
        <div v-if="loading">Loading...</div>
        <div v-else>{{ data }}</div>
    </div>
</template>

<!-- defineProps 和 defineEmits -->
<script setup>
const props = defineProps({
    title: String,
    count: {
        type: Number,
        default: 0
    }
});

const emit = defineEmits(['update', 'delete']);

function handleUpdate() {
    emit('update', props.count + 1);
}
</script>

<!-- defineExpose - 暴露给父组件 -->
<script setup>
import { ref } from 'vue';

const count = ref(0);

function increment() {
    count.value++;
}

// 只暴露这些给父组件
defineExpose({
    count,
    increment
});
</script>
```

---

# GitOps篇

## GitOps核心概念

### 1. GitOps原则和实践

**问题**: 什么是GitOps？核心原则是什么？

**答案**:

**GitOps核心原则**:
1. **声明式配置** - 整个系统状态用声明式描述
2. **Git作为单一事实来源** - 所有配置存储在Git仓库
3. **自动化** - Git变更自动触发部署
4. **持续协调** - 系统状态持续与Git仓库对齐

```yaml
# 传统部署 vs GitOps

# 传统部署（命令式）
kubectl create deployment nginx --image=nginx:1.20
kubectl scale deployment nginx --replicas=3
kubectl expose deployment nginx --port=80

# GitOps（声明式）
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx
spec:
  replicas: 3
  selector:
    matchLabels:
      app: nginx
  template:
    metadata:
      labels:
        app: nginx
    spec:
      containers:
      - name: nginx
        image: nginx:1.20
        ports:
        - containerPort: 80
---
apiVersion: v1
kind: Service
metadata:
  name: nginx
spec:
  selector:
    app: nginx
  ports:
  - port: 80
    targetPort: 80
```

**GitOps工作流**:
```
┌─────────────┐
│  Developer  │
└──────┬──────┘
       │ git push
       ▼
┌─────────────┐
│ Git Repo    │  ← Single Source of Truth
│ (Config)    │
└──────┬──────┘
       │ watch/pull
       ▼
┌─────────────┐
│ GitOps      │
│ Operator    │  (Argo CD / Flux)
└──────┬──────┘
       │ apply
       ▼
┌─────────────┐
│ Kubernetes  │
│ Cluster     │
└─────────────┘
```

**对比传统CI/CD**:

| 特性 | 传统CI/CD | GitOps |
|-----|----------|--------|
| **部署方式** | Push (CI推送) | Pull (Operator拉取) |
| **权限管理** | CI需要集群权限 | CI无需集群权限 |
| **状态同步** | 单向 | 双向（自动修正漂移） |
| **审计** | CI日志 | Git历史 |
| **回滚** | 手动触发 | Git revert |

---

### 2. Argo CD实战

**问题**: 使用Argo CD实现GitOps部署

**答案**:

```bash
# 安装Argo CD
kubectl create namespace argocd
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml

# 获取admin密码
kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d

# 端口转发访问UI
kubectl port-forward svc/argocd-server -n argocd 8080:443

# 使用CLI
argocd login localhost:8080
argocd app list
```

**创建Application**:
```yaml
# application.yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: my-app
  namespace: argocd
spec:
  project: default
  
  # Git仓库源
  source:
    repoURL: https://github.com/example/k8s-manifests
    targetRevision: main
    path: apps/my-app
    
    # Helm支持
    helm:
      valueFiles:
        - values-prod.yaml
      parameters:
        - name: image.tag
          value: v1.2.3
  
  # 目标集群
  destination:
    server: https://kubernetes.default.svc
    namespace: production
  
  # 同步策略
  syncPolicy:
    automated:
      prune: true      # 删除不在Git中的资源
      selfHeal: true   # 自动修复漂移
      allowEmpty: false
    
    syncOptions:
      - CreateNamespace=true
    
    retry:
      limit: 5
      backoff:
        duration: 5s
        factor: 2
        maxDuration: 3m
```

**多环境管理**:
```yaml
# Kustomize方式
# base/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-app
spec:
  replicas: 2
  template:
    spec:
      containers:
      - name: app
        image: myapp:latest

# overlays/dev/kustomization.yaml
bases:
  - ../../base
patchesStrategicMerge:
  - replica-patch.yaml
images:
  - name: myapp
    newTag: dev-latest

# overlays/prod/kustomization.yaml
bases:
  - ../../base
patchesStrategicMerge:
  - replica-patch.yaml
images:
  - name: myapp
    newTag: v1.2.3
```

**App of Apps模式**:
```yaml
# root-app.yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: root-app
spec:
  source:
    repoURL: https://github.com/example/argocd-apps
    path: apps
  destination:
    server: https://kubernetes.default.svc
    namespace: argocd
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
```

---

### 3. Flux实战

**问题**: 使用Flux实现GitOps

**答案**:

```bash
# 安装Flux CLI
brew install fluxcd/tap/flux

# 检查集群
flux check --pre

# Bootstrap到GitHub
export GITHUB_TOKEN=<your-token>
flux bootstrap github \
  --owner=my-org \
  --repository=fleet-infra \
  --branch=main \
  --path=clusters/production \
  --personal

# 创建GitRepository
flux create source git my-app \
  --url=https://github.com/example/my-app \
  --branch=main \
  --interval=1m \
  --export > ./clusters/production/my-app-source.yaml

# 创建Kustomization
flux create kustomization my-app \
  --source=my-app \
  --path="./kustomize" \
  --prune=true \
  --interval=5m \
  --export > ./clusters/production/my-app-kustomization.yaml
```

**Image自动更新**:
```yaml
# image-repository.yaml
apiVersion: image.toolkit.fluxcd.io/v1beta1
kind: ImageRepository
metadata:
  name: my-app
spec:
  image: registry.example.com/my-app
  interval: 1m

---
# image-policy.yaml
apiVersion: image.toolkit.fluxcd.io/v1beta1
kind: ImagePolicy
metadata:
  name: my-app
spec:
  imageRepositoryRef:
    name: my-app
  policy:
    semver:
      range: 1.x.x

---
# image-update.yaml
apiVersion: image.toolkit.fluxcd.io/v1beta1
kind: ImageUpdateAutomation
metadata:
  name: my-app
spec:
  interval: 1m
  sourceRef:
    kind: GitRepository
    name: my-app
  git:
    checkout:
      ref:
        branch: main
    commit:
      author:
        email: fluxbot@example.com
        name: Flux Bot
      messageTemplate: |
        Update image to {{range .Updated.Images}}{{println .}}{{end}}
    push:
      branch: main
  update:
    path: ./kustomize
    strategy: Setters
```

**Helm Release**:
```yaml
# helm-release.yaml
apiVersion: helm.toolkit.fluxcd.io/v2beta1
kind: HelmRelease
metadata:
  name: nginx
  namespace: default
spec:
  interval: 5m
  chart:
    spec:
      chart: nginx
      version: '9.x.x'
      sourceRef:
        kind: HelmRepository
        name: bitnami
        namespace: flux-system
  values:
    replicaCount: 3
    service:
      type: LoadBalancer
```

---

## GitOps最佳实践

### 4. GitOps安全和合规

**问题**: GitOps的安全实践

**答案**:

```yaml
# 1. 密钥管理 - Sealed Secrets
# 安装
kubectl apply -f https://github.com/bitnami-labs/sealed-secrets/releases/download/v0.18.0/controller.yaml

# 创建密钥
kubectl create secret generic mysecret \
  --from-literal=password=mypassword \
  --dry-run=client -o yaml | \
  kubeseal -o yaml > sealed-secret.yaml

# sealed-secret.yaml可以安全提交到Git
apiVersion: bitnami.com/v1alpha1
kind: SealedSecret
metadata:
  name: mysecret
spec:
  encryptedData:
    password: AgBy3i4OJSWK+PiTySYZZA9rO43cGDEq...

# 2. SOPS (Mozilla)
# .sops.yaml
creation_rules:
  - path_regex: .*.yaml
    encrypted_regex: ^(data|stringData)$
    kms: arn:aws:kms:us-east-1:123456789012:key/12345678-1234-1234-1234-123456789012

# 加密secret
sops --encrypt --in-place secret.yaml

# 3. 外部密钥注入 - External Secrets Operator
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: example
spec:
  refreshInterval: 1h
  secretStoreRef:
    name: vault-backend
    kind: SecretStore
  target:
    name: secret-to-be-created
  data:
  - secretKey: password
    remoteRef:
      key: secret/data/production/database
      property: password

# 4. RBAC最佳实践
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: argocd-application-controller
rules:
- apiGroups: [""]
  resources: ["pods", "services", "configmaps"]
  verbs: ["get", "list", "watch", "create", "update", "delete"]
- apiGroups: ["apps"]
  resources: ["deployments", "statefulsets"]
  verbs: ["get", "list", "watch", "create", "update", "delete"]

# 5. 审计和合规
# Git commit签名
git config --global commit.gpgsign true
git config --global user.signingkey YOUR_GPG_KEY

# PR审批流程
# .github/CODEOWNERS
/manifests/production/ @platform-team @security-team
/manifests/*/secrets/ @security-team
```

**分离配置和密钥**:
```
repo-structure/
├── base/
│   ├── deployment.yaml
│   ├── service.yaml
│   └── kustomization.yaml
├── overlays/
│   ├── dev/
│   │   ├── kustomization.yaml
│   │   └── configmap.yaml
│   └── prod/
│       ├── kustomization.yaml
│       └── configmap.yaml
└── secrets/  # 单独的私有仓库
    ├── dev/
    │   └── sealed-secrets.yaml
    └── prod/
        └── sealed-secrets.yaml
```

---

# DevOps篇

## CI/CD流程

### 1. CI/CD核心概念

**问题**: 解释CI/CD流程和最佳实践

**答案**:

**CI/CD流程**:
```
┌──────────────┐
│ Code Commit  │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  CI Pipeline │
│  - Build     │
│  - Test      │
│  - Security  │
│  - Package   │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ Artifact     │
│ Registry     │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ CD Pipeline  │
│ - Deploy Dev │
│ - Test       │
│ - Deploy Prod│
└──────────────┘
```

**GitHub Actions示例**:
```yaml
# .github/workflows/ci.yaml
name: CI

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Go
        uses: actions/setup-go@v4
        with:
          go-version: '1.21'
      
      - name: Run tests
        run: |
          go test -v -race -coverprofile=coverage.txt ./...
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          files: ./coverage.txt
  
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: golangci-lint
        uses: golangci/golangci-lint-action@v3
        with:
          version: latest
  
  security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Run Trivy vulnerability scanner
        uses: aquasecurity/trivy-action@master
        with:
          scan-type: 'fs'
          scan-ref: '.'
          format: 'sarif'
          output: 'trivy-results.sarif'
      
      - name: Upload Trivy results to GitHub Security tab
        uses: github/codeql-action/upload-sarif@v2
        with:
          sarif_file: 'trivy-results.sarif'
  
  build:
    needs: [test, lint, security]
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Log in to Container Registry
        uses: docker/login-action@v2
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      
      - name: Extract metadata
        id: meta
        uses: docker/metadata-action@v4
        with:
          images: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}
          tags: |
            type=ref,event=branch
            type=ref,event=pr
            type=semver,pattern={{version}}
            type=sha
      
      - name: Build and push
        uses: docker/build-push-action@v4
        with:
          context: .
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
          cache-from: type=gha
          cache-to: type=gha,mode=max
```

**GitLab CI示例**:
```yaml
# .gitlab-ci.yml
stages:
  - test
  - build
  - deploy

variables:
  DOCKER_IMAGE: $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA

test:
  stage: test
  image: golang:1.21
  script:
    - go test -v -race ./...
  coverage: '/total:.*\s(\d+\.\d+)%/'

lint:
  stage: test
  image: golangci/golangci-lint:latest
  script:
    - golangci-lint run

security_scan:
  stage: test
  image: aquasec/trivy:latest
  script:
    - trivy fs --exit-code 1 --severity CRITICAL,HIGH .

build:
  stage: build
  image: docker:latest
  services:
    - docker:dind
  before_script:
    - docker login -u $CI_REGISTRY_USER -p $CI_REGISTRY_PASSWORD $CI_REGISTRY
  script:
    - docker build -t $DOCKER_IMAGE .
    - docker push $DOCKER_IMAGE
  only:
    - main
    - tags

deploy_dev:
  stage: deploy
  image: bitnami/kubectl:latest
  script:
    - kubectl config use-context dev-cluster
    - kubectl set image deployment/myapp myapp=$DOCKER_IMAGE
    - kubectl rollout status deployment/myapp
  environment:
    name: development
  only:
    - main

deploy_prod:
  stage: deploy
  image: bitnami/kubectl:latest
  script:
    - kubectl config use-context prod-cluster
    - kubectl set image deployment/myapp myapp=$DOCKER_IMAGE
    - kubectl rollout status deployment/myapp
  environment:
    name: production
  when: manual
  only:
    - tags
```

---

### 2. Docker容器化

**问题**: Docker最佳实践

**答案**:

```dockerfile
# 多阶段构建 - Golang示例
FROM golang:1.21-alpine AS builder

WORKDIR /app

# 缓存依赖
COPY go.mod go.sum ./
RUN go mod download

# 构建
COPY . .
RUN CGO_ENABLED=0 GOOS=linux go build -a -installsuffix cgo -o main .

# 最终镜像
FROM alpine:latest

RUN apk --no-cache add ca-certificates

WORKDIR /root/

# 只复制二进制文件
COPY --from=builder /app/main .

# 非root用户
RUN addgroup -S appgroup && adduser -S appuser -G appgroup
USER appuser

EXPOSE 8080

CMD ["./main"]
```

```dockerfile
# Node.js示例
FROM node:18-alpine AS builder

WORKDIR /app

# 缓存依赖
COPY package*.json ./
RUN npm ci --only=production

# 构建
COPY . .
RUN npm run build

# 最终镜像
FROM node:18-alpine

WORKDIR /app

ENV NODE_ENV=production

# 复制依赖和构建产物
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/package*.json ./

# 非root用户
USER node

EXPOSE 3000

CMD ["node", "dist/index.js"]
```

**.dockerignore**:
```
node_modules
npm-debug.log
.git
.gitignore
.env
.env.local
dist
build
*.md
.vscode
.idea
coverage
.DS_Store
```

**Docker Compose示例**:
```yaml
# docker-compose.yml
version: '3.8'

services:
  app:
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "3000:3000"
    environment:
      - DATABASE_URL=postgresql://postgres:password@db:5432/mydb
      - REDIS_URL=redis://redis:6379
    depends_on:
      - db
      - redis
    restart: unless-stopped
  
  db:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: mydb
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5
  
  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data
    command: redis-server --appendonly yes
  
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
    depends_on:
      - app

volumes:
  postgres_data:
  redis_data:
```

---

### 3. Kubernetes部署

**问题**: Kubernetes核心概念和部署

**答案**:

```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: myapp
  labels:
    app: myapp
spec:
  replicas: 3
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 1
  selector:
    matchLabels:
      app: myapp
  template:
    metadata:
      labels:
        app: myapp
    spec:
      containers:
      - name: myapp
        image: myapp:v1.2.3
        ports:
        - containerPort: 8080
          name: http
        
        # 资源限制
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        
        # 健康检查
        livenessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 10
          timeoutSeconds: 5
          failureThreshold: 3
        
        readinessProbe:
          httpGet:
            path: /ready
            port: 8080
          initialDelaySeconds: 10
          periodSeconds: 5
          timeoutSeconds: 3
          failureThreshold: 3
        
        # 环境变量
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: myapp-secret
              key: database-url
        - name: LOG_LEVEL
          valueFrom:
            configMapKeyRef:
              name: myapp-config
              key: log-level
        
        # 挂载卷
        volumeMounts:
        - name: config
          mountPath: /etc/config
          readOnly: true
      
      volumes:
      - name: config
        configMap:
          name: myapp-config

---
# service.yaml
apiVersion: v1
kind: Service
metadata:
  name: myapp
spec:
  type: ClusterIP
  selector:
    app: myapp
  ports:
  - port: 80
    targetPort: 8080
    protocol: TCP
    name: http

---
# ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: myapp
  annotations:
    kubernetes.io/ingress.class: nginx
    cert-manager.io/cluster-issuer: letsencrypt-prod
spec:
  tls:
  - hosts:
    - myapp.example.com
    secretName: myapp-tls
  rules:
  - host: myapp.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: myapp
            port:
              number: 80

---
# hpa.yaml (Horizontal Pod Autoscaler)
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: myapp
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: myapp
  minReplicas: 3
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

**Helm Chart示例**:
```yaml
# Chart.yaml
apiVersion: v2
name: myapp
description: A Helm chart for myapp
type: application
version: 1.0.0
appVersion: "1.2.3"

# values.yaml
replicaCount: 3

image:
  repository: myregistry.io/myapp
  tag: v1.2.3
  pullPolicy: IfNotPresent

service:
  type: ClusterIP
  port: 80

ingress:
  enabled: true
  className: nginx
  hosts:
    - host: myapp.example.com
      paths:
        - path: /
          pathType: Prefix
  tls:
    - secretName: myapp-tls
      hosts:
        - myapp.example.com

resources:
  requests:
    memory: "256Mi"
    cpu: "250m"
  limits:
    memory: "512Mi"
    cpu: "500m"

autoscaling:
  enabled: true
  minReplicas: 3
  maxReplicas: 10
  targetCPUUtilizationPercentage: 70

# 部署
helm install myapp ./myapp -f values-prod.yaml
helm upgrade myapp ./myapp -f values-prod.yaml
helm rollback myapp 1
```

---

### 4. 监控和告警

**问题**: 实现Prometheus + Grafana监控

**答案**:

```yaml
# prometheus-config.yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  # Kubernetes API服务器
  - job_name: 'kubernetes-apiservers'
    kubernetes_sd_configs:
    - role: endpoints
    scheme: https
    tls_config:
      ca_file: /var/run/secrets/kubernetes.io/serviceaccount/ca.crt
    bearer_token_file: /var/run/secrets/kubernetes.io/serviceaccount/token
    relabel_configs:
    - source_labels: [__meta_kubernetes_namespace, __meta_kubernetes_service_name, __meta_kubernetes_endpoint_port_name]
      action: keep
      regex: default;kubernetes;https
  
  # Node Exporter
  - job_name: 'kubernetes-nodes'
    kubernetes_sd_configs:
    - role: node
    relabel_configs:
    - action: labelmap
      regex: __meta_kubernetes_node_label_(.+)
  
  # Pods
  - job_name: 'kubernetes-pods'
    kubernetes_sd_configs:
    - role: pod
    relabel_configs:
    - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_scrape]
      action: keep
      regex: true
    - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_path]
      action: replace
      target_label: __metrics_path__
      regex: (.+)
    - source_labels: [__address__, __meta_kubernetes_pod_annotation_prometheus_io_port]
      action: replace
      regex: ([^:]+)(?::\d+)?;(\d+)
      replacement: $1:$2
      target_label: __address__

# 告警规则
alerting:
  alertmanagers:
  - static_configs:
    - targets:
      - alertmanager:9093

rule_files:
  - /etc/prometheus/rules/*.yaml
```

**告警规则**:
```yaml
# alerts.yaml
groups:
- name: example
  interval: 30s
  rules:
  # Pod重启频繁
  - alert: PodRestartingTooOften
    expr: rate(kube_pod_container_status_restarts_total[15m]) > 1/3600
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "Pod {{ $labels.namespace }}/{{ $labels.pod }} restarting too often"
      description: "Pod has restarted {{ $value }} times in the last 15 minutes"
  
  # 高CPU使用率
  - alert: HighCPUUsage
    expr: 100 - (avg by(instance) (irate(node_cpu_seconds_total{mode="idle"}[5m])) * 100) > 80
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "High CPU usage on {{ $labels.instance }}"
      description: "CPU usage is {{ $value }}%"
  
  # 高内存使用率
  - alert: HighMemoryUsage
    expr: (1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100 > 85
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "High memory usage on {{ $labels.instance }}"
      description: "Memory usage is {{ $value }}%"
  
  # 磁盘空间不足
  - alert: DiskSpaceLow
    expr: (1 - (node_filesystem_avail_bytes{fstype!~"tmpfs|fuse.lxcfs"} / node_filesystem_size_bytes)) * 100 > 85
    for: 5m
    labels:
      severity: critical
    annotations:
      summary: "Disk space low on {{ $labels.instance }}"
      description: "Disk usage is {{ $value }}% on {{ $labels.mountpoint }}"
```

**应用监控示例**:
```go
// Golang with Prometheus
package main

import (
    "github.com/prometheus/client_golang/prometheus"
    "github.com/prometheus/client_golang/prometheus/promhttp"
    "net/http"
)

var (
    httpRequestsTotal = prometheus.NewCounterVec(
        prometheus.CounterOpts{
            Name: "http_requests_total",
            Help: "Total number of HTTP requests",
        },
        []string{"method", "endpoint", "status"},
    )
    
    httpDuration = prometheus.NewHistogramVec(
        prometheus.HistogramOpts{
            Name: "http_request_duration_seconds",
            Help: "HTTP request latencies in seconds",
            Buckets: prometheus.DefBuckets,
        },
        []string{"method", "endpoint"},
    )
    
    activeConnections = prometheus.NewGauge(
        prometheus.GaugeOpts{
            Name: "active_connections",
            Help: "Number of active connections",
        },
    )
)

func init() {
    prometheus.MustRegister(httpRequestsTotal)
    prometheus.MustRegister(httpDuration)
    prometheus.MustRegister(activeConnections)
}

func main() {
    http.Handle("/metrics", promhttp.Handler())
    http.ListenAndServe(":8080", nil)
}
```

---

### 5. 日志管理

**问题**: ELK/Loki日志架构

**答案**:

**Loki + Promtail + Grafana**:
```yaml
# promtail-config.yaml
server:
  http_listen_port: 9080
  grpc_listen_port: 0

positions:
  filename: /tmp/positions.yaml

clients:
  - url: http://loki:3100/loki/api/v1/push

scrape_configs:
  # Kubernetes Pod日志
  - job_name: kubernetes-pods
    kubernetes_sd_configs:
    - role: pod
    
    relabel_configs:
    - source_labels: [__meta_kubernetes_pod_label_app]
      target_label: app
    - source_labels: [__meta_kubernetes_pod_label_component]
      target_label: component
    - source_labels: [__meta_kubernetes_namespace]
      target_label: namespace
    - source_labels: [__meta_kubernetes_pod_name]
      target_label: pod
    
    pipeline_stages:
    - docker: {}
    - json:
        expressions:
          level: level
          msg: msg
    - labels:
        level:
    - timestamp:
        source: time
        format: RFC3339Nano

# 查询示例
{namespace="production", app="myapp"} |= "error"
{namespace="production"} | json | level="error"
sum(rate({app="myapp"}[5m])) by (level)
```

**结构化日志**:
```go
// Golang - 使用zap
package main

import (
    "go.uber.org/zap"
)

func main() {
    logger, _ := zap.NewProduction()
    defer logger.Sync()
    
    logger.Info("API request",
        zap.String("method", "GET"),
        zap.String("path", "/api/users"),
        zap.Int("status", 200),
        zap.Duration("latency", time.Millisecond*125),
    )
    
    // 输出JSON格式
    // {"level":"info","ts":1234567890.123,"msg":"API request","method":"GET","path":"/api/users","status":200,"latency":0.125}
}
```

---

# 云计算篇

## 云服务基础

### 1. 云服务模型

**问题**: IaaS、PaaS、SaaS的区别

**答案**:

**云服务模型对比**:
```
传统IT    IaaS      PaaS      SaaS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
应用      应用      应用      ✓ SaaS
数据      数据      数据      ✓ SaaS
运行时    运行时    ✓ PaaS    ✓ SaaS
中间件    中间件    ✓ PaaS    ✓ SaaS
操作系统  操作系统  ✓ PaaS    ✓ SaaS
虚拟化    ✓ IaaS   ✓ PaaS    ✓ SaaS
服务器    ✓ IaaS   ✓ PaaS    ✓ SaaS
存储      ✓ IaaS   ✓ PaaS    ✓ SaaS
网络      ✓ IaaS   ✓ PaaS    ✓ SaaS

✓ = 云提供商管理
```

| 模型 | 示例 | 使用场景 | 优势 |
|-----|------|---------|------|
| **IaaS** | AWS EC2, Azure VM, GCP Compute Engine | 虚拟机、存储、网络 | 最大灵活性 |
| **PaaS** | Heroku, Google App Engine, AWS Elastic Beanstalk | 应用部署平台 | 专注业务逻辑 |
| **SaaS** | Gmail, Salesforce, Slack | 现成软件服务 | 即开即用 |

---

### 2. AWS核心服务

**问题**: AWS常用服务和架构

**答案**:

**核心服务**:
```yaml
# 计算
EC2:        虚拟服务器
Lambda:     无服务器函数
ECS/EKS:    容器服务
Fargate:    无服务器容器

# 存储
S3:         对象存储
EBS:        块存储（EC2卷）
EFS:        文件系统
Glacier:    归档存储

# 数据库
RDS:        关系数据库（MySQL, PostgreSQL, etc.）
DynamoDB:   NoSQL
ElastiCache: Redis/Memcached
Aurora:     MySQL/PostgreSQL兼容

# 网络
VPC:        虚拟私有云
Route 53:   DNS服务
CloudFront: CDN
ELB:        负载均衡
API Gateway: API管理

# 安全
IAM:        身份和访问管理
KMS:        密钥管理
Secrets Manager: 密钥存储
WAF:        Web应用防火墙

# 监控
CloudWatch:  监控和日志
X-Ray:       分布式追踪
CloudTrail:  审计日志
```

**典型Web应用架构**:
```
Internet
    │
    ├─ Route 53 (DNS)
    │
    ▼
CloudFront (CDN)
    │
    ├─ S3 (静态资源)
    │
    ▼
ALB (负载均衡)
    │
    ├─ WAF (防火墙)
    │
    ▼
┌──────────────────────┐
│  Auto Scaling Group  │
│  ┌────┐ ┌────┐ ┌────┐│
│  │EC2 │ │EC2 │ │EC2 ││
│  └────┘ └────┘ └────┘│
└──────────────────────┘
    │
    ├─ ElastiCache (缓存)
    │
    ├─ RDS Multi-AZ (数据库)
    │
    └─ S3 (对象存储)
```

**Terraform示例**:
```hcl
# main.tf
provider "aws" {
  region = "us-east-1"
}

# VPC
resource "aws_vpc" "main" {
  cidr_block = "10.0.0.0/16"
  
  tags = {
    Name = "main-vpc"
  }
}

# 公有子网
resource "aws_subnet" "public" {
  count             = 2
  vpc_id            = aws_vpc.main.id
  cidr_block        = "10.0.${count.index}.0/24"
  availability_zone = data.aws_availability_zones.available.names[count.index]
  
  map_public_ip_on_launch = true
  
  tags = {
    Name = "public-subnet-${count.index + 1}"
  }
}

# 私有子网
resource "aws_subnet" "private" {
  count             = 2
  vpc_id            = aws_vpc.main.id
  cidr_block        = "10.0.${count.index + 10}.0/24"
  availability_zone = data.aws_availability_zones.available.names[count.index]
  
  tags = {
    Name = "private-subnet-${count.index + 1}"
  }
}

# 安全组
resource "aws_security_group" "web" {
  name        = "web-sg"
  vpc_id      = aws_vpc.main.id
  
  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  
  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# ALB
resource "aws_lb" "main" {
  name               = "main-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.web.id]
  subnets            = aws_subnet.public[*].id
}

# RDS
resource "aws_db_instance" "main" {
  identifier           = "mydb"
  engine              = "postgres"
  engine_version      = "15.3"
  instance_class      = "db.t3.micro"
  allocated_storage   = 20
  storage_type        = "gp3"
  
  db_name  = "myapp"
  username = "admin"
  password = var.db_password
  
  multi_az             = true
  publicly_accessible  = false
  skip_final_snapshot = true
  
  vpc_security_group_ids = [aws_security_group.db.id]
  db_subnet_group_name   = aws_db_subnet_group.main.name
}
```

---

### 3. Kubernetes云原生架构

**问题**: 云原生应用设计

**答案**:

**12 Factor App原则**:
1. **代码库**: 一个代码库，多环境部署
2. **依赖**: 显式声明依赖
3. **配置**: 环境变量存储配置
4. **后端服务**: 附加资源通过URL访问
5. **构建、发布、运行**: 严格分离
6. **进程**: 无状态进程
7. **端口绑定**: 通过端口暴露服务
8. **并发**: 通过进程模型扩展
9. **易处理**: 快速启动和优雅终止
10. **开发/生产一致**: 保持环境一致
11. **日志**: 日志作为事件流
12. **管理进程**: 管理任务作为一次性进程

**微服务架构示例**:
```yaml
# 服务网格 - Istio
apiVersion: networking.istio.io/v1alpha3
kind: VirtualService
metadata:
  name: myapp
spec:
  hosts:
  - myapp
  http:
  # 金丝雀发布
  - match:
    - headers:
        user-agent:
          regex: ".*Mobile.*"
    route:
    - destination:
        host: myapp
        subset: v2
      weight: 100
  - route:
    - destination:
        host: myapp
        subset: v1
      weight: 90
    - destination:
        host: myapp
        subset: v2
      weight: 10

---
# 断路器
apiVersion: networking.istio.io/v1alpha3
kind: DestinationRule
metadata:
  name: myapp
spec:
  host: myapp
  trafficPolicy:
    connectionPool:
      tcp:
        maxConnections: 100
      http:
        http1MaxPendingRequests: 50
        http2MaxRequests: 100
    outlierDetection:
      consecutiveErrors: 5
      interval: 30s
      baseEjectionTime: 30s
      maxEjectionPercent: 50
```

**可观测性三支柱**:
```yaml
# 1. Metrics (Prometheus)
# 指标类型:
Counter:    递增计数器 (请求总数)
Gauge:      可增减的值 (当前连接数)
Histogram:  分布统计 (延迟分布)
Summary:    类似Histogram (客户端聚合)

# 2. Logs (Loki/ELK)
# 结构化日志示例
{
  "timestamp": "2024-01-15T10:30:00Z",
  "level": "INFO",
  "service": "api-gateway",
  "trace_id": "abc123",
  "span_id": "def456",
  "user_id": "user123",
  "method": "GET",
  "path": "/api/users",
  "status": 200,
  "latency_ms": 45
}

# 3. Traces (Jaeger/Zipkin)
# 分布式追踪
API Gateway
  │
  ├─ Auth Service (50ms)
  │
  ├─ User Service (120ms)
  │   │
  │   ├─ Database Query (80ms)
  │   └─ Cache Lookup (10ms)
  │
  └─ Notification Service (30ms)
```

---

### 4. 成本优化

**问题**: 云成本优化策略

**答案**:

**成本优化实践**:
```yaml
# 1. 资源调优
# 使用Spot实例/抢占式VM
apiVersion: v1
kind: Pod
spec:
  nodeSelector:
    cloud.google.com/gke-spot: "true"
  tolerations:
  - key: cloud.google.com/gke-spot
    operator: Equal
    value: "true"
    effect: NoSchedule

# 2. Auto Scaling
# Cluster Autoscaler
apiVersion: autoscaling.k8s.io/v1
kind: VerticalPodAutoscaler
metadata:
  name: myapp-vpa
spec:
  targetRef:
    apiVersion: "apps/v1"
    kind: Deployment
    name: myapp
  updatePolicy:
    updateMode: "Auto"
  resourcePolicy:
    containerPolicies:
    - containerName: app
      minAllowed:
        cpu: 100m
        memory: 128Mi
      maxAllowed:
        cpu: 1000m
        memory: 1Gi

# 3. 资源限制优化
resources:
  requests:   # 调度依据
    memory: "256Mi"
    cpu: "250m"
  limits:     # 硬限制
    memory: "512Mi"
    cpu: "500m"

# 4. 存储优化
# 使用生命周期策略
aws s3api put-bucket-lifecycle-configuration \
  --bucket mybucket \
  --lifecycle-configuration file://lifecycle.json

# lifecycle.json
{
  "Rules": [{
    "Id": "archive-old-logs",
    "Status": "Enabled",
    "Transitions": [{
      "Days": 30,
      "StorageClass": "STANDARD_IA"
    }, {
      "Days": 90,
      "StorageClass": "GLACIER"
    }],
    "Expiration": {
      "Days": 365
    }
  }]
}
```

**成本监控**:
```bash
# AWS Cost Explorer CLI
aws ce get-cost-and-usage \
  --time-period Start=2024-01-01,End=2024-01-31 \
  --granularity MONTHLY \
  --metrics "BlendedCost" "UsageQuantity" \
  --group-by Type=DIMENSION,Key=SERVICE

# Kubecost - Kubernetes成本分析
kubectl port-forward -n kubecost svc/kubecost-cost-analyzer 9090:9090
# 访问 http://localhost:9090
```

**预留实例策略**:
```yaml
策略:
1. 分析历史使用量
2. 稳定负载使用Reserved Instances (RI) / Savings Plans
3. 弹性负载使用Spot/Preemptible
4. 不可中断负载使用On-Demand

成本节省:
- Reserved Instances: 30-70% 折扣
- Spot Instances: 50-90% 折扣
- Savings Plans: 灵活的长期折扣
```

---

### 5. 安全最佳实践

**问题**: 云安全架构

**答案**:

**零信任架构**:
```yaml
# 1. 身份验证 - IAM最小权限
# AWS IAM Policy示例
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Action": [
      "s3:GetObject",
      "s3:PutObject"
    ],
    "Resource": "arn:aws:s3:::mybucket/app/*",
    "Condition": {
      "IpAddress": {
        "aws:SourceIp": ["10.0.0.0/8"]
      }
    }
  }]
}

# 2. 网络隔离
# Kubernetes Network Policy
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: api-policy
spec:
  podSelector:
    matchLabels:
      app: api
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: frontend
    ports:
    - protocol: TCP
      port: 8080
  egress:
  - to:
    - podSelector:
        matchLabels:
          app: database
    ports:
    - protocol: TCP
      port: 5432

# 3. 密钥管理
# 使用Kubernetes External Secrets
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: app-secrets
spec:
  refreshInterval: 1h
  secretStoreRef:
    name: aws-secrets-manager
    kind: SecretStore
  target:
    name: app-secrets
  data:
  - secretKey: database-password
    remoteRef:
      key: prod/database
      property: password

# 4. 镜像扫描
# Trivy扫描
trivy image --severity HIGH,CRITICAL myapp:v1.2.3

# 5. Pod Security Standards
apiVersion: v1
kind: Namespace
metadata:
  name: production
  labels:
    pod-security.kubernetes.io/enforce: restricted
    pod-security.kubernetes.io/audit: restricted
    pod-security.kubernetes.io/warn: restricted
```

**合规和审计**:
```bash
# AWS CloudTrail - 审计所有API调用
aws cloudtrail create-trail \
  --name mytrail \
  --s3-bucket-name mytrail-logs

# 启用日志文件验证
aws cloudtrail update-trail \
  --name mytrail \
  --enable-log-file-validation

# 查询API调用
aws cloudtrail lookup-events \
  --lookup-attributes AttributeKey=EventName,AttributeValue=CreateBucket \
  --max-results 10

# Config Rules - 合规检查
aws configservice put-config-rule \
  --config-rule file://s3-bucket-public-read-prohibited.json
```

---

## 总结

### GitOps面试重点

✅ **核心原则**: 声明式、Git单一来源、自动化、持续协调  
✅ **工具**: Argo CD, Flux, Helm  
✅ **安全**: Sealed Secrets, SOPS, External Secrets  
✅ **最佳实践**: 多环境管理、App of Apps模式

### DevOps面试重点

✅ **CI/CD**: GitHub Actions, GitLab CI, Jenkins  
✅ **容器**: Docker多阶段构建、镜像优化  
✅ **Kubernetes**: Deployment, Service, Ingress, HPA  
✅ **监控**: Prometheus, Grafana, 告警规则  
✅ **日志**: ELK, Loki, 结构化日志

### 云计算面试重点

✅ **服务模型**: IaaS, PaaS, SaaS区别  
✅ **AWS核心**: EC2, S3, RDS, VPC, IAM  
✅ **云原生**: 12 Factor, 微服务, 服务网格  
✅ **成本优化**: Spot实例、Auto Scaling、生命周期策略  
✅ **安全**: 零信任、最小权限、密钥管理、网络隔离

---

**最终准备建议**:
1. **手写代码**: 不要只看，要亲自写
2. **理解原理**: 知其然，知其所以然
3. **实战经验**: 结合项目经历讲述
4. **性能意识**: 关注时间/空间复杂度
5. **最佳实践**: 了解社区推荐做法
6. **全栈融会贯通**: Shell脚本自动化、Node.js后端、Vue.js前端、Kubernetes编排
7. **DevOps思维**: 自动化一切，基础设施即代码，持续交付

**推荐资源**:
- Python: 《Fluent Python》《Effective Python》
- Golang: 《The Go Programming Language》《Go语言高级编程》
- Shell: 《Linux命令行与Shell脚本编程大全》
- Node.js: 《深入浅出Node.js》《Node.js设计模式》
- Vue.js: 《Vue.js设计与实现》官方文档
- DevOps: 《凤凰项目》《持续交付》《Kubernetes权威指南》
- 云计算: AWS/GCP/Azure官方文档、《云原生应用架构实践》
- GitOps: Argo CD官方文档、《GitOps and Kubernetes》
- 在线练习: LeetCode、牛客网、力扣
