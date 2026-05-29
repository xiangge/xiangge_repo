# NVIDIA Solution Engineering 面试准备文档

---

## 一、Python & Scripting

### Q1: 写一个脚本监控GPU利用率和显存使用，当超过阈值时告警

```python
#!/usr/bin/env python3
"""GPU监控脚本：利用nvidia-smi采集指标，超过阈值时告警并记录日志。"""

import subprocess
import json
import time
import logging
import sys
from dataclasses import dataclass
from typing import List

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)


@dataclass
class GPUStatus:
    index: int
    name: str
    utilization_gpu: int    # GPU核心利用率 (%)
    utilization_memory: int # 显存利用率 (%)
    memory_used_mb: int
    memory_total_mb: int
    temperature: int        # 温度 (摄氏度)

    @property
    def memory_percent(self) -> float:
        return (self.memory_used_mb / self.memory_total_mb) * 100


class GPUMonitor:
    def __init__(self, gpu_util_threshold=90, mem_threshold=90, temp_threshold=85):
        self.gpu_util_threshold = gpu_util_threshold
        self.mem_threshold = mem_threshold
        self.temp_threshold = temp_threshold

    def query_gpus(self) -> List[GPUStatus]:
        """调用nvidia-smi获取GPU状态，返回结构化数据。"""
        cmd = [
            'nvidia-smi',
            '--query-gpu=index,name,utilization.gpu,utilization.memory,memory.used,memory.total,temperature.gpu',
            '--format=csv,noheader,nounits'
        ]
        try:
            output = subprocess.check_output(cmd, text=True, timeout=10)
        except subprocess.TimeoutExpired:
            logger.error("nvidia-smi 命令超时")
            return []
        except FileNotFoundError:
            logger.error("nvidia-smi 未找到，请确认NVIDIA驱动已安装")
            sys.exit(1)

        gpus = []
        for line in output.strip().split('\n'):
            if not line.strip():
                continue
            parts = [p.strip() for p in line.split(',')]
            gpus.append(GPUStatus(
                index=int(parts[0]),
                name=parts[1],
                utilization_gpu=int(parts[2]),
                utilization_memory=int(parts[3]),
                memory_used_mb=int(parts[4]),
                memory_total_mb=int(parts[5]),
                temperature=int(parts[6]),
            ))
        return gpus

    def check_and_alert(self, gpu: GPUStatus):
        """根据阈值判断是否需要告警。"""
        alerts = []
        if gpu.utilization_gpu > self.gpu_util_threshold:
            alerts.append(f"GPU利用率 {gpu.utilization_gpu}% > {self.gpu_util_threshold}%")
        if gpu.memory_percent > self.mem_threshold:
            alerts.append(f"显存占用 {gpu.memory_percent:.1f}% > {self.mem_threshold}%")
        if gpu.temperature > self.temp_threshold:
            alerts.append(f"温度 {gpu.temperature}°C > {self.temp_threshold}°C")
        if alerts:
            logger.warning(f"GPU[{gpu.index}] {gpu.name}: {'; '.join(alerts)}")
        return bool(alerts)

    def run(self, interval=5):
        """持续监控循环。"""
        logger.info(
            f"GPU监控已启动，间隔={interval}s, GPU阈值={self.gpu_util_threshold}%, "
            f"显存阈值={self.mem_threshold}%, 温度阈值={self.temp_threshold}°C"
        )
        while True:
            gpus = self.query_gpus()
            for gpu in gpus:
                self.check_and_alert(gpu)
            time.sleep(interval)


if __name__ == '__main__':
    monitor = GPUMonitor(gpu_util_threshold=90, mem_threshold=90, temp_threshold=85)
    monitor.run()
```

**延伸知识：**

- `nvidia-smi` 本质是通过 NVIDIA Management Library (NVML) 与驱动通信，Python 可直接调用 `pynvml` 库获得更低延迟和更细粒度的数据，无需走子进程。
- 生产环境中不应仅靠利用率判断健康度——SM（Streaming Multiprocessor）占用率高不一定代表计算效率高，还需关注 `nvidia-smi dmon` 输出的 SM efficiency 等指标。
- 如果要在 K8s 中做 GPU 监控，可以用 **DCGM (Data Center GPU Manager)** + Prometheus + Grafana 方案，DCGM Exporter 会自动暴露丰富的 GPU 指标。

---

### Q2: Python GIL是什么？在CPU密集型任务中如何绕过它？

**GIL (Global Interpreter Lock)** 是 CPython 解释器中的一个互斥锁，它保证同一时刻只有一个线程在执行 Python 字节码。这意味着即使在多核 CPU 上，CPython 的多线程也无法真正并行执行 CPU 密集型任务。

**为什么有GIL？** CPython 的内存管理（引用计数）不是线程安全的，GIL 是最简单的解决方案。去掉 GIL 需要对整个解释器做细粒度锁改造（Python 3.13 已开始实验性支持 no-GIL 模式）。

**绕过方案：**

| 方案 | 适用场景 | 原理 |
|------|---------|------|
| `multiprocessing` | CPU密集型 | 每个进程有独立的Python解释器和GIL，真正并行 |
| `concurrent.futures.ProcessPoolExecutor` | CPU密集型 | multiprocessing的高层封装，更易用 |
| C扩展 / Cython | CPU密集型 | 在C代码中手动释放GIL，执行计算 |
| `numpy` / `numba` | 数值计算 | NumPy底层用C/Fortran实现，释放GIL；Numba JIT编译后也释放GIL |
| `asyncio` | IO密集型 | 单线程协程，根本不涉及多线程竞争 |

```python
# ProcessPoolExecutor 示例
from concurrent.futures import ProcessPoolExecutor
import math

def compute_prime_factors(n):
    factors = []
    d = 2
    while d * d <= n:
        while n % d == 0:
            factors.append(d)
            n //= d
        d += 1
    if n > 1:
        factors.append(n)
    return factors

numbers = [10**15 + i for i in range(100)]

# 每个进程有独立的GIL，真正并行
with ProcessPoolExecutor(max_workers=8) as executor:
    results = list(executor.map(compute_prime_factors, numbers))
```

**Python 3.13+ 的 no-GIL 模式：**

```bash
# 编译带 --disable-gil 的 Python，或使用 3.13+ 的 free-threaded 构建
python3.13t -X gil=0 script.py
```

但生态兼容性还需要时间，大量 C 扩展尚未适配。

---

### Q3: 如何用subprocess调用外部命令并捕获stdout/stderr超时？

```python
import subprocess
import shlex

def run_command(cmd, timeout=30):
    """
    安全地执行外部命令，返回 (returncode, stdout, stderr)。

    关键设计：
    1. 用 list 而非字符串传递命令，避免 shell 注入
    2. capture_output=True 捕获 stdout/stderr 到管道
    3. text=True 自动解码为字符串
    4. timeout 参数防止命令无限挂起
    """
    try:
        result = subprocess.run(
            cmd,                          # list形式，如 ['ls', '-la']
            capture_output=True,          # 捕获stdout和stderr
            text=True,                    # 以文本模式返回（Python 3.7+）
            timeout=timeout,              # 超时后抛出 TimeoutExpired
            check=False,                  # 不自动抛出异常，手动检查returncode
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return -1, "", f"命令执行超时 (>{timeout}s)"
    except FileNotFoundError:
        return -1, "", "命令未找到"

# 使用示例
ret, out, err = run_command(['nvidia-smi', '--query-gpu=name', '--format=csv,noheader'])
print(f"returncode={ret}, stdout={out.strip()}, stderr={err}")
```

**场景：管道命令**

```python
# 等价于: ps aux | grep python
ps = subprocess.Popen(['ps', 'aux'], stdout=subprocess.PIPE, text=True)
grep = subprocess.Popen(['grep', 'python'], stdin=ps.stdout, stdout=subprocess.PIPE, text=True)
ps.stdout.close()  # 关键：让ps的stdout关闭，否则grep会一直等待
output = grep.communicate()[0]
```

不要用 `shell=True` + 字符串拼接——那是命令注入漏洞的根源。必须用时用 `shlex.quote()` 转义参数。

---

### Q4: 写一个装饰器，实现函数级别的重试和超时控制

```python
import time
import signal
import functools
from typing import Type, Tuple

class TimeoutError(Exception):
    pass

def timeout(seconds: int):
    """超时装饰器：函数执行超过指定秒数则抛出TimeoutError。"""
    def decorator(func):
        def _handle_timeout(signum, frame):
            raise TimeoutError(f"{func.__name__} 执行超过 {seconds}s")

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # 设置alarm信号
            old_handler = signal.signal(signal.SIGALRM, _handle_timeout)
            signal.alarm(seconds)
            try:
                result = func(*args, **kwargs)
            finally:
                signal.alarm(0)  # 取消alarm
                signal.signal(signal.SIGALRM, old_handler)  # 恢复原handler
            return result
        return wrapper
    return decorator


def retry(max_attempts: int = 3, delay: float = 1.0, backoff: float = 2.0,
          exceptions: Tuple[Type[Exception], ...] = (Exception,)):
    """
    重试装饰器：捕获指定异常后自动重试。

    参数：
    - max_attempts: 最大尝试次数（包含首次）
    - delay: 初始等待秒数
    - backoff: 退避倍数（指数退避）
    - exceptions: 需要重试的异常类型
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            current_delay = delay
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    if attempt == max_attempts:
                        raise  # 最后一次仍失败则抛出
                    print(f"[重试] {func.__name__} 第{attempt}次失败: {e}, "
                          f"{current_delay}s后重试...")
                    time.sleep(current_delay)
                    current_delay *= backoff
            return None  # unreachable
        return wrapper
    return decorator


# ---- 组合使用 ----
@retry(max_attempts=3, delay=1, backoff=2, exceptions=(TimeoutError, ConnectionError))
@timeout(seconds=10)
def fetch_gpu_status():
    """获取GPU状态，超时或连接错误时自动重试，最多3次。"""
    # 模拟可能失败的GPU查询
    pass
```

**信号方式的局限性：**
- `signal.alarm` 只在主线程有效，子线程中无法使用
- 对于线程场景，推荐用 `concurrent.futures.ThreadPoolExecutor` + `future.result(timeout=...)` 实现超时

```python
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeout

def timeout_with_thread(seconds):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            with ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(func, *args, **kwargs)
                try:
                    return future.result(timeout=seconds)
                except FutureTimeout:
                    raise TimeoutError(f"{func.__name__} 执行超过 {seconds}s")
        return wrapper
    return decorator
```

---

### Q5: 如何调试卡住的Python服务？用过哪些profiling工具？

**调试卡住（hang）的服务：**

