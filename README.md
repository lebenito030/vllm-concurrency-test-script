# vllm-concurrency-test-script

## 简介

为了测试模型的并发性能用 Claude 3.7 生成了一个并发测试脚本。

## 使用说明

安装依赖：

```bash
pip install aiohttp
# 网不好用下面这个
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple aiohttp
```

只需要修改以下配置项，然后 `python main.py` 运行即可。

- concurrency: 并发数，位于 111 行中
- model: 同 vllm serve 启动时使用的 Model Tag 名称，位于 12 行中

在 Autodl 上租的 4*4090D 运行 32B 模型参考结果：

```bash
======= Test Results =======
Concurrency level: 500
Successful requests: 500/500

Performance Metrics:
  Total time:35.24 seconds
  Average latency: 21.34 seconds
  Average token speed: 6.33 tokens/second
  Overall token generation speed: 1419.03 tokens/second
  P50 latency: 21.45 seconds
  P95 latency: 35.19 seconds
  P99 latency: 35.19 seconds
  Total output tokens: 50000
```
