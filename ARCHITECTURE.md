# MicroGPT 架构分析

> **作者**: Andrej Karpathy  
> **文件**: microgpt.py  
> **说明**: 最原子化的 GPT 训练和推理实现，纯 Python，无依赖

---

## 📋 目录

- [概述](#概述)
- [核心组件](#核心组件)
- [模型架构](#模型架构)
- [训练流程](#训练流程)
- [推理生成](#推理生成)
- [代码结构](#代码结构)
- [关键设计决策](#关键设计决策)

---

## 概述

### 设计哲学

> "训练和运行 GPT 的最原子化方式，纯 Python 实现，无任何依赖。  
> 这个文件就是完整的算法。  
> 其他一切都只是效率优化。"

### 特点

- ✅ **零依赖**: 只使用 Python 标准库 (`os`, `math`, `random`)
- ✅ **完整实现**: 包含自动微分、Transformer 架构、优化器
- ✅ **教育目的**: 代码简洁清晰，适合学习理解
- ✅ **可运行**: 200 行代码即可训练一个真实的 GPT 模型

### 模型规模

```python
n_layer = 1        # Transformer 层数
n_embd = 16        # 嵌入维度
block_size = 16    # 最大上下文长度
n_head = 4         # 注意力头数量
head_dim = 4       # 每个头的维度 (n_embd // n_head)
vocab_size = ~27   # 词汇表大小（取决于数据集）
总参数量 ≈ 3,000  # 可训练参数
```

---

## 核心组件

### 1. 数据集和分词器

#### 数据加载
```python
# 自动下载示例数据集（人名列表）
if not os.path.exists('input.txt'):
    names_url = 'https://raw.githubusercontent.com/karpathy/makemore/988aa59/names.txt'
    urllib.request.urlretrieve(names_url, 'input.txt')

docs = [line.strip() for line in open('input.txt') if line.strip()]
random.shuffle(docs)  # 随机化训练数据
```

**数据集**: 人名列表（例如："emma", "olivia", "ava"）

#### 字符级分词器
```python
uchars = sorted(set(''.join(docs)))  # 提取所有唯一字符
BOS = len(uchars)                    # 特殊 token：序列开始标记
vocab_size = len(uchars) + 1         # 词汇表大小 = 字符数 + BOS
```

**分词方式**:
- 字符级别（character-level tokenization）
- 每个字符映射到一个整数 ID
- 添加特殊 `BOS` token 标记序列边界

---

### 2. 自动微分系统 (Autograd)

#### Value 类

实现标量值的自动梯度计算：

```python
class Value:
    __slots__ = ('data', 'grad', '_children', '_local_grads')
    
    def __init__(self, data, children=(), local_grads=()):
        self.data = data                # 前向传播的值
        self.grad = 0                   # 反向传播的梯度
        self._children = children       # 计算图的子节点
        self._local_grads = local_grads # 局部梯度
```

#### 支持的操作

| 操作 | 方法 | 局部梯度 |
|------|------|---------|
| 加法 | `__add__` | `(1, 1)` |
| 乘法 | `__mul__` | `(other.data, self.data)` |
| 幂运算 | `__pow__` | `n * x^(n-1)` |
| 对数 | `log()` | `1/x` |
| 指数 | `exp()` | `e^x` |
| ReLU | `relu()` | `1 if x > 0 else 0` |

#### 反向传播算法

```python
def backward(self):
    # 1. 拓扑排序：确保先计算依赖的梯度
    topo = []
    visited = set()
    def build_topo(v):
        if v not in visited:
            visited.add(v)
            for child in v._children:
                build_topo(child)
            topo.append(v)
    build_topo(self)
    
    # 2. 反向传播：从损失函数开始，逆向累积梯度
    self.grad = 1  # 损失对自身的梯度为 1
    for v in reversed(topo):
        for child, local_grad in zip(v._children, v._local_grads):
            child.grad += local_grad * v.grad  # 链式法则
```

**工作原理**:
1. 前向传播时构建计算图
2. 反向传播时从输出节点开始
3. 使用链式法则计算每个参数的梯度

---

### 3. 模型参数初始化

#### 参数字典结构

```python
state_dict = {
    # 嵌入层
    'wte': matrix(vocab_size, n_embd),     # Token 嵌入 [27, 16]
    'wpe': matrix(block_size, n_embd),     # 位置嵌入 [16, 16]
    
    # 输出层
    'lm_head': matrix(vocab_size, n_embd), # 语言模型头 [27, 16]
    
    # Transformer 层（每层包含）
    'layer{i}.attn_wq': matrix(n_embd, n_embd),  # Query 权重 [16, 16]
    'layer{i}.attn_wk': matrix(n_embd, n_embd),  # Key 权重 [16, 16]
    'layer{i}.attn_wv': matrix(n_embd, n_embd),  # Value 权重 [16, 16]
    'layer{i}.attn_wo': matrix(n_embd, n_embd),  # 输出权重 [16, 16]
    'layer{i}.mlp_fc1': matrix(4*n_embd, n_embd), # MLP 第1层 [64, 16]
    'layer{i}.mlp_fc2': matrix(n_embd, 4*n_embd), # MLP 第2层 [16, 64]
}
```

#### 初始化方法

```python
matrix = lambda nout, nin, std=0.08: [
    [Value(random.gauss(0, std)) for _ in range(nin)] 
    for _ in range(nout)
]
```

**高斯初始化**: 均值 0，标准差 0.08

---

## 模型架构

### GPT Transformer 整体流程

```
输入 Token ID + 位置 ID
         ↓
    Token 嵌入 + 位置嵌入
         ↓
      RMSNorm
         ↓
   ┌─────────────┐
   │ Transformer │ × n_layer 层
   │   Layer     │
   └─────────────┘
         ↓
    Language Model Head
         ↓
    输出 Logits (词汇表分布)
```

### Transformer Layer 详细结构

每个 Transformer 层包含两个主要模块：

#### 1. 多头自注意力 (Multi-Head Attention)

```python
# 伪代码流程
x_residual = x
x = rmsnorm(x)

# 计算 Q, K, V
q = linear(x, Wq)  # [n_embd]
k = linear(x, Wk)  # [n_embd]
v = linear(x, Wv)  # [n_embd]

# 缓存 K, V（用于自回归生成）
keys[layer].append(k)
values[layer].append(v)

# 多头注意力
for each head h:
    # 分割到各个头
    q_h = q[h*head_dim : (h+1)*head_dim]
    k_h = [ki[h*head_dim : (h+1)*head_dim] for ki in keys]
    v_h = [vi[h*head_dim : (h+1)*head_dim] for vi in values]
    
    # 计算注意力分数
    attn_logits = [dot(q_h, k_h[t]) / sqrt(head_dim) for t in range(seq_len)]
    attn_weights = softmax(attn_logits)
    
    # 加权求和
    head_out = sum(attn_weights[t] * v_h[t] for t in range(seq_len))
    x_attn.extend(head_out)

# 输出投影
x = linear(x_attn, Wo)
x = x + x_residual  # 残差连接
```

**关键点**:
- **缩放点积注意力**: `score = Q·K^T / sqrt(d_k)`
- **多头机制**: 将特征分成 4 个头，并行计算
- **KV 缓存**: 存储历史的 Key 和 Value，支持自回归生成
- **残差连接**: 帮助梯度流动

#### 2. 前馈网络 (MLP)

```python
x_residual = x
x = rmsnorm(x)

# MLP: 先扩展到 4x 维度，再压缩回来
x = linear(x, Wfc1)  # [16] -> [64]
x = relu(x)
x = linear(x, Wfc2)  # [64] -> [16]

x = x + x_residual   # 残差连接
```

**设计**:
- **扩展因子**: 4x（标准 GPT 设计）
- **激活函数**: ReLU（简化版，GPT-2 用 GeLU）
- **残差连接**: 稳定训练

---

### 核心函数实现

#### 1. 线性层 (Linear)

```python
def linear(x, w):
    # x: [n_embd] 输入向量
    # w: [n_out, n_embd] 权重矩阵
    # 返回: [n_out] 输出向量
    return [sum(wi * xi for wi, xi in zip(wo, x)) for wo in w]
```

矩阵乘法: `y = W @ x`

#### 2. Softmax

```python
def softmax(logits):
    max_val = max(val.data for val in logits)  # 数值稳定性技巧
    exps = [(val - max_val).exp() for val in logits]
    total = sum(exps)
    return [e / total for e in exps]
```

公式: `softmax(x_i) = exp(x_i - max(x)) / Σ exp(x_j - max(x))`

#### 3. RMSNorm

```python
def rmsnorm(x):
    ms = sum(xi * xi for xi in x) / len(x)  # 均方值
    scale = (ms + 1e-5) ** -0.5              # 缩放因子
    return [xi * scale for xi in x]
```

**RMSNorm vs LayerNorm**:
- LayerNorm: 减去均值，除以标准差
- RMSNorm: 只除以 RMS（更简单，效果相当）

公式: `RMSNorm(x) = x / sqrt(mean(x^2) + ε)`

---

## 训练流程

### 训练循环 (1000 步)

```python
for step in range(num_steps):
    # 1. 采样一个文档
    doc = docs[step % len(docs)]
    tokens = [BOS] + [char_to_id(ch) for ch in doc] + [BOS]
    
    # 2. 前向传播：逐个 token 预测下一个 token
    keys, values = [[] for _ in range(n_layer)], [[] for _ in range(n_layer)]
    losses = []
    for pos_id in range(len(tokens) - 1):
        token_id = tokens[pos_id]
        target_id = tokens[pos_id + 1]
        
        # 通过模型获得 logits
        logits = gpt(token_id, pos_id, keys, values)
        
        # 计算交叉熵损失
        probs = softmax(logits)
        loss_t = -probs[target_id].log()  # -log(p(正确答案))
        losses.append(loss_t)
    
    loss = (1 / n) * sum(losses)  # 平均损失
    
    # 3. 反向传播：计算梯度
    loss.backward()
    
    # 4. Adam 优化器更新参数
    lr_t = learning_rate * (1 - step / num_steps)  # 线性学习率衰减
    for i, p in enumerate(params):
        # Adam 一阶矩估计（动量）
        m[i] = beta1 * m[i] + (1 - beta1) * p.grad
        # Adam 二阶矩估计（自适应学习率）
        v[i] = beta2 * v[i] + (1 - beta2) * p.grad**2
        # 偏差修正
        m_hat = m[i] / (1 - beta1**(step + 1))
        v_hat = v[i] / (1 - beta2**(step + 1))
        # 参数更新
        p.data -= lr_t * m_hat / (sqrt(v_hat) + eps)
        p.grad = 0  # 梯度清零
```

### 损失函数

**交叉熵损失 (Cross-Entropy Loss)**:

```python
loss = -log(P(正确 token))
```

对于整个序列：
```python
loss = (1/n) * Σ -log(P(token_i | token_<i))
```

### 优化器: Adam

**超参数**:
```python
learning_rate = 0.01  # 初始学习率
beta1 = 0.85          # 一阶矩衰减率
beta2 = 0.99          # 二阶矩衰减率
eps_adam = 1e-8       # 数值稳定性
```

**Adam 更新公式**:
```
m_t = β₁ * m_{t-1} + (1 - β₁) * g_t        # 一阶矩（动量）
v_t = β₂ * v_{t-1} + (1 - β₂) * g_t²       # 二阶矩（自适应学习率）
m̂_t = m_t / (1 - β₁^t)                     # 偏差修正
v̂_t = v_t / (1 - β₂^t)                     # 偏差修正
θ_t = θ_{t-1} - α * m̂_t / (√v̂_t + ε)      # 参数更新
```

**特性**:
- **自适应学习率**: 每个参数有独立的学习率
- **动量**: 利用历史梯度信息加速收敛
- **线性衰减**: 学习率随训练步数线性降低

---

## 推理生成

### 自回归采样

```python
temperature = 0.5  # 控制生成的"创造性"（0.1=保守，1.0=创意）

for sample_idx in range(20):
    keys, values = [[] for _ in range(n_layer)], [[] for _ in range(n_layer)]
    token_id = BOS  # 从 BOS token 开始
    sample = []
    
    for pos_id in range(block_size):
        # 1. 通过模型获得下一个 token 的分布
        logits = gpt(token_id, pos_id, keys, values)
        
        # 2. 使用 temperature 调整分布
        probs = softmax([l / temperature for l in logits])
        
        # 3. 从分布中采样下一个 token
        token_id = random.choices(range(vocab_size), 
                                   weights=[p.data for p in probs])[0]
        
        # 4. 如果生成 BOS，停止生成
        if token_id == BOS:
            break
        
        sample.append(uchars[token_id])
    
    print(f"sample {sample_idx+1:2d}: {''.join(sample)}")
```

### Temperature 采样

**作用**: 控制生成文本的随机性

```python
adjusted_logits = logits / temperature
```

- **temperature = 0.1**: 几乎总是选择概率最高的 token（保守）
- **temperature = 1.0**: 按原始概率分布采样（标准）
- **temperature = 2.0**: 增加随机性（创意）

**公式**:
```
P(token_i) = exp(logit_i / T) / Σ exp(logit_j / T)
```

---

## 代码结构

### 文件组织

```
microgpt.py (200 行)
├── 导入和数据准备 (1-26 行)
│   ├── 标准库导入
│   ├── 随机种子设置
│   ├── 数据集下载/加载
│   └── 字符级分词器
│
├── 自动微分系统 (29-71 行)
│   └── Value 类实现
│
├── 参数初始化 (74-89 行)
│   ├── 超参数定义
│   ├── 权重矩阵初始化
│   └── state_dict 构建
│
├── 模型架构 (92-143 行)
│   ├── 辅助函数 (linear, softmax, rmsnorm)
│   └── GPT 主函数
│
├── 训练循环 (146-183 行)
│   ├── Adam 优化器初始化
│   ├── 前向传播
│   ├── 反向传播
│   └── 参数更新
│
└── 推理生成 (186-200 行)
    └── 自回归采样
```

### 依赖关系图

```
数据集 (input.txt)
    ↓
分词器 (uchars, BOS)
    ↓
参数 (state_dict) ←→ Value (自动微分)
    ↓                     ↓
GPT 模型 (gpt函数)        ↓
    ↓                     ↓
损失计算 ──────────→ 反向传播
    ↓
Adam 优化器
    ↓
参数更新
```

---

## 关键设计决策

### 1. 为什么是字符级分词？

**优点**:
- ✅ 词汇表小（~27 个字符）
- ✅ 永远不会遇到未知 token
- ✅ 简单实现，无需 BPE 等复杂算法

**缺点**:
- ❌ 序列更长（每个单词变成多个 token）
- ❌ 训练效率相对较低

**权衡**: 对于教学目的和小型数据集，字符级是最佳选择。

### 2. 为什么用 RMSNorm 而不是 LayerNorm？

```python
# LayerNorm (GPT-2)
mean = sum(x) / len(x)
var = sum((x - mean)^2) / len(x)
normalized = (x - mean) / sqrt(var + ε)

# RMSNorm (MicroGPT)
rms = sqrt(sum(x^2) / len(x))
normalized = x / (rms + ε)
```

**RMSNorm 优势**:
- ✅ 更简单的计算
- ✅ 不需要计算均值
- ✅ 效果相当，更高效

### 3. 为什么用 ReLU 而不是 GeLU？

```python
# ReLU (MicroGPT)
relu(x) = max(0, x)

# GeLU (GPT-2)
gelu(x) = x * Φ(x)  # Φ 是标准正态分布的 CDF
```

**ReLU 优势**:
- ✅ 极其简单
- ✅ 梯度计算容易 (0 或 1)
- ✅ 无需复杂的数学函数

**GeLU 优势**:
- 更平滑的激活
- 更好的性能（在大规模模型上）

**权衡**: 对于 200 行代码的实现，ReLU 是明智选择。

### 4. 为什么不用 Bias？

```python
# 标准实现
y = W @ x + b

# MicroGPT
y = W @ x
```

**去掉 bias 的理由**:
- ✅ 减少参数量
- ✅ 简化代码
- ✅ RMSNorm 可以部分替代 bias 的作用
- ✅ 现代 LLM 趋势（LLaMA 等也不用 bias）

### 5. KV 缓存机制

```python
keys[layer].append(k)    # 缓存当前 token 的 Key
values[layer].append(v)  # 缓存当前 token 的 Value
```

**作用**:
- 自回归生成时，不需要重新计算之前 token 的 K 和 V
- 只需计算当前 token 的 K、V，然后与历史做注意力
- 大幅提升推理速度

**工作流程**:
```
t=0: Q₀ attends to [K₀], 缓存 K₀, V₀
t=1: Q₁ attends to [K₀, K₁], 缓存 K₁, V₁
t=2: Q₂ attends to [K₀, K₁, K₂], 缓存 K₂, V₂
...
```

---

## 性能特征

### 模型大小

```
Token 嵌入:     27 × 16 = 432
位置嵌入:       16 × 16 = 256
语言模型头:     27 × 16 = 432

每个 Transformer 层:
  - Wq: 16 × 16 = 256
  - Wk: 16 × 16 = 256
  - Wv: 16 × 16 = 256
  - Wo: 16 × 16 = 256
  - MLP fc1: 64 × 16 = 1024
  - MLP fc2: 16 × 64 = 1024
  层总计: 3072

总参数量: 432 + 256 + 432 + 1 × 3072 ≈ 4,192 参数
```

### 训练时间

- **1000 步训练**: 约 5-10 分钟（CPU）
- **每步耗时**: ~300-600ms
- **瓶颈**: 纯 Python 实现，无向量化

### 生成质量

训练 1000 步后，模型可以生成类似训练数据的新名字：

```
输入训练数据: emma, olivia, ava, sophia...
生成示例:
  sample 1: ella
  sample 2: mia
  sample 3: aria
  sample 4: lila
  ...
```

---

## 与 GPT-2 的对比

| 特性 | MicroGPT | GPT-2 |
|------|---------|-------|
| **参数量** | ~4K | 117M - 1.5B |
| **层数** | 1 | 12 - 48 |
| **嵌入维度** | 16 | 768 - 1600 |
| **注意力头** | 4 | 12 - 25 |
| **归一化** | RMSNorm | LayerNorm |
| **激活函数** | ReLU | GeLU |
| **Bias** | ❌ 无 | ✅ 有 |
| **分词** | 字符级 | BPE |
| **代码量** | 200 行 | 数千行 |
| **依赖** | 0 | PyTorch/TensorFlow |

---

## 学习路径建议

### 初学者 (理解架构)

1. **先读这些部分**:
   - 数据集和分词器 (1-26 行)
   - 模型架构概览 (92-143 行)
   - 训练循环主流程 (152-183 行)

2. **实验**:
   - 修改超参数（层数、维度）
   - 尝试不同的数据集
   - 调整 temperature 观察生成效果

### 中级 (深入细节)

1. **研读**:
   - Value 类的自动微分实现 (29-71 行)
   - 注意力机制的具体计算 (122-131 行)
   - Adam 优化器的实现 (174-181 行)

2. **扩展**:
   - 增加更多层
   - 实现 LayerNorm 对比 RMSNorm
   - 添加 Dropout

### 高级 (优化和改进)

1. **优化方向**:
   - 使用 NumPy 向量化计算
   - 实现批处理（batch processing）
   - 添加梯度裁剪
   - 实现学习率调度器

2. **架构改进**:
   - 实现 GeLU 激活函数
   - 添加 Pre-Norm / Post-Norm
   - 实现相对位置编码

---

## 常见问题

### Q1: 为什么只有 200 行代码？

**A**: Karpathy 的设计哲学是"最小可行实现"。通过：
- 去掉所有非核心功能
- 使用纯 Python（无依赖）
- 简化架构（ReLU vs GeLU，去掉 bias）
- 直接用列表推导而不是类封装

实现了一个完全可运行的 GPT。

### Q2: 为什么不用 PyTorch？

**A**: 教育目的。通过从零实现：
- 理解自动微分的本质
- 理解 Transformer 的数学原理
- 不被框架抽象隐藏细节

生产环境当然应该用 PyTorch/JAX。

### Q3: 性能如何？

**A**: 
- **训练速度**: 非常慢（纯 Python，无并行）
- **生成质量**: 对于小数据集（人名）效果不错
- **可扩展性**: 受限于 Python 性能

这是学习工具，不是生产系统。

### Q4: 可以训练更大的模型吗？

**A**: 理论上可以，但：
- 需要更多内存
- 训练时间呈指数增长
- 纯 Python 实现的性能瓶颈

建议：
- 学习理解用 MicroGPT
- 实际应用用 PyTorch + GPT-2/GPT-3

---

## 扩展阅读

### 相关资源

1. **Andrej Karpathy 的教程**:
   - [The spelled-out intro to neural networks and backpropagation](https://www.youtube.com/watch?v=VMj-3S1tku0)
   - [Let's build GPT](https://www.youtube.com/watch?v=kCc8FmEb1nY)

2. **论文**:
   - [Attention Is All You Need](https://arxiv.org/abs/1706.03762) (Transformer 原始论文)
   - [Language Models are Unsupervised Multitask Learners](https://d4mucfpksywv.cloudfront.net/better-language-models/language_models_are_unsupervised_multitask_learners.pdf) (GPT-2)

3. **代码实现**:
   - [nanoGPT](https://github.com/karpathy/nanoGPT) (Karpathy 的更完整实现)
   - [minGPT](https://github.com/karpathy/minGPT) (PyTorch 教学版)

### 下一步

想要更强大的实现？尝试：

1. **nanoGPT**: ~300 行 PyTorch，可训练 GPT-2
2. **Hugging Face Transformers**: 生产级实现
3. **自己扩展 MicroGPT**:
   - 添加 NumPy 加速
   - 实现多层
   - 尝试更大的数据集

---

## 总结

MicroGPT 是理解 Transformer 架构和 GPT 工作原理的绝佳起点：

✅ **教育价值**: 每一行代码都清晰可读  
✅ **完整性**: 从数据加载到生成的完整流程  
✅ **可运行**: 真实可用的模型  
✅ **简洁性**: 200 行代码的奇迹  

通过阅读和实验这个代码，你将深入理解：
- 自动微分如何工作
- Transformer 的注意力机制
- GPT 的训练过程
- 语言模型的自回归生成

**记住**: 这是算法的本质，其他一切都只是效率优化。

---

**文档版本**: 1.0  
**最后更新**: 2026-05-10  
**作者**: AI 架构分析  
**基于**: microgpt.py by Andrej Karpathy