1. **`py-spy`** — 不需要修改代码，直接dump进程的当前调用栈：
   ```bash
   py-spy dump --pid <PID>        # 打印当前所有线程的调用栈
   py-spy top --pid <PID>         # 实时显示函数耗时排行
   ```
   能立即看出线程卡在 `time.sleep()`、`socket.recv()` 还是某个死循环。

2. **`gdb` + python 扩展** — 在更底层排查：
   ```bash
   gdb -p <PID>
   (gdb) py-bt      # 打印Python调用栈
   (gdb) info threads
   (gdb) thread apply all py-bt   # 打印所有线程的Python栈
   ```

3. **`faulthandler`** — Python内置，预先加载，故障时自动dump栈：
   ```python
   import faulthandler
   import signal
   faulthandler.register(signal.SIGUSR1)  # 收到SIGUSR1时dump所有线程栈
   # 或直接
   faulthandler.dump_traceback_later(30)    # 30秒后自动dump
   ```
   之后 `kill -SIGUSR1 <PID>` 就能看到stack trace。

4. **`strace`** — 查看系统调用层面在做什么：
   ```bash
   strace -p <PID> -f -t   # -f跟踪所有线程，-t显示时间戳
   ```
   如果卡在 `futex` 或 `recvfrom`，说明在等锁或等网络数据。

**Profiling工具：**

| 工具 | 用途 | 亮点 |
|------|------|------|
| `cProfile` + `snakeviz` | CPU profiling | Python内置，snakeviz提供火焰图可视化 |
| `py-spy` | 实时CPU采样 | 无需改代码，可attach到运行中的进程 |
| `memray` | 内存分析 | Bloomberg开源，可追踪内存分配、泄漏 |
| `tracemalloc` | 内存追踪 | Python内置，快速定位内存增长的代码行 |
| `line_profiler` | 逐行分析 | 精确到每行代码的执行时间 |
| `scalene` | CPU+内存+GPU | 一个工具同时分析三种资源，GPU分析独有 |

```bash
# cProfile 使用示例
python -m cProfile -o output.prof my_script.py
snakeviz output.prof  # 在浏览器中查看火焰图
```

---

### Q6: `*args` 和 `**kwargs` 的区别和使用场景

| | `*args` | `**kwargs` |
|---|---|---|
| 全称 | arguments (positional) | keyword arguments |
| 类型 | `tuple` | `dict` |
| 捕获 | 多余的**位置**参数 | 多余的**关键字**参数 |
| 语法 | `*` 前缀 | `**` 前缀 |

```python
def demo(a, b, *args, **kwargs):
    print(f"a={a}, b={b}")          # a=1, b=2
    print(f"args={args}")           # args=(3, 4, 5)
    print(f"kwargs={kwargs}")       # kwargs={'x': 10, 'y': 20}

demo(1, 2, 3, 4, 5, x=10, y=20)
```

**实际场景：**

```python
# 1. 装饰器：透传任意参数
def log_call(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        print(f"调用 {func.__name__}, args={args}, kwargs={kwargs}")
        return func(*args, **kwargs)
    return wrapper

# 2. 子类构造器：不关心父类有哪些参数
class MyModel(ParentModel):
    def __init__(self, my_param, **kwargs):
        super().__init__(**kwargs)  # 透传所有父类需要的参数
        self.my_param = my_param

# 3. API请求封装：灵活传递可选参数
def gpu_query(endpoint, **params):
    """params可以是limit, offset, filter等任意可选参数"""
    url = f"https://api.example.com/{endpoint}"
    return requests.get(url, params=params)
```

**延伸：`*` 还可用来强制关键字参数（PEP 3102）：**

```python
def configure_gpu(device_id, *, memory_limit=None, compute_mode=None):
    """`*` 之后的所有参数必须用关键字形式传递"""
    pass

configure_gpu(0, memory_limit=4096)  # ✅
configure_gpu(0, 4096)               # ❌ TypeError
```

---

### Q7: 如何写一个并发下载多个文件的Python程序？

三种并发模型的对比：

| 模型 | 原理 | 适合场景 | 限制 |
|------|------|---------|------|
| `threading` | 多个线程共享内存 | IO密集型（网络下载） | GIL限制CPU并行，但IO时会释放GIL |
| `multiprocessing` | 多个进程独立内存 | CPU密集型 | 进程间通信开销大 |
| `asyncio` | 单线程事件循环 | 高并发IO（数万连接） | 需要异步库支持（aiohttp, aiofiles） |

对于文件下载（IO密集型），**threading和asyncio都合适**，asyncio在超高并发时更省资源：

```python
# 方案A: ThreadPoolExecutor — 简单直接
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests

def download_file(url, dest):
    resp = requests.get(url, stream=True, timeout=30)
    resp.raise_for_status()
    with open(dest, 'wb') as f:
        for chunk in resp.iter_content(chunk_size=8192):
            f.write(chunk)
    return f"{dest} 下载完成, size={len(open(dest, 'rb').read())}"

urls = [
    ("https://example.com/file1.bin", "/tmp/file1.bin"),
    ("https://example.com/file2.bin", "/tmp/file2.bin"),
]

with ThreadPoolExecutor(max_workers=5) as executor:
    futures = {executor.submit(download_file, url, dest): url for url, dest in urls}
    for future in as_completed(futures):
        try:
            print(future.result())
        except Exception as e:
            print(f"下载失败 {futures[future]}: {e}")
```

```python
# 方案B: asyncio + aiohttp — 高并发首选
import asyncio
import aiohttp
import aiofiles

async def download_async(session, url, dest):
    async with session.get(url, timeout=aiohttp.ClientTimeout(total=30)) as resp:
        resp.raise_for_status()
        async with aiofiles.open(dest, 'wb') as f:
            async for chunk in resp.content.iter_chunked(8192):
                await f.write(chunk)
    return f"{dest} done"

async def main():
    async with aiohttp.ClientSession() as session:
        tasks = [download_async(session, url, dest) for url, dest in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        for r in results:
            print(r)

asyncio.run(main())
```

**延伸：信号量控制并发数**

```python
semaphore = asyncio.Semaphore(10)  # 最多10个并发

async def bounded_download(session, url, dest):
    async with semaphore:
        return await download_async(session, url, dest)
```

---

### Q8: Shell脚本——一键排查GPU节点健康状态

```bash
#!/bin/bash
# gpu_health_check.sh — GPU节点一键健康检查

set -e
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

pass_count=0
fail_count=0

check() {
    local desc="$1"
    shift
    if "$@" > /dev/null 2>&1; then
        echo -e "  [${GREEN}PASS${NC}] $desc"
        ((pass_count++))
    else
        echo -e "  [${RED}FAIL${NC}] $desc"
        ((fail_count++))
    fi
}

echo "========== GPU Node Health Check =========="

# 1. NVIDIA驱动
check "NVIDIA驱动已加载" lsmod | grep -q nvidia
check "nvidia-smi可用" nvidia-smi > /dev/null 2>&1

# 2. CUDA版本
CUDA_VERSION=$(nvidia-smi --query-gpu=driver_version --format=csv,noheader | head -1)
echo "  驱动版本: $CUDA_VERSION"
nvcc --version 2>/dev/null | grep "release" || echo "  nvcc 未安装或不在PATH中"

# 3. GPU数量和基本信息
GPU_COUNT=$(nvidia-smi --query-gpu=name --format=csv,noheader | wc -l)
echo "  GPU数量: $GPU_COUNT"
nvidia-smi --query-gpu=index,name,memory.total,temperature.gpu --format=csv,noheader 2>/dev/null

# 4. GPU错误检查 (Xid errors)
check "无GPU Xid错误" ! dmesg | grep -i "NVRM: Xid" > /dev/null 2>&1
# 如有则显示
dmesg 2>/dev/null | grep -i "NVRM: Xid" | tail -5 || true

# 5. Docker runtime
check "Docker已安装" docker --version > /dev/null 2>&1
check "nvidia-docker runtime已配置" docker info 2>/dev/null | grep -q nvidia || \
    (command -v nvidia-container-runtime > /dev/null 2>&1)

# 6. nvidia-container-toolkit
check "nvidia-container-toolkit已安装" dpkg -l nvidia-container-toolkit 2>/dev/null | grep -q ii || \
    rpm -q nvidia-container-toolkit 2>/dev/null

# 7. K8s（如果存在）
if command -v kubectl &>/dev/null; then
    check "kubectl可用" kubectl version --client > /dev/null 2>&1
    check "nvidia-device-plugin DaemonSet运行中" kubectl get pods -n kube-system 2>/dev/null | grep nvidia-device-plugin | grep Running
fi

# 8. GPU ECC错误
check "无GPU ECC错误" ! nvidia-smi --query-gpu=ecc.errors.corrected.volatile.total,ecc.errors.uncorrected.volatile.total --format=csv,noheader 2>/dev/null | grep -v "0, 0"

# 9. 电源和性能模式
echo "  电源状态和性能模式:"
nvidia-smi --query-gpu=index,pstate,power.draw,clocks.sm --format=csv,noheader 2>/dev/null

# 10. 系统资源
echo "  CPU: $(nproc) cores"
echo "  Memory: $(free -h | awk '/Mem:/{print $2}')"
echo "  Disk: $(df -h / | awk 'NR==2{print $4}') available"

echo ""
echo "========== Summary: ${GREEN}${pass_count} PASS${NC}, ${RED}${fail_count} FAIL${NC} =========="
[ $fail_count -eq 0 ] && echo "✅ GPU节点健康" || echo "❌ 存在异常，请排查"
```

---

## 二、Linux 系统深度

### Q1: 一个进程占用CPU 100%，如何定位它在干什么？

**分层排查流程：**

```bash
# Step 1: 找到高CPU进程
top -c -o %CPU          # 按CPU排序，c显示完整命令行

# Step 2: 查看线程级CPU分布
top -H -p <PID>          # -H显示线程，看哪个线程在吃CPU

# Step 3: 查看进程当前在做什么系统调用
strace -c -p <PID>       # 统计系统调用频率
strace -p <PID> -e trace=write,read  # 只看特定调用

# Step 4: 用perf看进程在哪个函数花时间（代码级热点）
perf top -p <PID>                          # 实时函数采样
perf record -p <PID> -g -- sleep 10        # 记录10秒，-g记录调用链
perf report                                # 查看报告

# Step 5: 如果是Python进程，dump调用栈
py-spy dump --pid <PID>
py-spy top --pid <PID>   # 实时看哪个函数最热
```

**常见根因及特征：**

| 症状 | 常见原因 | 排查命令 |
|------|---------|---------|
| 用户态CPU高 | 死循环、算法复杂度过高 | `perf top` 看函数 |
| 系统态CPU高(sys%) | 频繁系统调用、上下文切换 | `strace -c` 统计调用 |
| I/O wait高(wa%) | 磁盘/网络IO阻塞 | `iotop`, `iostat` |
| 单线程高，其他空闲 | 单线程瓶颈 | `top -H` 定位线程 |

