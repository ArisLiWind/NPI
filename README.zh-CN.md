# NPI：神经扰动推断

<p align="center">
  <a href="README.md">English</a> · <a href="README.zh-CN.md">简体中文</a>
</p>

> 本 fork 保留原始 NPI 的代码、实验和数据结构。当前新增内容仅限于双语文档与后续复现规划，不改变原论文方法和训练代码。

## 成果来源与本 fork 的目标

NPI（Neural Perturbational Inference，神经扰动推断）由南方科技大学 NCC Lab 开发，研究成果发表于 *Nature Methods*（2025）：[Mapping effective connectivity by virtually perturbing a surrogate brain](https://www.nature.com/articles/s41592-025-02654-x)。本仓库是作者公开的代码和数据资源。

这项工作的核心目标，是从观测到的脑区时间序列中学习一个能够近似脑动力学的人工神经网络代理模型，然后在这个“代理脑”中逐个扰动脑区，观察其他脑区的响应，从而估计全脑有向有效连接（effective connectivity, EC）。

本 fork 的目标是：

1. 保留作者原始代码、notebook、模拟数据和全脑 EC 资源；
2. 为中文用户提供与英文 README 对应的说明；
3. 在不悄悄改变原始实现的前提下，后续增加小规模复现和外部数据验证；
4. 明确区分“论文原始结果”和“本 fork 的复现实验结果”。

这里的“有效连接”是对学习到的代理动力学系统进行虚拟扰动后得到的有向影响估计。它不能直接等同于对人脑观测数据本身作出的生物学因果证明。

## 论文方法概览

### 1. 用神经网络学习代理脑

给定包含多个脑区的时间序列，模型学习：

```text
[x(t-k+1), ..., x(t)]  ->  神经网络代理模型  ->  x(t+1)
```

其中每个 `x(t)` 是所有 ROI 在时刻 `t` 的活动向量。仓库提供 MLP、CNN、RNN 和 VAR 等代理模型。训练目标是下一时刻预测误差，通常使用均方误差（MSE）和 Adam 优化器。

### 2. 用随机噪声滚动得到模型 FC

训练完成后，将模型的预测结果反馈给下一步，并持续加入噪声，生成较长的模型时间序列。对该序列计算相关矩阵，得到模型功能连接（model FC），再与经验时间序列的 FC 比较。

### 3. 用虚拟扰动估计有向 EC

对每个源脑区 `i`，在输入历史的最后一个时间步增加扰动，重新计算模型输出。源区 `i` 引起目标区 `j` 的平均响应被写入 EC 矩阵的 `(i, j)` 位置：

```text
EC[i, j] = mean(model(扰动 i 后的输入) - model(原始输入))
```

因此矩阵的行表示源区，列表示目标区。正值通常表示兴奋性方向，负值通常表示抑制性方向；具体解释仍依赖数据预处理、扰动尺度和模型拟合质量。

## 仓库内容

- `NPI.py`：代理模型、训练、模型 FC 和模型 EC 的核心实现。
- `NPI_demo(RNN).ipynb`：带已知结构连接/真实 EC 的 RNN 合成数据示例。
- `NPI_demo(WBM).ipynb`：全脑模型（WBM）模拟示例。
- `NPI_demo(fMRI).ipynb`：HCP 个体静息态 fMRI 示例。
- `RNN_simulation_data/`、`WBM_simulation_data/`：合成信号及其参考连接矩阵。
- `real_fMRI_data/`：仓库提供的 HCP 个体数据示例。
- `Whole-brain_EC/`：不同脑图谱下的群体 EC 资源。

## 安装与运行

```bash
git clone https://github.com/ArisLiWind/NPI.git
cd NPI
pip install -r requirements.txt
jupyter notebook
```

建议先运行 `NPI_demo(RNN).ipynb`，因为它同时提供模拟信号、结构连接和真实 EC，最适合检查“训练—模型 FC—虚拟扰动 EC—参考矩阵比较”的完整链路。

## 外部数据验证注意事项

外部数据应先整理为 `[时间点, ROI]` 的矩阵，并明确 ROI 图谱、时间单位、预处理方法和训练/测试划分。若要验证 EC，最好同时提供独立的刺激传播、已知生成模型连接或其他方向性基准；只有经验 FC 时，只能验证动力学拟合和 FC 一致性，不能单独证明 EC 正确。

不要把不同受试者或不同 run 直接拼成一条连续时间序列；应按受试者/run 独立训练或进行明确的组水平建模。

## 引用

```text
Luo, Z., Peng, K., Liang, Z. et al. Mapping effective connectivity by
virtually perturbing a surrogate brain. Nature Methods (2025).
https://doi.org/10.1038/s41592-025-02654-x
```

## 许可证与联系

原仓库使用 Apache-2.0 许可证。问题和评论请联系 [NCC Lab](https://www.sustech.edu.cn/en/faculties/liuquanying.html)。
