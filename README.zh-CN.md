# AI–半导体反馈研究实验室

[English](README.md) | **简体中文**

> **交互式研究看板：** [Feedback Observatory](https://ifrvn.github.io/ai-semiconductor-feedback/) · [网站部署与本地预览](site/README.md)

本项目使用可复现的 Python 模型，探索 **AI 能力、有效算力成本、半导体产能、商业化延迟和可投资资本**之间的动态反馈关系。它既包含可追溯的历史观测与有限的预测检验，也包含用于理解机制的假设情景模拟。

> **重要说明：** 模型的初始值、反馈系数、扩产融资与冲击参数尚未通过真实产业数据完成校准。2026—2045 年的模拟曲线**不是未来预测**，也不能据此认定 AI 对半导体研发存在已证实的因果效应。

## 模型概览

基础动态模型包含五个主要状态：

| 变量 | 含义 |
| --- | --- |
| `A` | AI 能力指数，越高代表模型中的能力越强 |
| `C` | 单位有效算力成本，越低越好 |
| `Q` | 每年可交付的有效算力产能 |
| `T` | 商业化延迟，单位为年 |
| `B` | 可投资资本存量 |

投资流量为 `I_A = u_A B` 和 `I_Q = u_Q B`；用于 AI 研发的有效算力受到预算和可用产能共同约束。模型考虑历史 AI 能力与历史投资承诺的滞后效应、折旧、成本下限及产能瓶颈。公式与局限见 [模型文档](docs/model.md)。

此外，四部门模型单独模拟晶圆制造、HBM、先进封装和电力基础设施，并区分实际可交付量、需求与稀缺性带来的市场价格变化。此处的“交付量”是**归一化模型指数**，并非真实芯片出货量。

## 快速开始

需要 Python 3.11 或更新版本。基础模拟、CSV 导出、测试与敏感性分析无需额外依赖。

```bash
python -m feedback_lab simulate --scenario baseline --output results/baseline.csv
python -m feedback_lab compare --output results/comparison.csv
python -m feedback_lab sensitivity --output results/sensitivity.csv
python -m unittest discover -s tests -v
```

如需生成静态图：

```bash
pip install -e ".[plot]"
python -m feedback_lab plot --input results/comparison.csv --output results/comparison.png
```

## 历史数据与预测检验

项目收录了有来源标注的历史数据：

- **Epoch AI**：2023 年第一季度至 2025 年第四季度的 AI 芯片理论性能/美元季度指标，数据经过分组、取整和购买金额加权，不能直接代表实际训练任务效率。
- **SIA**：2022—2025 年全球半导体销售额，属于销售收入数据，**不能直接当作物理产能**。

运行历史数据分析：

```bash
python -m feedback_lab.calibration --output results/calibration.json
python -m feedback_lab.empirical_validation --output results/empirical_validation.json
```

预测检验使用 2025 年留出时段及按时间推进的滚动检验，比较“沿用上期数值”“历史增长趋势”和“对数线性趋势”三种简单方法。误差指标为 **Log RMSE（对数均方根误差）**，数值越小表示该样本上的误差越小。

| 检验方式 | 沿用上期数值 | 历史增长趋势 | 对数线性趋势 |
| --- | ---: | ---: | ---: |
| 2025 年预测检验 | 0.473 | **0.342** | 0.486 |
| 滚动预测下一季度 | 0.144 | **0.112** | 0.214 |
| 滚动预测未来四季度 | 0.611 | **0.545** | 0.585 |

这些只是**小样本历史预测诊断**，并不意味着历史增长趋势将始终表现最好，更不能据此证明 AI→芯片产业的因果反馈强度。

## 研究模块

### 1. AI 辅助芯片研发的因果证据

整理实验研究、EDA 厂商案例、产业验证及生产结果，区分局部效率改善与行业层面的因果影响。

```bash
python -m feedback_lab.evidence --output results/evidence_audit.json
```

参考：[研究证据说明](docs/ai_chip_evidence.md) · [证据表](data/evidence/ai_semiconductor_studies.csv)

### 2. AI 辅助研发如何传导到芯片成本

区分元器件成本、设计效率、良率与实际工作负载吞吐量，避免将某个环节的局部改进直接等同于全行业降本。

```bash
python -m feedback_lab.transmission --output results/transmission.json
```

参考：[成本传导模型](docs/cost_transmission.md)

### 3. 芯片组件的动态反馈

分别模拟 HBM、逻辑芯片、封装、网络与能源等因素，并考虑计算、内存、网络和电力约束。

```bash
python -m feedback_lab.dynamic_experiments --output results/dynamic_components.csv
```

参考：[动态组件模型](docs/dynamic_components.md)

### 4. 四部门产能、投资与稀缺性

模拟晶圆、HBM、先进封装、电力四个互补环节的扩产、折旧、建设延迟和瓶颈影响。

```bash
python -m feedback_lab.sector_experiments --output results/sector_capacity.csv
```

当前版本将**内部投资**（`investment_fraction × B`）与**外部项目融资**（`expansion_project_financing`）分开核算。外部项目融资直接用于扩产，不再计入资本存量 `B`，以避免重复计算。投资分配会参考各环节需求与产能之间的缺口，但建设完成前不会立即增加产能。

外部项目融资默认值 `0.75` 以及瓶颈响应系数都是**研究者设定的示意参数**，不是根据行业资本开支数据估算出的真实数值。模型假定 2026 年之前没有已承诺、尚在建设中的产能，因此即使增加投资，初期仍可能出现供给下降。

参考：[四部门产能模型](docs/sector_capacity.md)

### 5. 不确定性与参数敏感性

在预先指定的参数范围内抽样，对比有无 AI→芯片成本反馈的模拟结果，并纳入外部扩产融资与瓶颈投资响应等假设。

```bash
python -m feedback_lab.uncertainty --samples 200 --seed 20261030 --output results/uncertainty.json
```

模拟结果的第 5—95 百分位范围**不是统计置信区间，也不代表真实世界发生的概率**。

参考：[不确定性方法](docs/uncertainty.md)

## 交互式网站

网站采用原生 HTML、CSS 和 JavaScript，不需要额外后端或 API 密钥。数据由 Python 脚本生成，支持中文、英文和明暗主题。

本地预览：

```bash
PYTHONPATH=. python site/build_data.py
python -m http.server 8000 --directory site
```

浏览器访问 `http://localhost:8000`。直接双击打开 `index.html` 可能因浏览器的本地文件限制而无法读取 `data.json`。

部署使用 [GitHub Actions](.github/workflows/pages.yml)。首次启用时，在仓库 **Settings → Pages** 中选择 **GitHub Actions** 作为发布来源；推送到 `main` 后由工作流生成数据并发布 `site/`。

## 项目结构

- `feedback_lab/`：基础模型、四部门模拟、校准、检验和敏感性分析
- `site/`：交互式网站及数据生成脚本
- `tests/`：模型数值与回归测试
- `data/`：历史数据、来源记录及研究证据
- `docs/`：模型方程、研究方法和局限说明
- `results/`：运行命令生成的结果文件目录

## 后续研究方向

1. 建立包含日期、计量单位、来源和误差范围的可靠产业数据集。
2. 区分 AI 算法进步与硬件性能/价格改善。
3. 使用对照组或准实验方法识别 AI 工具对芯片设计和制造的因果影响。
4. 使用真实资本开支、建设周期和产能利用率数据校准四部门模型。
5. 在一致的投资与冲击假设下比较不同反馈机制。
6. 在进行预测之前完成历史检验、参数不确定性和结构敏感性分析。

## 许可证与贡献

项目采用 **MIT 许可证**。欢迎提交可复现的研究改进；请为新增数据标注来源，为新增参数说明依据，并明确区分历史事实、模型假设与未来预测。