---

### Q2: 如何查看一个进程打开了哪些文件、哪些网络连接？

```bash
PID=12345

# 方法1: lsof — 最全面
lsof -p $PID              # 所有打开的文件、socket、pipe
lsof -p $PID -i           # 仅网络连接
lsof -p $PID | grep REG   # 仅普通文件

# 方法2: /proc 文件系统 — 无需安装额外工具
ls -la /proc/$PID/fd/           # 所有文件描述符
ls -la /proc/$PID/fd/ | grep socket  # socket文件描述符
cat /proc/$PID/net/tcp          # TCP连接（hex格式）
cat /proc/$PID/net/unix         # Unix domain socket

# 更人性化的网络连接查看
ss -tnp | grep "pid=$PID"       # TCP连接
ss -unp | grep "pid=$PID"       # UDP连接
```

**延伸：`lsof` 的使用场景**

```bash
# 查看端口被谁占用
lsof -i :8080

# 查看某个用户打开的所有文件
lsof -u nvidia

# 查看某个目录下被打开的文件
lsof +D /var/log

# 查看删除了但进程还持有句柄的文件（磁盘空间不释放的常见原因）
lsof | grep deleted
```

当磁盘空间满了但 `du` 看不到大文件时，很可能就是某个进程持有已删除的大文件句柄，用 `lsof | grep deleted` 找到后重启该进程即可释放空间。

---

### Q3: Linux内存管理：buffer/cache、swap、OOM killer

**free 命令输出解读：**

```bash
$ free -h
              total        used        free      shared  buff/cache   available
Mem:           62Gi        30Gi        10Gi       500Mi        22Gi        31Gi
Swap:         8.0Gi       2.0Gi       6.0Gi
```

| 字段 | 含义 |
|------|------|
| `total` | 物理内存总量 |
| `used` | 进程实际使用的内存（不含cache） |
| `free` | 完全未被使用的内存 |
| `buff/cache` | 内核用于缓存磁盘数据的页（可随时回收） |
| `available` | **关键指标**——新进程可申请的内存估算值（已考虑可回收的cache） |
| `shared` | tmpfs（如/dev/shm）使用的内存，跨进程共享 |

**Buffer vs Cache：**
- **Buffer**：块设备的元数据缓存（如inode、superblock）
- **Page Cache（free中的cache）**：文件内容页缓存。当进程读文件时，内核将内容缓存于page cache，下次读取命中则无需磁盘IO

**Linux 总是"看起来内存满了"——这是设计行为不是bug。** 空闲内存 = 浪费的内存，内核会积极使用剩余内存作为磁盘缓存。真正需要关注的是 `available` 字段。

**Swap：**
- 当物理内存不足时，内核将不活跃的匿名页（非文件映射的进程内存）换出到磁盘
- `swappiness` (0-100)：控制内核换出的倾向，值越高越积极使用swap（默认为60）
- 对于跑GPU训练任务的机器，一般建议设低（如10），避免频繁swap影响性能
- `vm.swappiness=10` 写入 `/etc/sysctl.conf`

**OOM Killer：**

当内存彻底耗尽，内核必须杀死某个进程来释放内存。选择策略基于 `oom_score`：
```bash
cat /proc/<PID>/oom_score      # 当前OOM评分（越高越可能被kill）
cat /proc/<PID>/oom_score_adj  # 可手动调整（-1000到1000，-1000完全豁免）
```

关键日志：`dmesg | grep -i "killed process"` 或 `journalctl -k | grep oom`

**GPU场景特有的内存问题：**
- GPU显存OOM不等于系统内存OOM——`nvidia-smi` 看显存，`free` 看系统内存
- PyTorch默认会缓存显存分配器（caching allocator），`nvidia-smi` 显示的占用 > 实际tensor占用
- NCCL通信会额外消耗显存（通信buffer），这是分布式训练OOM的常见原因

---

### Q4: strace用过吗？程序报错"cannot open shared object file"，怎么定位？

```bash
# strace打印所有系统调用
strace -f -o /tmp/trace.log ./my_program

# 只看文件相关的调用（open/openat/stat）
strace -e trace=open,openat,stat,access ./my_program 2>&1 | grep "\.so"

# 输出示例：你会看到程序搜索了哪些路径、哪个.so没找到
# openat(AT_FDCWD, "/usr/lib/x86_64-linux-gnu/libcuda.so.1", O_RDONLY) = -1 ENOENT
# openat(AT_FDCWD, "/usr/local/cuda/lib64/libcuda.so.1", O_RDONLY) = -1 ENOENT
# ↑ 这就是原因——动态链接器在这些路径都没找到 .so
```

**完整排查链路：**

```bash
# 1. 查看可执行文件依赖哪些 .so
ldd ./my_program          # 显示依赖及找到的路径
ldd -r ./my_program       # -r 显示未解析的符号（relocation）

# 2. 查看动态链接器的搜索路径
ldconfig -p | grep libcuda    # 系统范围内搜索
cat /etc/ld.so.conf            # 链接器配置文件
ldconfig -v 2>/dev/null | grep -v "^$"  # 查看所有缓存路径

# 3. 如果.so在某目录但链接器不知道
LD_LIBRARY_PATH=/path/to/lib ./my_program   # 临时添加搜索路径
# 或永久添加：
echo "/path/to/lib" > /etc/ld.so.conf.d/myapp.conf
ldconfig

# 4. 容器场景：CUDA .so文件在哪？
# nvidia-container-toolkit 会自动将宿主机 CUDA 库挂载到容器内
# 确认：
ldconfig -p | grep cuda
ls /usr/local/cuda/lib64/
echo $LD_LIBRARY_PATH
```

**strace 常用技巧：**

```bash
# 统计各类系统调用的次数和时间
strace -c -p <PID>       # -c输出统计摘要

# 只看网络相关
strace -e trace=network -p <PID>

# 显示时间戳
strace -tt -p <PID>       # 微秒级时间戳

# 看子进程
strace -f -p <PID>
```

**延伸：为什么 `ldd` 可能不安全？** `ldd` 实际上会执行程序来解析依赖。对于不可信的二进制文件，应该用 `objdump -p /path/to/binary | grep NEEDED` 或 `readelf -d /path/to/binary | grep NEEDED` 代替。

---

### Q5: systemd service文件怎么写？如何设置重启策略和环境变量？

```ini
# /etc/systemd/system/gpu-monitor.service
[Unit]
Description=GPU Health Monitor Service
After=network.target docker.service     # 在网络和Docker之后启动
Wants=nvidia-persistenced.service       # 弱依赖（推荐但非必须）

[Service]
Type=simple                              # 主进程即为服务进程
User=gpu-admin                           # 以什么用户运行
Group=gpu-admin
WorkingDirectory=/opt/gpu-monitor
EnvironmentFile=/etc/gpu-monitor/env      # 从文件加载环境变量
Environment=NVIDIA_VISIBLE_DEVICES=all    # 直接设置环境变量
Environment=LOG_LEVEL=info

ExecStart=/usr/bin/python3 /opt/gpu-monitor/monitor.py
ExecStop=/bin/kill -s SIGTERM $MAINPID    # 优雅停止
ExecReload=/bin/kill -s SIGHUP $MAINPID   # reload信号

Restart=on-failure                        # 仅在异常退出时重启
RestartSec=10s                            # 重启前等待10秒
TimeoutStartSec=30s                       # 启动超时
TimeoutStopSec=30s                        # 停止超时

# 资源限制
LimitNOFILE=65536
MemoryMax=2G
CPUQuota=200%

# 标准输出重定向到journald
StandardOutput=journal
StandardError=journal
SyslogIdentifier=gpu-monitor

[Install]
WantedBy=multi-user.target                # 在多用户模式下启动
```

**Restart策略对比：**

| 值 | 行为 | 使用场景 |
|---|---|---|
| `no` | 永不重启 | 手动运行的一次性任务 |
| `always` | 无论什么退出原因都重启 | 核心守护进程 |
| `on-success` | 退出码为0时重启 | 任务型服务 |
| `on-failure` | 异常退出时重启（非0退出码/信号终止/超时） | **一般服务的推荐选择** |
| `on-abnormal` | 仅信号终止或超时时重启 | 允许正常退出 |

> 注意：`Restart=always` 可能导致BUG——如果服务因为配置错误启动就crash，systemd会陷入无限重启循环。配合 `StartLimitBurst` 和 `StartLimitIntervalSec` 可以限制重启频率。

```bash
# 操作命令
systemctl daemon-reload                # 修改service文件后必须执行
systemctl enable gpu-monitor.service   # 设置开机自启
systemctl start gpu-monitor.service
systemctl status gpu-monitor.service
journalctl -u gpu-monitor.service -f   # 查看实时日志
```

---

### Q6: 容器的entrypoint进程退出了但容器没退出，可能是什么原因？

这通常不是一个正确配置的容器行为——**容器的生命周期与PID 1的进程绑定**。但确实存在一些场景：

**原因分析：**

1. **多进程容器** — entrypoint进程fork了子进程后退出，但子进程仍在运行。例如用了 `tini` 或 `dumb-init` 作为PID 1，真正的entrypoint作为子进程。

2. **Entrypoint是shell脚本，脚本退出了但后台进程还在运行**：
   ```bash
   #!/bin/bash
   ./my_service &
   # 脚本结束了但my_service还在跑，因为&让它在后台运行
   ```
   实际上这种情况下容器通常还是会退出，因为bash进程退出时如果还有子进程，子进程会被SIGHUP。

3. **进程被 `exec` 替换了** — entrypoint里用了 `exec ./real_service`，看起来entrypoint退出了但其实是PID 1被替换成了real_service。

4. **Docker不是普通的init系统** — PID 1在容器内有特殊责任：它必须reap僵尸进程、正确处理信号。如果PID 1是一个不处理SIGCHLD的应用，僵尸进程会堆积。

**正确的容器设计模式：**

```dockerfile
# 使用tini作为init进程
RUN apt-get update && apt-get install -y tini
ENTRYPOINT ["/usr/bin/tini", "--"]
CMD ["/app/my_service"]

# 或者Docker 1.13+ 内置init
# docker run --init ...
```

---

### Q7: 如何给正在运行的进程绑定CPU核心（taskset/cgroups）？

```bash
# taskset — 最直接的方式
taskset -cp <PID>             # 查看进程当前绑在哪些CPU核心
taskset -cp 0-3 <PID>         # 绑定到CPU 0-3
taskset -cp 0,2,4,6 <PID>     # 绑定到指定核心（不连续）

# 启动时就绑定
taskset -c 0-7 python train.py
```

