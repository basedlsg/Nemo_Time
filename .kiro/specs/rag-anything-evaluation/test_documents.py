#!/usr/bin/env python3
"""
Test document dataset for RAG-Anything evaluation.
Contains sample Chinese regulatory documents for processing tests.
"""

import os
import tempfile
from pathlib import Path
from typing import Dict, List


class TestDocumentGenerator:
    """Generate test documents for evaluation"""
    
    def __init__(self, output_dir: str = "./test_documents"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
    
    def create_all_test_documents(self) -> Dict[str, str]:
        """Create all test documents and return file paths"""
        documents = {}
        
        documents["td_001"] = self.create_gd_solar_regulation()
        documents["td_002"] = self.create_sd_wind_technical_table()
        documents["td_003"] = self.create_nm_coal_formula_doc()
        documents["td_004"] = self.create_mixed_content_doc()
        documents["td_005"] = self.create_english_technical_doc()
        
        return documents
    
    def create_gd_solar_regulation(self) -> str:
        """Create Guangdong solar regulation document (text-heavy)"""
        content = """# 广东省分布式光伏发电管理办法

## 第一章 总则

第一条 为规范分布式光伏发电项目管理，促进分布式光伏发电健康有序发展，根据《可再生能源法》、《电力法》等法律法规，结合本省实际，制定本办法。

第二条 本办法适用于在广东省行政区域内建设的分布式光伏发电项目的备案、并网、运营等管理活动。

第三条 分布式光伏发电是指在用户场地附近建设，运行方式以用户侧自发自用、多余电量上网，且在配电系统平衡调节为特征的光伏发电设施。

## 第二章 项目备案

第四条 分布式光伏发电项目实行备案制管理。项目备案由县级以上发展改革部门负责。

第五条 申请项目备案应当提交以下材料：
1. 分布式光伏发电项目备案申请表
2. 项目建设方案和设计文件
3. 用电户同意项目建设的证明文件
4. 土地使用权或屋顶使用权证明
5. 电网接入系统方案

第六条 发展改革部门应当在收到完整备案材料后15个工作日内完成备案手续。

## 第三章 并网管理

第七条 分布式光伏发电项目并网应当符合国家和省有关技术标准，满足电网安全运行要求。

第八条 项目单位应当向电网企业提出并网申请，提交以下材料：
- 项目备案文件
- 电气设计图纸和技术参数
- 设备合格证明和检测报告
- 施工和调试方案

第九条 电网企业应当在收到并网申请后20个工作日内完成接入系统方案审查，并出具审查意见。

第十条 分布式光伏发电项目应当安装双向电能计量装置，计量装置应当符合国家相关标准。

## 第四章 运营管理

第十一条 分布式光伏发电项目投产后，项目单位应当建立运营管理制度，确保设备安全稳定运行。

第十二条 项目单位应当定期对光伏发电设备进行维护保养，发现安全隐患应当及时处理。

第十三条 电网企业应当为分布式光伏发电项目提供并网服务，不得设置不合理的技术门槛。

## 第五章 监督管理

第十四条 发展改革部门应当加强对分布式光伏发电项目的监督管理，建立项目信息管理系统。

第十五条 对违反本办法规定的行为，由相关部门依法予以处理。

## 第六章 附则

第十六条 本办法自发布之日起施行，有效期5年。

---

附件：分布式光伏发电项目备案申请表

项目名称：_________________
建设地点：_________________
建设规模：_________________MW
投资总额：_________________万元
建设单位：_________________
联系方式：_________________

备案机关意见：
□ 同意备案
□ 不予备案

备案机关（盖章）：_________________
备案时间：_________________
"""
        
        filepath = self.output_dir / "gd_solar_regulation.md"
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return str(filepath)
    
    def create_sd_wind_technical_table(self) -> str:
        """Create Shandong wind technical standards document (table-heavy)"""
        content = """# 山东省风电项目技术标准

## 风电机组技术要求

### 基本技术参数

| 参数名称 | 陆上风电 | 海上风电 | 单位 | 备注 |
|---------|---------|---------|------|------|
| 额定功率 | 2.0-3.0 | 5.0-8.0 | MW | 单机容量 |
| 轮毂高度 | 80-120 | 90-150 | m | 地面至轮毂中心 |
| 风轮直径 | 110-150 | 150-200 | m | 叶片扫掠直径 |
| 切入风速 | 3.0 | 3.0 | m/s | 开始发电风速 |
| 额定风速 | 11-13 | 12-14 | m/s | 达到额定功率风速 |
| 切出风速 | 25 | 25 | m/s | 停机保护风速 |
| 生存风速 | 50 | 70 | m/s | 极端风速 |

### 电气技术要求

| 项目 | 技术指标 | 检测标准 |
|------|---------|---------|
| 电压等级 | 35kV/110kV | GB/T 19963 |
| 功率因数 | 0.95以上 | IEC 61400-21 |
| 电能质量 | 谐波<5% | GB/T 14549 |
| 低电压穿越 | 满足国标要求 | GB/T 19963 |
| 频率适应性 | 49.5-50.5Hz | GB/T 15945 |

### 环境适应性要求

#### 陆上风电环境条件

| 环境因素 | 技术要求 | 测试方法 |
|---------|---------|---------|
| 工作温度 | -30℃ ~ +40℃ | IEC 61400-1 |
| 相对湿度 | ≤95% | GB/T 2423.3 |
| 海拔高度 | ≤2000m | IEC 61400-1 |
| 抗震等级 | 8度 | GB 50011 |
| 防雷等级 | 一级 | GB 50057 |

#### 海上风电环境条件

| 环境因素 | 技术要求 | 测试方法 |
|---------|---------|---------|
| 工作温度 | -20℃ ~ +45℃ | IEC 61400-3 |
| 盐雾等级 | C5-M | ISO 12944 |
| 波浪高度 | 有效波高≤15m | IEC 61400-3 |
| 风浪联合 | 50年一遇 | IEC 61400-3 |
| 防腐等级 | 25年 | ISO 12944 |

## 并网技术要求

### 电能质量指标

| 指标名称 | 限值 | 测量点 | 标准 |
|---------|------|-------|------|
| 电压偏差 | ±7% | 并网点 | GB/T 12325 |
| 频率偏差 | ±0.2Hz | 并网点 | GB/T 15945 |
| 电压谐波 | <3% | 并网点 | GB/T 14549 |
| 电压闪变 | Plt≤0.4 | 并网点 | GB/T 12326 |
| 三相不平衡 | <2% | 并网点 | GB/T 15543 |

### 保护装置配置

| 保护类型 | 35kV | 110kV | 220kV |
|---------|------|-------|-------|
| 主保护 | 差动保护 | 差动保护 | 差动保护 |
| 后备保护 | 过流保护 | 距离保护 | 距离保护 |
| 辅助保护 | 零序保护 | 零序保护 | 零序保护 |
| 故障录波 | 必须 | 必须 | 必须 |
| 同期装置 | 必须 | 必须 | 必须 |

## 验收标准

### 设备验收项目

1. **机械验收**
   - 基础验收：混凝土强度≥C30
   - 塔筒验收：垂直度偏差<1/1000
   - 叶片验收：动平衡<G2.5级

2. **电气验收**
   - 绝缘测试：≥1000MΩ
   - 接地电阻：≤4Ω
   - 保护定值：按调度要求

3. **性能验收**
   - 功率曲线测试
   - 电能质量测试
   - 噪声测试：≤45dB(A)

### 验收程序

| 阶段 | 验收内容 | 责任单位 | 时限 |
|------|---------|---------|------|
| 设备到货 | 外观检查、技术文件 | 建设单位 | 3天 |
| 安装完成 | 安装质量、调试记录 | 监理单位 | 7天 |
| 并网前 | 保护试验、性能测试 | 电网公司 | 15天 |
| 投产后 | 运行考核、性能评估 | 调度机构 | 30天 |

---

注：本标准参考IEC 61400系列标准和国家相关技术规范制定。
"""
        
        filepath = self.output_dir / "sd_wind_technical_standards.md"
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return str(filepath)
    
    def create_nm_coal_formula_doc(self) -> str:
        """Create Inner Mongolia coal power formula document (formula-heavy)"""
        content = """# 内蒙古煤电并网计算公式文档

## 电力系统基本计算

### 功率计算公式

#### 有功功率计算
```
P = U × I × cosφ
```
其中：
- P: 有功功率 (MW)
- U: 线电压 (kV)  
- I: 线电流 (A)
- cosφ: 功率因数

#### 无功功率计算
```
Q = U × I × sinφ
```
其中：
- Q: 无功功率 (MVar)
- sinφ = √(1 - cos²φ)

#### 视在功率计算
```
S = √(P² + Q²) = U × I
```

### 短路电流计算

#### 三相短路电流
```
I₃ = U_n / (√3 × X_Σ)
```
其中：
- I₃: 三相短路电流 (kA)
- U_n: 系统额定电压 (kV)
- X_Σ: 系统总电抗 (Ω)

#### 单相接地短路电流
```
I₁ = 3 × U_n / (X₁ + X₂ + X₀)
```
其中：
- I₁: 单相接地短路电流 (kA)
- X₁: 正序电抗 (Ω)
- X₂: 负序电抗 (Ω)  
- X₀: 零序电抗 (Ω)

## 发电机并网计算

### 同步发电机功率计算

#### 电磁功率
```
P_em = (E_q × U × sinδ) / X_d
```
其中：
- P_em: 电磁功率 (MW)
- E_q: 发电机内电势 (kV)
- U: 端电压 (kV)
- δ: 功角 (度)
- X_d: 直轴同步电抗 (Ω)

#### 励磁电流计算
```
I_f = (E_q - U × cosφ) / (X_d - X_q) × I_a × sinφ + E_q / X_ad
```
其中：
- I_f: 励磁电流 (A)
- I_a: 电枢电流 (A)
- X_q: 交轴同步电抗 (Ω)
- X_ad: 直轴电枢反应电抗 (Ω)

### 调速器计算

#### 频率调节
```
Δf/f_n = -R × ΔP/P_n
```
其中：
- Δf: 频率偏差 (Hz)
- f_n: 额定频率 50Hz
- R: 调差系数 (通常为4-5%)
- ΔP: 功率变化 (MW)
- P_n: 额定功率 (MW)

#### 一次调频响应时间
```
T_g = K_g / (1 + T_g × s)
```
其中：
- T_g: 调速器时间常数 (s)
- K_g: 调速器增益
- s: 拉普拉斯算子

## 电网稳定性计算

### 静态稳定性

#### 功角特性
```
P = P_max × sin(δ)
P_max = (E × U) / X
```

#### 稳定判据
```
dP/dδ > 0  (静态稳定条件)
```

### 暂态稳定性

#### 摇摆方程
```
M × d²δ/dt² = P_m - P_e - D × dδ/dt
```
其中：
- M: 惯性常数 (s²)
- P_m: 机械功率 (MW)
- P_e: 电磁功率 (MW)
- D: 阻尼系数

#### 临界切除时间
```
t_cr = √(2M × (δ_cr - δ_0) / (P_m - P_e0))
```

## 继电保护整定计算

### 过电流保护

#### 电流速断保护
```
I_set = K_rel × I_max / K_return
```
其中：
- I_set: 整定电流 (A)
- K_rel: 可靠系数 (1.2-1.3)
- I_max: 最大短路电流 (A)
- K_return: 返回系数 (0.85-0.95)

#### 过电流保护时限
```
t = t_max + Δt
```
其中：
- t: 保护动作时间 (s)
- t_max: 下级保护最大动作时间 (s)
- Δt: 时间级差 (0.3-0.5s)

### 距离保护

#### 阻抗整定
```
Z_set = K_rel × Z_line × L_prot / L_line
```
其中：
- Z_set: 整定阻抗 (Ω)
- Z_line: 线路阻抗 (Ω/km)
- L_prot: 保护范围 (km)
- L_line: 线路长度 (km)

## 经济调度计算

### 等微增率准则
```
λ = dC_i/dP_i = 常数
```
其中：
- λ: 系统边际成本 (元/MWh)
- C_i: 第i台机组成本函数
- P_i: 第i台机组出力 (MW)

### 煤耗特性曲线
```
C(P) = a × P² + b × P + c
```
其中：
- C(P): 煤耗量 (t/h)
- a, b, c: 煤耗特性系数
- P: 机组出力 (MW)

### 网损计算
```
P_loss = Σ R_i × I_i²
```
其中：
- P_loss: 网络损耗 (MW)
- R_i: 第i条线路电阻 (Ω)
- I_i: 第i条线路电流 (A)

---

注：以上公式适用于内蒙古电网330kV及以下电压等级的煤电机组并网计算。
具体参数应根据实际设备和系统条件确定。
"""
        
        filepath = self.output_dir / "nm_coal_formulas.md"
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return str(filepath)
    
    def create_mixed_content_doc(self) -> str:
        """Create mixed content document with text, tables, formulas, and diagrams"""
        content = """# 综合能源项目审批流程指南

## 项目概述

综合能源项目是指在同一区域内，统筹多种能源资源，采用先进的物理信息技术和创新管理模式，实现多种异质能源子系统之间的协调规划、优化运行、协同管理、交互响应和互补互济，在满足系统内多元化用能需求的同时，有效提升能源利用效率，促进能源清洁化利用的新型一体化的能源系统。

## 审批流程图

```
[项目立项] → [可研报告] → [环评审批] → [用地审批] → [规划许可] → [施工许可] → [并网申请] → [竣工验收]
     ↓           ↓           ↓           ↓           ↓           ↓           ↓           ↓
  发改委      发改委      生态环境    自然资源    住建部门    住建部门    电网公司    多部门联合
  (15天)      (30天)      (60天)      (20天)      (15天)      (7天)       (30天)      (15天)
```

## 项目分类及审批权限

### 按投资规模分类

| 项目类型 | 投资规模 | 审批部门 | 审批时限 | 备注 |
|---------|---------|---------|---------|------|
| 大型项目 | ≥10亿元 | 国家发改委 | 90天 | 需国务院审批 |
| 中型项目 | 1-10亿元 | 省发改委 | 60天 | 省级审批 |
| 小型项目 | <1亿元 | 市县发改委 | 30天 | 地方审批 |

### 按能源类型分类

| 能源类型 | 主管部门 | 特殊要求 | 审批要点 |
|---------|---------|---------|---------|
| 光伏发电 | 能源局 | 土地性质 | 用地合规性 |
| 风力发电 | 能源局 | 环境影响 | 鸟类保护 |
| 储能系统 | 能源局 | 安全评估 | 消防安全 |
| 充电设施 | 住建部门 | 规划许可 | 配电容量 |
| 供热系统 | 住建部门 | 管网接入 | 热力平衡 |

## 技术经济指标计算

### 投资回收期计算

#### 静态投资回收期
```
T_s = I₀ / A
```
其中：
- T_s: 静态投资回收期 (年)
- I₀: 初始投资 (万元)
- A: 年平均净收益 (万元/年)

#### 动态投资回收期
```
NPV = Σ(CI - CO)_t / (1 + r)^t = 0
```
其中：
- NPV: 净现值
- CI: 现金流入
- CO: 现金流出  
- r: 折现率
- t: 时间 (年)

### 能效指标计算

#### 综合能源利用效率
```
η_total = (E_useful / E_input) × 100%
```

#### 一次能源利用率
```
PER = E_output / (E_fuel / η_grid)
```
其中：
- PER: 一次能源利用率
- E_output: 系统输出能量 (kWh)
- E_fuel: 燃料消耗量 (kWh)
- η_grid: 电网效率 (通常取0.35)

## 审批材料清单

### 基础材料

1. **项目申请报告**
   - 项目基本情况
   - 建设内容和规模
   - 投资估算和资金来源
   - 建设条件和选址方案

2. **可行性研究报告**
   - 技术方案比选
   - 经济效益分析
   - 风险评估
   - 实施计划

### 专项评估报告

| 评估类型 | 报告名称 | 编制单位资质 | 有效期 |
|---------|---------|-------------|-------|
| 环境影响 | 环境影响评价报告 | 环评甲级 | 5年 |
| 安全评价 | 安全预评价报告 | 安评甲级 | 3年 |
| 职业卫生 | 职业病危害预评价 | 职卫甲级 | 3年 |
| 地质灾害 | 地质灾害危险性评估 | 地勘甲级 | 长期有效 |
| 水土保持 | 水土保持方案 | 水保乙级以上 | 长期有效 |

### 技术文件

#### 设计文件要求

1. **总体设计**
   - 总平面布置图 (1:500)
   - 工艺流程图
   - 主要设备清单
   - 技术经济指标

2. **专业设计**
   - 建筑设计图纸
   - 结构设计计算书
   - 电气系统图
   - 给排水设计
   - 暖通空调设计

#### 设备技术参数

| 设备类型 | 技术参数 | 性能指标 | 检测标准 |
|---------|---------|---------|---------|
| 光伏组件 | 功率≥400W | 效率≥20% | IEC 61215 |
| 逆变器 | 效率≥98% | THD<3% | IEC 62109 |
| 储能电池 | 循环寿命≥6000次 | 效率≥95% | IEC 62619 |
| 变压器 | 损耗≤国标 | 噪声≤65dB | GB 1094 |

## 并网接入要求

### 电能质量标准

#### 电压质量指标
```
电压偏差 = (U_actual - U_nominal) / U_nominal × 100%
```
要求：±7% (35kV及以下)，±3% (110kV及以上)

#### 谐波限值
| 谐波次数 | 电压谐波限值 | 电流谐波限值 |
|---------|-------------|-------------|
| 3次 | 4.0% | 按容量比例 |
| 5次 | 4.0% | 按容量比例 |
| 7次 | 4.0% | 按容量比例 |
| 总谐波 | 5.0% | 按容量比例 |

### 保护配置要求

#### 35kV接入
- 主保护：电流速断 + 过电流
- 辅助保护：零序过流 + 低频减载
- 自动装置：备自投 + 故障录波

#### 110kV接入  
- 主保护：差动保护 + 距离保护
- 后备保护：零序保护 + 过负荷
- 自动装置：重合闸 + 安稳装置

## 验收标准

### 分阶段验收

| 验收阶段 | 验收内容 | 验收标准 | 责任单位 |
|---------|---------|---------|---------|
| 隐蔽工程 | 基础、管线 | 设计要求 | 监理单位 |
| 设备安装 | 设备就位、接线 | 安装规范 | 施工单位 |
| 系统调试 | 功能测试 | 技术协议 | 调试单位 |
| 并网验收 | 保护试验 | 电网标准 | 电网公司 |
| 竣工验收 | 整体性能 | 设计指标 | 建设单位 |

### 性能考核指标

#### 发电效率考核
```
年发电效率 = 实际年发电量 / 理论年发电量 × 100%
```
要求：≥85%

#### 可用率考核  
```
设备可用率 = (8760 - 故障停运小时) / 8760 × 100%
```
要求：≥95%

---

**注意事项：**
1. 所有审批材料需加盖公章，并提供电子版
2. 涉及多个部门的需要并联审批，避免串联等待
3. 重大项目需要专家评审，提前做好准备工作
4. 审批过程中如有政策调整，按最新政策执行

**联系方式：**
- 项目审批咨询：400-XXX-XXXX
- 技术支持热线：400-XXX-YYYY  
- 在线申报平台：www.energy-approval.gov.cn
"""
        
        filepath = self.output_dir / "mixed_content_approval_guide.md"
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return str(filepath)
    
    def create_english_technical_doc(self) -> str:
        """Create English technical document for multilingual testing"""
        content = """# Grid Connection Technical Specifications

## Overview

This document outlines the technical requirements for connecting renewable energy systems to the electrical grid in accordance with international standards and local regulations.

## General Requirements

### Voltage Levels and Standards

| Voltage Level | Application | Standard | Frequency |
|---------------|-------------|----------|-----------|
| Low Voltage | < 1 kV | IEC 60038 | 50 Hz ± 0.2 Hz |
| Medium Voltage | 1-35 kV | IEC 60038 | 50 Hz ± 0.2 Hz |
| High Voltage | 35-110 kV | IEC 60038 | 50 Hz ± 0.2 Hz |
| Extra High Voltage | > 110 kV | IEC 60038 | 50 Hz ± 0.1 Hz |

### Power Quality Requirements

#### Voltage Regulation
- Steady-state voltage variation: ±5% of nominal voltage
- Rapid voltage changes: <3% for normal operation
- Voltage unbalance: <2% under normal conditions

#### Harmonic Distortion Limits
```
THD_v = √(Σ(V_h)²) / V_1 × 100%
```
Where:
- THD_v: Total Harmonic Distortion of voltage
- V_h: RMS value of harmonic voltage of order h
- V_1: RMS value of fundamental voltage

Limits:
- Individual voltage harmonics: <3% (h ≤ 25), <1.5% (h > 25)
- Total voltage harmonic distortion: <5%

### Protection Systems

#### Overcurrent Protection
```
I_pickup = K_reliability × I_load_max / K_return
```
Where:
- I_pickup: Protection pickup current
- K_reliability: Reliability factor (1.1-1.3)
- I_load_max: Maximum load current
- K_return: Return ratio (0.85-0.95)

#### Distance Protection
```
Z_reach = K_reliability × Z_line × Coverage_factor
```
Where:
- Z_reach: Protection reach impedance
- Z_line: Line impedance per unit length
- Coverage_factor: Typically 0.8-0.85 for Zone 1

## Renewable Energy Integration

### Solar PV Systems

#### Technical Parameters
| Parameter | Requirement | Test Standard |
|-----------|-------------|---------------|
| Power Factor | 0.95 leading to 0.95 lagging | IEEE 1547 |
| Efficiency | >95% at rated power | IEC 61683 |
| Voltage Ride-Through | Per grid code | IEEE 1547.1 |
| Frequency Response | 47-52 Hz continuous | IEEE 1547 |

#### Anti-Islanding Protection
```
t_detection ≤ 2.0 seconds
```
For all islanding conditions as per IEEE 1547.

### Wind Power Systems

#### Grid Code Compliance
- Low Voltage Ride Through (LVRT): Remain connected for voltage dips to 0.15 p.u. for 625ms
- High Voltage Ride Through (HVRT): Remain connected for voltage rises to 1.1 p.u. for 60 minutes
- Frequency Response: Primary response within 2-30 seconds

#### Power Control
```
P_available = 0.5 × ρ × A × v³ × C_p × η_total
```
Where:
- P_available: Available wind power
- ρ: Air density (kg/m³)
- A: Rotor swept area (m²)
- v: Wind speed (m/s)
- C_p: Power coefficient
- η_total: Total system efficiency

## Connection Procedures

### Application Process

1. **Pre-Application Consultation**
   - System impact study
   - Connection point identification
   - Preliminary design review

2. **Formal Application Submission**
   - Technical specifications
   - Single-line diagrams
   - Protection settings
   - Control system description

3. **Technical Review**
   - Grid impact assessment
   - Protection coordination study
   - Power quality analysis
   - Stability assessment

4. **Connection Agreement**
   - Technical requirements
   - Commercial terms
   - Operational procedures
   - Maintenance responsibilities

### Testing and Commissioning

#### Factory Acceptance Tests (FAT)
- Type testing per IEC standards
- Routine testing of all equipment
- Witness testing by utility representatives

#### Site Acceptance Tests (SAT)
- Installation verification
- Functional testing
- Protection system testing
- Communication system testing

#### Performance Testing
```
Performance_ratio = E_actual / E_expected
```
Where performance ratio should be ≥0.85 for solar PV systems.

## Monitoring and Control

### SCADA Integration
- Real-time data acquisition
- Remote control capabilities
- Alarm and event logging
- Historical data storage

### Communication Protocols
| Protocol | Application | Standard |
|----------|-------------|----------|
| IEC 61850 | Substation automation | IEC 61850 |
| DNP3 | SCADA communication | IEEE 1815 |
| Modbus | Device communication | Modbus.org |
| IEC 60870-5-104 | Telecontrol | IEC 60870-5-104 |

## Maintenance Requirements

### Preventive Maintenance Schedule

| Equipment Type | Inspection Frequency | Major Maintenance |
|----------------|---------------------|-------------------|
| Transformers | Monthly visual, Annual thermal | 5-year oil analysis |
| Switchgear | Quarterly inspection | 3-year contact maintenance |
| Protection relays | Semi-annual testing | Annual calibration |
| Communication systems | Monthly status check | Annual system update |

### Performance Monitoring

#### Key Performance Indicators (KPIs)
```
Availability = (Total_time - Outage_time) / Total_time × 100%
```
Target availability: ≥98% for critical equipment

```
Reliability = MTBF / (MTBF + MTTR)
```
Where:
- MTBF: Mean Time Between Failures
- MTTR: Mean Time To Repair

## Compliance and Standards

### International Standards
- IEC 61400 series: Wind turbine standards
- IEC 61215: Photovoltaic module qualification
- IEEE 1547: Distributed resource interconnection
- IEC 61850: Substation automation

### Safety Requirements
- Personnel safety procedures per OSHA standards
- Equipment safety certification per IEC 61508
- Cybersecurity measures per IEC 62443
- Environmental protection per ISO 14001

---

**Document Control:**
- Version: 2.1
- Effective Date: January 2024
- Review Date: January 2025
- Approved by: Technical Standards Committee
"""
        
        filepath = self.output_dir / "english_technical_specs.md"
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return str(filepath)


def main():
    """Generate all test documents"""
    generator = TestDocumentGenerator()
    
    print("Generating test documents for RAG-Anything evaluation...")
    print("=" * 60)
    
    documents = generator.create_all_test_documents()
    
    print(f"\n✅ Generated {len(documents)} test documents:")
    for doc_id, filepath in documents.items():
        file_size = os.path.getsize(filepath) / 1024  # KB
        print(f"  - {doc_id}: {os.path.basename(filepath)} ({file_size:.1f} KB)")
    
    print(f"\n📁 Documents saved to: {generator.output_dir}")
    print("\nDocument types generated:")
    print("  - Chinese regulatory text (Guangdong solar)")
    print("  - Technical tables (Shandong wind)")
    print("  - Mathematical formulas (Inner Mongolia coal)")
    print("  - Mixed content (Comprehensive approval guide)")
    print("  - English technical specs (Multilingual test)")
    
    return documents


if __name__ == "__main__":
    main()