**在GPU场景中，CPU亲和性很重要：**
- GPU通常通过PCIe与特定CPU socket相连（NUMA拓扑）
- 如果GPU在NUMA node 0上，而进程的CPU核心在NUMA node 1上，数据搬运会跨QPI/UPI总线，显著增加延迟
- **理想做法**：将进程的CPU亲和性设为与GPU相同NUMA node的CPU核心

```bash
# 查看GPU/NUMA拓扑
nvidia-smi topo -m     # GPU拓扑矩阵
lscpu | grep NUMA      # NUMA node信息
numactl --hardware     # NUMA详细拓扑

# 将进程绑定到与GPU0同一NUMA node的CPU上
# 假设GPU0在NUMA node0，对应CPU核心0-15
numactl --cpunodebind=0 --membind=0 python train.py
# 或
taskset -c 0-15 python train.py
```

**cgroups v2 方式（更现代）：**
```bash
# 创建cgroup并设置CPU限制
mkdir -p /sys/fs/cgroup/gpu_training
echo "0-15" > /sys/fs/cgroup/gpu_training/cpuset.cpus
echo "0" > /sys/fs/cgroup/gpu_training/cpuset.mems  # NUMA node 0
echo "<PID>" > /sys/fs/cgroup/gpu_training/cgroup.procs
```

---

### Q8: 内核模块相关——`nvidia-smi`看不到GPU怎么排查？

这是生产环境中最常见的GPU问题之一。分层排查：

```bash
# Layer 1: 硬件层
lspci | grep -i nvidia          # GPU是否被BIOS识别到
lspci -s <PCI_BUS> -vv          # 查看PCI设备详细信息

# Layer 2: 内核驱动层
lsmod | grep nvidia             # nvidia内核模块是否加载
dmesg | grep -i nvidia | tail -20    # 驱动加载日志
dmesg | grep -i "NVRM"               # NVIDIA RM (Resource Manager) 日志

# 常见错误：驱动版本不匹配
cat /proc/driver/nvidia/version  # 驱动版本
nvidia-smi                       # CUDA toolkit中的工具版本
# 如果dmesg显示 "NVRM: API mismatch" — 驱动模块和用户态库版本不一致

# Layer 3: 设备文件层
ls -la /dev/nvidia*             # 设备文件是否存在
# 如果缺失：
nvidia-smi -pm 1                 # 开启持久化模式（自动创建设备节点）
# 或手动：
mknod /dev/nvidia0 c 195 0      # 创建字符设备

# Layer 4: 权限层
ls -la /dev/nvidia*             # 检查权限和owner
# Docker场景需要将nvidia devices映射进容器

# Layer 5: Docker/容器特有
# 确认nvidia-container-runtime已注册
cat /etc/docker/daemon.json | grep nvidia
docker info | grep -i runtime   # 确认Runtime列表中有nvidia

# 确认nvidia-container-toolkit配置正确
cat /etc/nvidia-container-runtime/config.toml
# 尤其注意 no-cgroups = false 确保GPU被正确分配给容器

# 容器内验证
docker run --rm --gpus all nvidia/cuda:12.0-base nvidia-smi
```

**延伸：常见失败模式及快速诊断表**

| 现象 | 关键命令 | 可能原因 |
|------|---------|---------|
| `nvidia-smi` 无输出/报连接错误 | `lsmod \| grep nvidia` | 驱动未加载、驱动损坏 |
| `nvidia-smi` 运行极慢 | `nvidia-smi -pm 1` | 持久化模式未开启 |
| 容器内无GPU | `echo $NVIDIA_VISIBLE_DEVICES` | nvidia-container-toolkit未安装 |
| `nvidia-smi` 提示版本不匹配 | `dmesg \| grep "API mismatch"` | 更新了用户态库但没重启（旧内核模块还在） |
| GPU掉卡（PCIe link down） | `dmesg \| grep "PCIe link"` | 硬件故障、过热、电源不足 |

---

## 三、Docker & Kubernetes

### Q1: Docker镜像分层的原理是什么？如何优化镜像大小？

**分层原理：**
Dockerfile中每条指令（RUN、COPY、ADD）创建一个新的层，每层是前一层的增量文件系统快照。层是只读的，通过 **UnionFS（Overlay2）** 叠加。容器运行时在最顶层加一个可写层。

```dockerfile
# 这个Dockerfile产生4个镜像层
FROM nvidia/cuda:12.0-base     # Layer 1: 基础镜像
RUN apt-get update              # Layer 2
RUN apt-get install -y python3  # Layer 3
COPY app.py /app/               # Layer 4
```

**优化策略：**

```dockerfile
# ❌ 差：每步一个RUN，层多且大
FROM nvidia/cuda:12.0-devel-ubuntu22.04
RUN apt-get update
RUN apt-get install -y python3
RUN apt-get install -y pip
RUN pip install torch
# 安装包缓存没有清理

# ✅ 好：合并RUN，清理缓存，多阶段构建
FROM nvidia/cuda:12.0-devel-ubuntu22.04 AS builder
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 python3-pip && \
    pip install --no-cache-dir torch && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# 多阶段构建：编译和运行分离
FROM nvidia/cuda:12.0-runtime-ubuntu22.04
COPY --from=builder /usr/local/lib/python3.10/dist-packages /usr/local/lib/python3.10/dist-packages
COPY app.py /app/
ENTRYPOINT ["python3", "/app/app.py"]
```

**常用优化要点：**
- `--no-install-recommends` 跳过推荐包
- `apt-get clean && rm -rf /var/lib/apt/lists/*` 清理apt缓存
- `pip install --no-cache-dir` 不保留pip下载缓存
- 用 `.dockerignore` 排除不需要的文件
- 多阶段构建（multi-stage build）：编译在devel镜像，运行在runtime镜像
- CUDA应用：运行时用 `nvidia/cuda:xx-runtime` 而非 `devel`（小几百MB）

---

### Q2: 多阶段构建Dockerfile——CUDA + PyTorch

```dockerfile
# Stage 1: 构建阶段
FROM nvidia/cuda:12.4.0-devel-ubuntu22.04 AS builder

# 安装编译依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3.10 python3.10-dev python3-pip git && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# 安装PyTorch（CUDA 12.4版本）
RUN pip install --no-cache-dir \
    torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124

# Stage 2: 运行阶段——使用更小的runtime镜像
FROM nvidia/cuda:12.4.0-runtime-ubuntu22.04

# 安装Python运行时
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3.10 python3-pip && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# 从builder复制已安装的包
COPY --from=builder /usr/local/lib/python3.10/dist-packages /usr/local/lib/python3.10/dist-packages

# 复制应用代码
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

# 设置环境变量
ENV NVIDIA_VISIBLE_DEVICES=all
ENV CUDA_VISIBLE_DEVICES=0

ENTRYPOINT ["python3", "train.py"]
```

`devel` vs `runtime` 镜像大小差异：通常 `devel` 比 `runtime` 大约 2-3GB（因为包含编译工具链、头文件等）。用多阶段构建可节省 GB 级别的大小。

---

### Q3: Docker网络模式有哪些？GPU容器通常用哪种？

| 模式 | 描述 | 适用场景 |
|------|------|---------|
| `bridge`（默认） | 通过docker0网桥+NAT与宿主机通信 | 单机容器，默认选择 |
| `host` | 直接使用宿主机网络栈，无隔离 | **GPU分布式训练首选** |
| `none` | 无网络 | 安全隔离场景 |
| `overlay` | 跨主机的容器网络 | Docker Swarm |
| `macvlan` | 容器拥有独立MAC地址 | 需要直接暴露在物理网络 |

**GPU容器为什么用 `--network=host`？**

NCCL（NVIDIA Collective Communications Library）做多GPU跨节点通信时，性能高度依赖网络延迟和带宽。用 `host` 模式的原因：
1. **消除NAT开销** — bridge模式多一层NAT，增加延迟
2. **RDMA/InfiniBand** — 高性能计算中GPU节点通过IB互联，只有host网络模式能直接访问IB设备
3. **NCCL通信发现** — NCCL需要节点间直接TCP连接，bridge模式下通信对端看到的源IP是docker0的IP而非宿主机IP，导致节点间通信失败

```bash
# GPU分布式训练典型启动命令
docker run --gpus all --network=host --ipc=host \
    -v /data:/data \
    pytorch:latest \
    torchrun --nnodes=2 --nproc_per_node=8 train.py
```

注意 `--ipc=host` 也很关键：PyTorch DataLoader多进程之间用共享内存通信，默认的IPC命名空间太小（64MB），会导致 `RuntimeError: DataLoader worker (pid xxx) is killed by signal: Bus error`。

---

### Q4: Pod一直处于Pending状态，如何排查？

这是K8s面试几乎必考的问题。**系统化排查方法：**

```bash
# 第一步：看Pod的Events——最直接的信息来源
kubectl describe pod <pod-name> -n <namespace>
# 关注Events部分的最后几条信息

# 第二步：看Pod的Conditions
kubectl get pod <pod-name> -o jsonpath='{.status.conditions}' | jq .
```

**常见Pending原因及排查方向：**

| Events关键信息 | 原因 | 排查 |
|---|---|---|
| `0/N nodes are available: insufficient nvidia.com/gpu` | GPU资源不足 | `kubectl describe nodes \| grep nvidia` 看各节点GPU容量和分配情况 |
| `0/N nodes are available: insufficient cpu/memory` | CPU/内存不足 | `kubectl top nodes` 看实际使用 |
| `pod has unbound immediate PersistentVolumeClaims` | PVC未绑定 | `kubectl get pvc` 看PVC状态 |
| `node(s) had taint {key: value} that the pod didn't tolerate` | Taint/Toleration不匹配 | `kubectl describe node \| grep Taint` 查看节点污点 |
| `node(s) didn't match node selector` | nodeSelector/affinity不满足 | 检查Pod的nodeSelector配置 vs 节点Labels |
| (无Events，长时间Pending) | Scheduler未调度 | `kubectl get events --all-namespaces \| grep scheduler` |

**GPU资源不足的深入排查：**

```bash
# 查看各节点的GPU容量
kubectl get nodes -o custom-columns=\
"NODE:.metadata.name,\
GPU_CAPACITY:.status.capacity.nvidia\.com/gpu,\
GPU_ALLOCATABLE:.status.allocatable.nvidia\.com/gpu"

# 查看哪些Pod在使用GPU
kubectl get pods --all-namespaces -o json | \
  jq -r '.items[] | select(.spec.containers[].resources.limits."nvidia.com/gpu" != null) | 
  "\(.metadata.namespace)/\(.metadata.name) node=\(.spec.nodeName) gpu=\(.spec.containers[].resources.limits."nvidia.com/gpu")"'
```

---

### Q5: K8s调度器如何工作？GPU Pod如何调度到正确的节点？

**调度器核心流程：**

1. **Filtering（过滤）**：排除不满足要求的节点（资源不足、taint不匹配、nodeSelector不满足等）
2. **Scoring（打分）**：对剩余节点按策略打分（资源均衡、亲和性等）
3. **Binding（绑定）**：选择最高分节点，将Pod绑定到该节点

**GPU调度的关键组件：**
- **nvidia-device-plugin**（DaemonSet）：在每个GPU节点上运行，向kubelet注册 `nvidia.com/gpu` 资源，使调度器知道哪些节点有GPU、各有多少
- **GPU Operator**（Red Hat主导）：将device plugin、驱动、container toolkit等封装为统一的K8s Operator，简化GPU集群管理

```yaml
# GPU Pod的资源声明
apiVersion: v1
kind: Pod
metadata:
  name: gpu-training
spec:
  containers:
  - name: trainer
    image: pytorch/pytorch:latest
    resources:
      limits:
        nvidia.com/gpu: 2     # 申请2个GPU（必须设置，否则不会分配GPU）
    env:
    - name: NVIDIA_VISIBLE_DEVICES
      value: "all"
  # 确保被调度到有GPU的节点（可选，device plugin已足够）
  nodeSelector:
    accelerator: nvidia-tesla-v100   # 如需指定GPU型号
```

**延伸：GPU共享和时间切片**

K8s默认一个GPU只能分配给一个容器。MIG (Multi-Instance GPU) 技术可以将A100/H100切分为多个独立实例：

```bash
# 在节点上启用MIG
nvidia-smi -i 0 -mig 1
# 创建GPU实例
nvidia-smi mig -cgi 9,9,9,9 -C
```

K8s 1.27+ 支持MIG设备插件，可将每个MIG实例作为独立资源调度。

---

### Q6: nvidia-device-plugin和GPU Operator

**nvidia-device-plugin（基础层）：**

作用：在每个GPU节点上以DaemonSet运行，向kubelet注册GPU资源的可用性。工作原理：
1. 启动时通过NVML库枚举节点上的GPU
2. 向kubelet的Device Plugin API注册 `nvidia.com/gpu` 资源
3. kubelet据此更新节点的allocatable资源
4. 调度器根据资源需求将GPU Pod分配到相应节点
5. Pod创建时，device plugin将宿主机的 `/dev/nvidia*` 设备映射到容器内，并设置 `NVIDIA_VISIBLE_DEVICES` 环境变量

**GPU Operator（管理层，由NVIDIA + Red Hat/Konflux生态推动）：**

在device plugin之上封装了完整的GPU软件栈：
- **驱动安装**：自动在每个节点安装匹配的NVIDIA驱动（通过Driver Container）
- **nvidia-container-toolkit**：配置Docker/containerd的nvidia runtime
- **device plugin**：注册GPU资源
- **DCGM Exporter**：GPU监控指标暴露
- **MIG Manager**：管理MIG分区
- **Node Feature Discovery**：自动给节点打上GPU型号等label

**面试要点：** 如果你说"我知道GPU Operator"，面试官可能会追问"它解决了什么问题"。核心答案——**它将GPU节点的全生命周期管理（驱动安装→运行时配置→资源注册→监控）统一为单一K8s Operator，消除了手动在每个节点上安装驱动和配置运行时的运维负担。**

---

### Q7: ConfigMap和Secret的区别？如何热更新？

| | ConfigMap | Secret |
|---|---|---|
| 用途 | 非敏感的配置数据 | 敏感数据（密码、Token、证书） |
| 存储 | 明文存储在etcd中 | Base64编码存储（可配合etcd加密） |
| 大小限制 | 1MB | 1MB |
| 使用方式 | envFrom / volume mount / 命令行参数 | 同ConfigMap |

**热更新机制：**
- 以**环境变量**注入的ConfigMap/Secret **不会**热更新——Pod必须重启
- 以**Volume挂载**的ConfigMap/Secret **会**热更新——kubelet定期同步（默认约60-90秒），但应用需要reload才能感知

```yaml
# Volume挂载方式（支持热更新）
volumes:
- name: config
  configMap:
    name: my-config
containers:
- volumeMounts:
  - name: config
    mountPath: /etc/config
```

**延伸：应用如何感知ConfigMap更新？**
- 监听文件变化（如 `inotify`）
- 通过 `/etc/config/..data` 符号链接的变化判断
- 或者通过sidecar发送SIGHUP信号给主进程触发reload

---

### Q8: CrashLoopBackOff和ImagePullBackOff的排查

**CrashLoopBackOff：**

意味着容器启动后立即退出，K8s反复重启。排查步骤：

```bash
# 1. 看Pod Events
kubectl describe pod <pod-name> | grep -A 20 Events
# 重点关注 Restart Count 和 Last State 的 Exit Code

# 2. 查看上一个崩溃容器的日志
kubectl logs <pod-name> --previous  # --previous 看上一次的日志！

# 3. 常见Exit Code含义
# Exit Code 0:  正常退出（但restartPolicy导致重启）
# Exit Code 1:  应用错误
# Exit Code 137: 被SIGKILL杀死（通常是OOM或资源限制）—— 重点排查！
# Exit Code 139: SIGSEGV 段错误
# Exit Code 143: SIGTERM 优雅终止

# 4. 如果是Exit Code 137，检查是否OOMKilled
kubectl describe pod <pod-name> | grep -i oom
# 如果看到 "OOMKilled" → 增加memory limit或排查内存泄漏
```

**ImagePullBackOff：**

```bash
# 1. 确认镜像名称是否正确
kubectl describe pod <pod-name> | grep -A 5 "Failed"
# 常见错误：镜像tag写错、registry地址拼错

# 2. 验证拉取权限
kubectl get secret <pull-secret> -o yaml  # 确认imagePullSecrets存在且正确

# 3. 手动在节点上拉取验证
docker pull <image>   # 或 crictl pull <image>
# 看具体错误——认证失败？网络不通？镜像不存在？

# 4. 私有registry的常见坑
# - imagePullSecrets 必须和Pod在同一namespace
# - ServiceAccount也可以绑定pull secret，这样该SA下的所有Pod都自动使用
kubectl patch serviceaccount default -p '{"imagePullSecrets": [{"name": "my-registry-secret"}]}'
```

---

### Q9: liveness probe和readiness probe的区别？

| | Liveness Probe | Readiness Probe | Startup Probe |
|---|---|---|---|
| 目的 | 检测容器是否需要重启 | 检测容器是否可以接收流量 | 检测应用是否已完成启动 |
| 失败动作 | **杀死容器**，按restartPolicy重建 | 将Pod从Service的Endpoints中**移除** | 杀死容器 |
| 不配置 | 默认假设容器永远活着 | 默认假设容器启动即可服务 | 无 |
| 典型场景 | 死锁、无限循环 | 预热缓存、数据库连接就绪 | 慢启动应用 |

```yaml
containers:
- name: gpu-service
  image: my-gpu-app:latest
  startupProbe:                    # 给慢启动应用充足的时间
    httpGet:
      path: /healthz
      port: 8080
    failureThreshold: 30           # 最多允许30次失败
    periodSeconds: 10              # 每10s检查一次  → 最多300s（5min）启动时间
  livenessProbe:
    httpGet:
      path: /healthz
      port: 8080
    initialDelaySeconds: 0         # 有了startupProbe后不需要delay
    periodSeconds: 30
    failureThreshold: 3            # 连续3次失败才kill（不要设1，太敏感）
  readinessProbe:
    httpGet:
      path: /ready
      port: 8080
    periodSeconds: 10
    failureThreshold: 2
```

**Probe配置的常见反模式：**
- Liveness和Readiness用同一个endpoint——应用依赖的外部服务挂了后，readiness应该失败（摘除流量），但liveness不应该失败（不需要重启）
- `failureThreshold: 1`——过于敏感，一个临时抖动就触发重启
- 没有配置startupProbe，给慢启动应用设了很长的 `initialDelaySeconds`——在延迟期间应用实际已死也不会被检测到

---

### Q10: K8s Service的ClusterIP不通，排查思路？

**K8s Service的本质**：Service不是一个进程，它是kube-proxy在每台节点上维护的iptables/IPVS规则 + CoreDNS的一条A记录。

```bash
# 系统化排查：
# 1. Service是否存在，Endpoints是否正常
kubectl get svc <svc-name> -o wide
kubectl get endpoints <svc-name>    # 如果ENDPOINTS列为空 → Service发现不了Pod

# 2. 如果Endpoints为空，检查Selector是否匹配Pod Labels
kubectl get svc <svc-name> -o jsonpath='{.spec.selector}'
kubectl get pods --show-labels | grep <expected-label>

# 3. 如果Endpoints正常，排查网络层面
# 在另一Pod中测试
kubectl run test --rm -it --image=busybox -- nslookup <svc-name>
kubectl run test --rm -it --image=busybox -- wget -O- http://<svc-name>:<port>

# 4. DNS解析正常但连接不通 → kube-proxy/网络插件问题
# 检查kube-proxy DaemonSet
kubectl get pods -n kube-system | grep kube-proxy
kubectl logs -n kube-system kube-proxy-<xxx>

# 5. 确认Service的目标端口（targetPort）与Pod暴露的端口一致
kubectl get svc <svc-name> -o yaml | grep -A 5 ports
kubectl get pod <pod-name> -o yaml | grep -A 5 ports

# 6. 检查NetworkPolicy是否阻止了流量
kubectl get networkpolicies
```

**延伸：kube-proxy的三种模式**

| 模式 | 原理 | 性能 | 说明 |
|------|------|------|------|
| iptables | 通过iptables规则链实现DNAT | 规则多时线性变慢 | 默认模式，调试难 |
| IPVS | Linux内核IPVS模块做L4负载均衡 | O(1)查找，性能最好 | 需要内核模块支持 |
| userspace | kube-proxy进程做代理转发 | 差（已弃用） | 历史遗留 |

---

## 四、GPU & CUDA & Deep Learning框架

### Q1: nvidia-smi输出中各指标详解

```bash
$ nvidia-smi
+-----------------------------------------------------------------------------+
| NVIDIA-SMI 550.54.14     Driver Version: 550.54.14     CUDA Version: 12.4   |
|-------------------------------+----------------------+----------------------+
| GPU  Name                 Persistence-M | Bus-Id        Disp.A | Volatile ECC |
| Fan  Temp   Perf          Pwr:Usage/Cap |         Memory-Usage | GPU-Util  M |
|===============================+======================+======================|
|   0  NVIDIA H100 80GB HBM3    On     | 00000000:17:00.0 Off |                0 |
| N/A   45C    P0             72W /  700W |   4000MiB / 81559MiB |     85%   M |
+-------------------------------+----------------------+----------------------+
```

| 指标 | 含义 | 面试要点 |
|------|------|---------|
| **Driver Version** | 内核驱动版本 | 决定了CUDA最高版本支持 |
| **CUDA Version** | 驱动支持的CUDA最高版本 | nvidia-smi显示的CUDA版本 = 驱动兼容的CUDA上限，不等于系统安装的CUDA Toolkit版本 |
| **Persistence-M** | 持久化模式 | `On` = GPU驱动常驻，nvidia-smi秒回；`Off` = 空闲时卸载驱动，首次查询慢 |
| **Bus-Id** | PCIe总线地址 | 配合NUMA拓扑判断GPU与CPU的亲和关系 |
| **ECC** | Error Correcting Code | 纠错码，HPC场景必须开启（但会占用约6.25%显存） |
| **Fan** | 风扇转速百分比 | 被动散热GPU显示N/A |
| **Temp** | GPU核心温度 | 一般>85°C开始限频（thermal throttling） |
| **Perf** | 性能状态 | P0（最高）→ P12（最低），训练时应在P0 |
| **Pwr:Usage/Cap** | 当前功耗/设计上限 | 接近上限说明在满负荷；远低于上限但利用率高可能是显存带宽瓶颈 |
| **Memory-Usage** | 显存使用/总量 | 注意PyTorch的caching allocator会让这个值偏高 |
| **GPU-Util** | GPU核心利用率 | **重要误区**：GPU-Util 100%不代表计算效率高，只代表有kernel在执行。需结合SM efficiency判断 |
| **Compute M.** | 计算模式 | Default（多进程共享）、Exclusive（单进程独占） |

**延伸：GPU-Util和SM Efficiency的区别**
- `GPU-Util` (nvidia-smi)：过去采样周期内GPU是否有kernel在执行（二进制指标：忙/闲）—— 85% 意味着85%的采样点GPU核在运行，但不代表运行得充分
- `SM Efficiency` (DCGM/nvidia-smi dmon)：SM内部各单元（CUDA Core、Tensor Core、显存控制器）的利用率——这才是真正的计算效率指标
- 场景：kernel启动延迟大、grid太小、显存带宽受限 → GPU-Util可能很高但SM Efficiency很低。

---

### Q2: CUDA Context是什么？为什么多进程OOM但nvidia-smi显示有显存？

**CUDA Context** 是CPU进程与GPU设备之间交互的上下文，封装了：
- 该进程在GPU上的地址空间（虚拟地址映射）
- 加载到GPU上的CUDA模块（kernels）
- 显存分配记录
- CUDA stream、event等运行时对象

每个进程在首次调用CUDA API时自动创建primary context，后续操作都在该context内。

**为什么多进程会"虚假OOM"：**
1. **PyTorch Caching Allocator**：PyTorch分配显存后会缓存起来，即使tensor被释放，显存也不立即归还驱动。`nvidia-smi` 显示的是驱动层面的占用 = 实际tensor + 缓存池
2. **CUDA Context开销**：每个进程的primary context本身占用几百MB显存（取决于GPU型号和驱动版本，H100上约300-600MB/进程）
3. **碎片化**：多个进程频繁分配/释放不同大小的显存块，可能产生碎片，导致有剩余显存但无法分配连续块

```bash
# 查看PyTorch实际显存使用（需要在代码中设置）
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True

# 在Python代码中
import torch
torch.cuda.memory_summary()         # 打印详细显存报告
torch.cuda.memory_stats()           # 返回字典格式的统计
torch.cuda.empty_cache()            # 释放PyTorch缓存的显存给驱动
```

---

### Q3: PyTorch DataLoader num_workers设多少合适？

**num_workers** 是DataLoader中用于数据加载的子进程数。数据从磁盘→内存→GPU的流水线是训练中的常见瓶颈。

```
num_workers太少 → GPU等待数据（GPU利用率低）
num_workers太多 → CPU/内存争抢（上下文切换开销 > 收益）
```

**经验法则：**
- 起点：`num_workers = 4 * num_gpus`（大致公式）
- IO密集型（大量图片读取、解压）：可以到8-16
- CPU密集型（大量数据增强）：4-8
- 最终需要通过实验确定：**从2开始翻倍增加，直到GPU利用率不再提高**

```python
from torch.utils.data import DataLoader

train_loader = DataLoader(
    dataset,
    batch_size=256,
    num_workers=8,         # 数据加载子进程数
    pin_memory=True,        # 将数据pin在CPU锁页内存，加速→GPU传输
    prefetch_factor=2,      # 每个worker预取2个batch
    persistent_workers=True # worker进程常驻（避免每个epoch都fork新进程）
)
```

**为什么不是越大越好？**
- Fork开销：每个worker是独立进程，启动有成本
- 内存：每个worker在内存中维护自己的batch副本（`num_workers * batch_size * 样本大小`）
- 共享资源竞争：所有worker都在读同一个磁盘/NFS时，IO带宽会饱和

**`pin_memory=True` 为什么能加速？** 将CPU内存锁定在物理内存页（不可swap），使得DMA（Direct Memory Access）可以直接从此区域传输数据到GPU，无需CPU参与一次中间拷贝。

**`persistent_workers=True`** 避免每个epoch结束销毁又创建worker进程，推荐在epoch数多时启用。

---

### Q4: 训练时CUDA OOM排查和解决

```python
# 1. 确认显存使用情况
import torch
print(torch.cuda.memory_summary())

# 2. 查看峰值显存
print(f"Peak allocated: {torch.cuda.max_memory_allocated() / 1024**3:.2f} GB")
print(f"Peak reserved:  {torch.cuda.max_memory_reserved() / 1024**3:.2f} GB")
```

**解决OOM的策略（按推荐优先级排列）：**

| 方案 | 原理 | 效果 | 代价 |
|------|------|------|------|
| **减小batch size** | 直接减少前向激活值和梯度存储 | 最直接 | 训练收敛可能变慢 |
| **Gradient Accumulation** | 多个小batch累积梯度后再update | 等效大batch | 训练时间变长 |
| **混合精度训练 (AMP)** | fp32→fp16，显存减半 | ~40%显存节省 | 几乎无 |
| **Activation Checkpointing (Gradient Checkpointing)** | 不存储中间激活，反向时重新计算 | ~30-50%显存节省 | ~20%计算开销 |
| **ZeRO优化器 (DeepSpeed/FSDP)** | 将优化器状态/梯度/参数分片到多GPU | 线性扩展到多GPU | 通信开销增加 |
| **Offloading** | 将优化器状态卸载到CPU内存 | 极大节省GPU显存 | 显著变慢 |
| **换更大显存GPU** | 硬件升级 | — | — |

```python
# Gradient Accumulation 示例
accumulation_steps = 4
optimizer.zero_grad()
for i, (inputs, labels) in enumerate(dataloader):
    outputs = model(inputs)
    loss = criterion(outputs, labels)
    loss = loss / accumulation_steps    # 关键：loss要除以累积步数
    loss.backward()
    if (i + 1) % accumulation_steps == 0:
        optimizer.step()
        optimizer.zero_grad()

# 混合精度训练
from torch.cuda.amp import autocast, GradScaler
scaler = GradScaler()
for inputs, labels in dataloader:
    with autocast():               # 自动选择fp16/fp32
        outputs = model(inputs)
        loss = criterion(outputs, labels)
    scaler.scale(loss).backward()  # 放大loss防止fp16梯度下溢
    scaler.step(optimizer)
    scaler.update()
```

---

### Q5: TensorFlow和PyTorch的多GPU策略对比

| | DataParallel (DP) | DistributedDataParallel (DDP) |
|---|---|---|
| 实现方式 | 单进程多线程 | 多进程（每GPU一个进程） |
| Python GIL | 受GIL限制 | 无GIL限制（独立进程） |
| GPU负载均衡 | 差——主GPU承担聚合工作 | 好——AllReduce均摊 |
| 性能 | 慢，不推荐 | 快，推荐 |
| 代码复杂度 | 低（一行model = nn.DataParallel(model)） | 中（需初始化进程组） |

```python
# PyTorch DDP 示例
import torch.distributed as dist
from torch.nn.parallel import DistributedDataParallel as DDP

def setup(rank, world_size):
    dist.init_process_group("nccl", rank=rank, world_size=world_size)

def train(rank, world_size):
    setup(rank, world_size)
    model = MyModel().to(rank)
    ddp_model = DDP(model, device_ids=[rank])
    # ... training loop ...

# 启动方式（推荐torchrun，替代老的torch.distributed.launch）
# torchrun --nnodes=2 --nproc_per_node=8 train.py
```

**TensorFlow的 `tf.distribute.MirroredStrategy`** 在单机多GPU时类似DDP，底层使用NCCL做AllReduce；多机时用 `MultiWorkerMirroredStrategy`。

---

### Q6: K8s上PyTorch分布式训练只有一个GPU在工作，怎么排查？

这是面试中经典的综合排查场景题。排查链路：

```bash
# Step 1: 确认进程数
kubectl exec <pod> -- nvidia-smi | grep "Processes" -A 10
# 应该看到每个GPU上都有对应进程，如果只有一个GPU上有进程：
#   → 可能只有单进程启动，多进程初始化失败

# Step 2: 检查分布式初始化环境变量
kubectl exec <pod> -- env | grep -E "RANK|WORLD_SIZE|MASTER_ADDR|MASTER_PORT|LOCAL_RANK"
# 关键变量：
# - WORLD_SIZE: 全局进程总数（应为 nnodes * nproc_per_node）
# - RANK: 当前进程的全局编号（0 到 WORLD_SIZE-1）
# - LOCAL_RANK: 当前进程在所在节点的GPU编号
#   → 如果所有进程的LOCAL_RANK都是0，说明多进程没有正确分配到不同GPU

# Step 3: 验证NCCL通信
kubectl exec <pod> -- bash -c "
  export NCCL_DEBUG=INFO
  python -c 'import torch.distributed as dist; dist.init_process_group(\"nccl\")'
"
# 看NCCL日志：能否发现其他节点？能否建立连接？
# 常见问题：NCCL_SOCKET_IFNAME 指向了错误的网络接口

# Step 4: 确认Pod网络配置
kubectl get pod <pod> -o yaml | grep -A 5 "hostNetwork\|hostIPC"
# 分布式训练需要：
# - hostNetwork: true (或配置好Pod间网络可达)
# - hostIPC: true (PyTorch DataLoader shm共享内存)
```

**常见根因及解决：**

| 现象 | 可能原因 | 解决 |
|------|---------|------|
| 所有进程都是RANK 0 | torchrun没有正确分发RANK | 用torchrun/kubeflow-operator管理 |
| 单机正常，多机看不到对方 | 网络不通、NCCL_SOCKET_IFNAME错误 | 设置正确的网络接口名 |
| NCCL报"network is unreachable" | Pod间网络隔离 | 确认CNI插件、NetworkPolicy |
| 训练启动但速度异常慢 | NCCL选了慢速网卡（如管理口） | `export NCCL_SOCKET_IFNAME=eth0` |
| 周期性hang | NCCL_P2P_LEVEL设置不当 | 尝试 `NCCL_P2P_DISABLE=1` 排查是否是P2P导致 |

---

### Q7: CUDA版本和NVIDIA驱动版本的兼容性问题？

**核心原则：驱动版本是上限，CUDA Toolkit版本不能高于驱动支持的CUDA版本。**

```bash
# nvidia-smi 显示的 "CUDA Version: 12.4"
# 意思是驱动支持的CUDA最高版本是12.4
# 即你可以运行任何 CUDA Toolkit ≤ 12.4 编译的程序

# 查看驱动版本
nvidia-smi --query-gpu=driver_version --format=csv,noheader

# 查看系统安装的CUDA Toolkit版本
nvcc --version             # 开发用CUDA版本
ls /usr/local/cuda*/       # 可能安装了多个CUDA版本
```

**兼容性表（CUDA 12.x时代）：**

| 驱动版本 | 支持CUDA | CUDA Driver API版本 |
|---------|---------|-------------------|
| R550 | CUDA 12.4 | 12.4 |
| R545 | CUDA 12.3 | 12.3 |
| R535 | CUDA 12.2 | 12.2 |
| R525 | CUDA 12.0 | 12.0 |
| R470 | CUDA 11.4 | 11.4 |

**容器场景的特殊处理：**
- Docker镜像 `nvidia/cuda:12.4.0-base` 包含的是CUDA 12.4的用户态库，但**不包含驱动**
- 容器的CUDA库版本必须 ≤ 宿主机驱动版本
- nvidia-container-toolkit在容器启动时将宿主机驱动的**内核模块接口**映射进容器，但用户态库用镜像内的版本。只要镜像的CUDA Toolkit版本≤驱动版本，就能正常工作。

**最佳实践：** 在同个集群中使用统一的驱动版本，CUDA Toolkit通过容器镜像管理，解耦驱动和CUDA Toolkit版本。

---

### Q8: cuDNN是什么？和CUDA是什么关系？

- **CUDA**：通用GPU并行计算平台，提供基础的计算能力——管理GPU内存、启动kernel、线程调度等
- **cuDNN**：深度神经网络加速库，构建在CUDA之上，为DNN的常见操作（卷积、池化、归一化、激活函数、RNN/LSTM）提供高度优化的实现

**关系类比：** CUDA = C语言编译器，cuDNN = 高度优化的BLAS库

cuDNN的价值在于：
- 每种卷积（不同kernel size、stride、dilation）有数十种算法实现（Winograd、FFT、implicit GEMM、direct convolution），cuDNN在首次调用时自动benchmark并选择最优算法
- 支持Tensor Core加速（fp16/bf16/int8）
- 跨GPU架构可移植（V100→A100→H100代码无需改动）

```python
# PyTorch中cuDNN的配置
torch.backends.cudnn.benchmark = True     # cuDNN自动搜索最优卷积算法
torch.backends.cudnn.deterministic = False # True=确定性结果(可复现)，False=性能优先
```

---

### Q9: 混合精度训练（AMP）原理

混合精度训练（Automatic Mixed Precision）在训练中同时使用 `fp32` 和 `fp16`（或 `bf16`）：

- **前向传播**：大部分计算用fp16（减少显存、加速计算）
- **反向传播**：梯度用fp16计算
- **权重更新**：维护一份fp32的主权重副本（master weights），确保更新精度
- **Loss Scaling**：对于fp16，梯度值可能小于fp16的最小正数（~6e-8），变为0。因此在反向传播前将loss放大（如×1024），反向后再缩小

**bf16 vs fp16：** 在A100/H100上推荐bf16（brain floating point）
- fp16：动态范围小（±65504），需要loss scaling技巧
- bf16：与fp32相同的指数位（8bit），动态范围大，不需要loss scaling，但精度略低（尾数位少）
- H100的Transformer Engine原生支持fp8训练

**对面试官的回答要点：** AMP几乎零代码成本（`torch.cuda.amp.autocast`），换取40%显存节省和1.5-3x的加速（在Tensor Core GPU上），且精度损失可忽略（<0.1% accuracy）。这是生产环境中**标准实践**。

---

## 五、Cloud & 分布式系统

### Q1: AWS/GCP上部署GPU集群的坑

**常见痛点：**

1. **GPU配额限制**：默认AWS账户的GPU实例限额为0，需要提support ticket申请提升。p5（H100）实例在新区域可能完全不开放。

2. **实例类型选型**：训练用 p4d/p5（A100/H100），推理用 g5（A10G），需根据场景选择，差别巨大（价格、显存、互联带宽）。

3. **跨可用区延迟**：GPU训练集群对网络延迟敏感。跨AZ的NCCL通信延迟（通常1-2ms）足以让分布式训练效率大幅下降。最佳实践：所有GPU节点必须在**同一个置放群组（Placement Group）和同一个AZ**中。

4. **EFA (Elastic Fabric Adapter)**：AWS的GPU实例间高速网络。必须在创建实例时指定EFA接口，且需要特殊的ENA/EFA驱动和NCCL的AWS OFI插件才能发挥性能。

5. **存储性能**：共享存储（EFS/FSx for Lustre）的吞吐量可能成为瓶颈。大规模训练数据集建议用FSx for Lustre或直接本地NVMe SSD。

6. **Spot Instance抢占**：用Spot实例省钱但可能随时被回收，需要checkpoint机制。

---

### Q2: NCCL的Ring AllReduce和Tree AllReduce

**AllReduce** 是将所有GPU上的梯度求和后广播回所有GPU的通信模式。

**Ring AllReduce：**
- 所有GPU排成一个逻辑环
- 分两步：Scatter-Reduce（每个GPU累加一部分梯度）→ AllGather（每个GPU收集所有累加结果）
- 通信量与GPU数量无关（每个GPU发送和接收 2(N-1)/N 的数据）—— **带宽最优**
- 延迟随GPU数量线性增长 —— **延迟不友好**（多GPU时环很大）

**Tree AllReduce：**
- GPU排成树形拓扑
- Reduce（叶→根）→ Broadcast（根→叶）
- 延迟为 O(log N) —— **延迟友好**
- 带宽利用不如Ring —— 根节点可能成为瓶颈

**NCCL的智能选择：** NCCL会根据消息大小自动选择算法——小消息用Tree（延迟敏感），大消息用Ring（带宽敏感）。

**面试回答：** 在训练大模型时（梯度通常数百MB到数GB），NCCL默认选择Ring AllReduce，因为带宽最优。小模型或用NCCL做同步Barrier时可能切到Tree。

---

### Q3: 如何设计支持多租户的GPU集群调度系统？

**设计要点（面试时可画架构图）：**

```
┌─────────────────────────────────────────────┐
│  用户层：Jupyter / CLI / SDK                  │
├─────────────────────────────────────────────┤
│  调度层：Volcano / Kubeflow / 自研Scheduler    │
│  - 队列管理 (FIFO / Priority / Fair-share)    │
│  - Gang Scheduling（All-or-nothing调度）       │
│  - 抢占策略                                  │
├─────────────────────────────────────────────┤
│  资源层：Kubernetes + GPU Operator             │
│  - MIG分区（A100/H100）                       │
│  - Time-slicing（GPU分时复用）                 │
│  - 拓扑感知调度                               │
├─────────────────────────────────────────────┤
│  监控层：DCGM + Prometheus + Grafana          │
│  - GPU利用率、显存、温度、功耗                 │
│  - NCCL通信带宽                               │
└─────────────────────────────────────────────┘
```

**关键设计决策：**
1. **排队 vs 抢占**：科研场景用FIFO队列；生产业务需要优先级+抢占
2. **Gang Scheduling**：分布式训练要求所有GPU同时分配，否则全部等待（避免部分分配的死锁）
3. **拓扑感知**：优先将同训练任务的GPU分配在同一节点/NVSwitch域内，减少跨节点通信
4. **MIG vs MPS**：MIG（硬件隔离，安全但灵活性低）vs MPS（软件多进程共享，灵活但无隔离）

---

### Q4: etcd在K8s中的角色

etcd是K8s的唯一数据源（Source of Truth），存储所有集群状态：
- Pod、Service、ConfigMap等所有API对象的定义
- 节点状态、租约
- RBAC策略
- 配置数据

**如果etcd挂了：**
- **已有Pod仍运行**（kubelet本地缓存Pod spec）
- **无法创建/更新/删除任何资源**（API Server依赖etcd做写操作）
- **Scheduler停止工作**（无法更新Pod→Node绑定）
- **Controller Manager停止工作**（无法做reconciliation）

生产环境一般部署3或5节点的etcd集群（奇数个），容忍1或2节点故障。etcd使用Raft共识协议选举Leader，只有Leader处理写请求。

**关键指标（Prometheus）：**
- `etcd_server_has_leader`：集群是否有leader
- `etcd_disk_wal_fsync_duration_seconds`：写延迟（>10ms需关注）
- `etcd_mvcc_db_total_size_in_bytes`：数据库大小（默认quota 2GB）

---

### Q5: 分布式系统监控方案（Observability）

**三层监控体系：**

| 层 | 工具 | GPU特有指标 |
|---|---|---|
| 基础设施 | node_exporter + DCGM | GPU功耗、温度、ECC错误、PCIe带宽 |
| 容器/编排 | kube-state-metrics | GPU allocatable/capacity |
| 应用 | 应用内埋点 | 训练吞吐（samples/sec）、loss变化、NCCL通信耗时 |

```
Prometheus (采集) →  Grafana (可视化)  +  AlertManager (告警)
                     ↑
Loki (日志)    ← Fluentd/Bitnami (采集)
```

**需要告警的关键指标：**
- GPU温度 > 85°C → 可能导致降频/掉卡
- GPU ECC错误 > 0 → 显存硬件错误，需更换GPU
- GPU掉卡（`DCGM_FI_DEV_XID_ERRORS`）→ Sev1
- 训练吞吐下降超过20%（基于应用层指标）
- NCCL通信带宽下降（可能网络故障）

---

## 六、问题排查 & 客户支持场景

### 场景1: "容器里nvidia-smi看不到GPU"

**结构化排查（从外到内5层）：**

```
Layer 1: 宿主机硬件
├─ lspci | grep -i nvidia          GPU是否被识别？
├─ nvidia-smi                      宿主机上是否正常？
└─ nvidia-smi topo -m              拓扑是否正常？

Layer 2: 驱动和运行时
├─ lsmod | grep nvidia             内核模块是否加载？
├─ docker info | grep -i runtime   nvidia runtime是否注册？
└─ cat /etc/docker/daemon.json     确认 daemon.json 配置

Layer 3: Container Toolkit
├─ dpkg -l | grep nvidia-container 容器工具包是否安装？
├─ cat /etc/nvidia-container-runtime/config.toml
└─ nvidia-container-cli info       验证工具包识别GPU

Layer 4: 容器启动参数
├─ docker inspect <container>      确认 --gpus all 参数？
├─ 确认 NVIDIA_VISIBLE_DEVICES 环境变量
└─ 确认 --runtime=nvidia (老版本Docker)

Layer 5: 容器内部
├─ ls /dev/nvidia*                 设备文件是否存在？
├─ ldconfig -p | grep cuda         CUDA库是否在搜索路径？
└─ echo $LD_LIBRARY_PATH           库路径是否正确？
```

**90%的情况是这3个原因之一：**
1. `--gpus` 参数没加或加错了（`docker run` 忘了 `--gpus all`）
2. nvidia-container-toolkit 没安装或版本不匹配（驱动更新后没重启docker）
3. DaemonSet 的 nvidia-device-plugin 挂了（K8s环境）

---

### 场景2: "K8s上训练比裸机慢很多"

**排查框架：量化→定位→修复**

```bash
# Step 1: 量化——确认真实性能差距
# 运行一个标准benchmark而非依赖用户描述
docker run --gpus all nvidia/cuda:12.0-base \
    /workspace/benchmark.sh  # NCCL all_reduce 带宽测试

# Step 2: 逐层对比
# 单GPU训练 → 如果也慢，问题在存储/数据加载
# 多GPU训练 → 如果单GPU正常多GPU慢，问题在网络/通信

# Step 3: 通信层排查
export NCCL_DEBUG=INFO     # 看NCCL选用了什么协议和算法
# NCCL通信协议优先级：NVLink > PCIe > IB/RoCE > TCP
# 如果NCCL选择TCP而非NVLink，说明P2P访问被阻止

# Step 4: 存储排查
# 数据加载是否是瓶颈？测试本地SSD vs 网络存储的速度
dd if=/dev/zero of=/mnt/testfile bs=1M count=1024 conv=fdatasync
```

**常见根因：**

| 原因 | 检查方式 | 修复 |
|------|---------|------|
| NCCL走TCP而非NVLink | `NCCL_DEBUG=INFO` 查看通信协议 | `NCCL_P2P_DISABLE=0`，确认无 `no-snoop` 问题 |
| 网络存储IO瓶颈 | `iotop` 或 `dd` 测试 | 用本地NVMe做临时缓存或换FSx for Lustre |
| CPU未绑核，跨NUMA | `numactl --hardware` | 使用 `taskset` 或 `numactl` 绑核 |
| GPU throttling（过热） | `nvidia-smi -q -d TEMPERATURE` | 改善散热、降低功耗上限 |
| K8s网络插件性能差 | `iperf3` 测节点间带宽 | 考虑hostNetwork模式 |
| 不正确的资源limits | 容器CPU limits被throttling | 移除CPU limits或配得足够大 |

---

### 场景3: "容器启动时拉取镜像超时"

```bash
# Step 1: 确认镜像名称和Tag
kubectl describe pod <pod> | grep -A 5 "Failed"
# 最常见的低级错误：tag拼错、registry地址漏了

# Step 2: 在节点上手动拉取
# 登录到Pod所在节点
crictl pull <image>     # containerd
# 或
docker pull <image>      # Docker
# 看错误信息：认证失败？DNS解析失败？TLS证书问题？超时？

# Step 3: 排查registry连通性
# 从节点上测试
curl -v https://<registry>/v2/    # 测试HTTPS连通性
nslookup <registry>                # DNS解析
telnet <registry> 443              # TCP连通性

# Step 4: 认证问题
kubectl get secret <pull-secret> -o yaml
# 确认：
# - Secret类型为 kubernetes.io/dockerconfigjson
# - .dockerconfigjson 中registry地址正确
# - Secret在Pod所在的namespace中
# - Pod的imagePullSecrets引用了正确的Secret名称

# Step 5: 网络策略/防火墙
# 检查是否有NetworkPolicy限制节点访问外部registry
kubectl get networkpolicies -A
# 企业环境可能有出网代理，确认containerd/Docker配置了HTTPS_PROXY
```

**企业环境专用坑：**
- 私有registry用了自签名证书 → 需要将CA证书添加到节点的信任存储
- 镜像太大（nvidia/cuda devel镜像可达8GB+）→ 默认2分钟超时不够，设置 `--image-pull-progress-deadline`
- Air-gapped环境 → 需要通过私有registry mirror或离线导入镜像

---

### 场景4: Sev1故障——前5分钟做什么？

**第一反应（前30秒）：**
1. **保持冷静**，确认这是真的Sev1（大规模影响/客户业务中断）
2. **打开War Room**：创建应急沟通渠道（Slack频道/会议桥），拉入必要人员
3. **声明Incident Commander**：一人指挥，明确分工

**前5分钟行动：**

```
Minute 0-1: 信息收集
├─ 确认影响范围：多少客户受影响？什么症状？
├─ 确认时间线：从什么时候开始的？
├─ 确认最近变更：是否有部署、配置变更、基础设施变更？
└─ 查看监控大盘：哪些指标异常？

Minute 1-3: 初步排查
├─ 快速检查关键告警和日志
├─ 确认是否是代码变更导致（优先rollback）
├─ 确认是否是基础设施问题（云厂商状态页、网络）
└─ 如果不是明显原因，启动系统化排查

Minute 3-5: 决策和行动
├─ 如果10分钟内找不到根因 → 优先rollback最近的变更
├─ 如果rollback不可行 → 启动灾备/降级方案
├─ 分配并行任务：一组继续排查，一组准备恢复方案
└─ 开始对外沟通：给客户/内部stakeholder发第一封更新
```

**面试时强调的要点：**
- 不要一个人扛——立刻拉人，清晰分工
- 先止损，后找根因——不要为了找到完美根因而拖延恢复
- 保留现场——在恢复之前保存日志、dump、snapshot
- 沟通同步——每15-30分钟发一次状态更新，减少干系人焦虑

---

### Q: 如何处理从未见过的问题？方法论

**STAR 故事框架：**
1. **Isolate**：缩小问题范围——哪个组件？哪个时间点？什么变更触发的？
2. **Reproduce**：能否在测试环境复现？最小复现步骤是什么？
3. **Hypothesize**：根据现象提出假设，逐一验证（二分排除法）
4. **Research**：查官方文档、GitHub Issues、StackOverflow、内部知识库
5. **Escalate**：如果30-60分钟无进展，不要犹豫寻求帮助（内部专家/厂商支持）
6. **Post-mortem**：解决后写复盘文档，防止同类问题再次发生

---

### Q: 如何向非技术客户解释复杂技术问题？

**原则：**
- 用类比而不是术语
- 先说结论再说细节
- 聚焦在"对你的影响是什么"和"我们在做什么"

**示例：** 解释GPU显存OOM问题

> "想象GPU是一张办公桌，显存是桌面的大小。您的模型（工作文件）展开后比桌面还大，所以放不下。我们现在通过折叠文件（模型优化）和分批处理（减小batch size）来解决这个问题。预计30分钟后恢复。在此期间您的训练任务需要重启，已训练的checkpoint不会丢失。"

---

## 七、行为面试（Behavioral）

### 回答框架：STAR (Situation → Task → Action → Result)

**推荐准备3个故事：**

1. **复杂Debug经历**
   - Situation: 生产环境出现间歇性故障
   - Task: 需要定位根因并修复
   - Action: 系统化排查步骤——日志→指标→隔离变量→复现→修复
   - Result: 找到根因（例如：NCCL在特定网络拓扑下选择错误通信协议），修复后系统稳定，写了复盘文档

2. **客户沟通/冲突处理**
   - Situation: 客户对产品功能不满，要求不可能的时间表
   - Task: 在维护客户关系的同时设立合理预期
   - Action: 主动沟通，先理解真正需求（5 Whys），提供阶段性的替代方案
   - Result: 客户接受了分阶段交付方案，第一阶段提前上线获得了客户认可

3. **主动改进/创新**
   - Situation: 团队重复性工作多，效率低
   - Task: 找到自动化改进点
   - Action: 设计并实现了自动化工具/AI辅助方案
   - Result: 效率提升XX%，被推广到其他团队

---

## 八、快速查阅清单

### 必备命令Cheatsheet

```bash
# GPU
nvidia-smi                          # 查看GPU状态
nvidia-smi topo -m                  # GPU拓扑矩阵
nvidia-smi dmon -s pucvmet          # 详细GPU监控（进程/利用率/时钟/显存/温度/ECC/节流）
nvidia-smi -q -d MEMORY,UTILIZATION # 详细信息
dcgmi dmon -e 155,156,1001          # DCGM关键指标（SM占用/SM频率/显存带宽利用率）

# 系统
strace -p <PID> -f -c               # 系统调用统计
perf top -p <PID>                   # CPU热点函数
lsof -p <PID>                       # 打开的文件和连接
lsof | grep deleted                 # 查找已删除但未释放的文件
free -h                             # 内存概况（关注available而非free）

# K8s
kubectl describe pod <pod>          # Pod详情和Events
kubectl logs <pod> --previous       # 上一个容器的日志
kubectl get events --sort-by=.metadata.creationTimestamp | tail -20
kubectl top pods --containers       # 资源使用（需要metrics-server）

# 网络
iperf3 -s / iperf3 -c <host>       # 带宽测试
nccl-tests/build/all_reduce_perf    # NCCL带宽基准
ss -tunlp                           # 所有监听端口和连接
```

### 关键环境变量

```bash
# NCCL
NCCL_DEBUG=INFO                     # 开启调试日志
NCCL_SOCKET_IFNAME=eth0             # 指定通信网卡（关键！）
NCCL_P2P_DISABLE=1                  # 禁用P2P（排查通信问题时使用）
NCCL_IB_DISABLE=1                   # 禁用InfiniBand
NCCL_NET_GDR_LEVEL=5                # GPUDirect RDMA等级

# CUDA/PyTorch
CUDA_VISIBLE_DEVICES=0,1            # 限制可见GPU
PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True  # 减少显存碎片
NVIDIA_VISIBLE_DEVICES=all          # 容器中可见的GPU

# 系统
LD_LIBRARY_PATH=/usr/local/cuda/lib64:$LD_LIBRARY_PATH
```

---

> 文档基于 NVIDIA Solution Engineering JD 编写，覆盖面试高频考点。建议结合自身项目经验，为每个场景题准备一个自己的真实案例。
