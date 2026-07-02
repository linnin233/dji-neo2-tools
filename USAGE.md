# DJI Neo 2 — 关闭近地保护 (Landing Protection) 指南

基于 [dji-firmware-tools](https://github.com/o-gs/dji-firmware-tools) 开源工具，通过 USB 直连 DJI Neo 2 修改飞控参数，**不改固件，只改参数**，安全可恢复。

## 原理

修改飞控参数：

```
g_config.flying_limit.avoid_ground_and_smart_landing_enable
```

| 值 | 效果 |
|----|------|
| `1`（默认） | 近地保护开启 — 靠近地面/障碍物时自动抬升 |
| `0` | 近地保护关闭 — 可贴地飞行、穿越狭窄空间 |

修改后效果：
- ✅ 超低空飞行不再自动抬升
- ✅ 手接降落正常工作
- ✅ Z 轴高度保持准确
- ⚠️ XY 轴极低空时可能有轻微漂移（手动修正即可）
- ✅ 重启后参数持久保留

## 硬件要求

- DJI Neo 2 无人机（初代 Neo 也支持）
- USB-C 数据线（必须支持数据传输）
- Windows 10+ 64-bit（Linux/macOS 也可用，驱动配置更简单）

## 准备工作（一次性）

### 1. 安装 Python 依赖

```bash
pip install --user pyusb pyserial libusb1
```

### 2. 安装 Zadig USB 驱动替换工具

DJI 官方驱动（WinUSB）会锁住设备，需要用 [Zadig](https://zadig.akeo.ie/) 替换为通用驱动。

```
1. 下载 zadig-2.9.exe → 右键 → 以管理员身份运行
2. Options → List All Devices（勾上）
3. 下拉框找到 "BULK Interface (Interface 3~7)"（选任意一个）
4. 驱动类型选 libusb-win32
5. 点 Replace Driver
```

> **注意：** 换驱动后 DJI Assistant 2 将无法连接 Neo 2。如需恢复，用 Zadig 选回 WinUSB 驱动，或重装 DJI Assistant 2。

### 3. 克隆本项目

```bash
git clone https://github.com/o-gs/dji-firmware-tools.git
cd dji-firmware-tools
```

> 本项目已添加 DJI Neo / Neo 2 的产品代码支持，见 `comm_og_service_tool.py` 中的 `NEO` / `NEO2`。

## 使用方法

### 第一步：连接 Neo 2

```
Neo 2 装电池 → 开机 → USB-C 连电脑
```

### 第二步：读取当前参数值

```bash
python comm_og_service_tool.py --bulk NEO2 FlycParam get --alt \
  g_config.flying_limit.avoid_ground_and_smart_landing_enable
```

输出示例：
```
g_config.flying_limit.avoid_ground_and_smart_landing_enable = 1 range = < 0 .. 1 >
```

### 第三步：关闭近地保护

```bash
python comm_og_service_tool.py --bulk NEO2 FlycParam set --alt \
  g_config.flying_limit.avoid_ground_and_smart_landing_enable 0
```

输出示例：
```
g_config.flying_limit.avoid_ground_and_smart_landing_enable = 0 range = < 0 .. 1 >
```

### 第四步：验证

```bash
python comm_og_service_tool.py --bulk NEO2 FlycParam get --alt \
  g_config.flying_limit.avoid_ground_and_smart_landing_enable
```

确保返回 `= 0`。

## 恢复默认

```bash
python comm_og_service_tool.py --bulk NEO2 FlycParam set --alt \
  g_config.flying_limit.avoid_ground_and_smart_landing_enable 1
```

## 探索其他参数

列出 Neo 2 所有可修改的飞控参数：

```bash
# 列出前 50 个参数
python comm_og_service_tool.py --bulk NEO2 FlycParam list --start=0 --count=50 --fmt=2line

# 搜索含指定关键字的参数
python comm_og_service_tool.py --bulk NEO2 FlycParam list --start=0 --count=500 --fmt=2line | grep -i "avoid"
python comm_og_service_tool.py --bulk NEO2 FlycParam list --start=0 --count=500 --fmt=2line | grep -i "fpv"
```

## 性能全开调参套餐 🔥

> **注意：** 以下参数已实测可用。修改前建议先读当前值确认。Neo 2 没有暴露 `max_horiz_vel`（最大水平速度）参数，极速受物理限制无法突破。

### 避障全关（贴地/穿空间必备）

| 参数 | 默认 | 推荐 | 说明 |
|------|------|------|------|
| `user_avoid_enable\|g_config...user_avoid_enable` | 1 | 0 | 前避障 |
| `user_down_avoid_enable\|g_config...user_down_avoid_enable` | 1 | 0 | 下视避障 |
| `user_back_avoid_enable\|g_config...user_back_avoid_enable` | 1 | 0 | 后避障 |
| `user_all_avoid_enable` | 1 | 0 | 全部避障总开关 |
| `g_config.avoid_obstacle_limit_cfg.avoid_obstacle_enable` | 1 | 0 | 避障引擎开关 |
| `enable_avoid_ground_protection` | 1 | 0 | 近地保护（底层） |
| `enable_horizontal_obstacle_avoidance` | 1 | 0 | 水平避障 |
| `enable_downward_vision_position_and_avoidance` | 1 | 0 | 下视定位+避障 |
| `g_config.flying_limit.roof_limit_enable` | 1 | 0 | 屋顶限制（室内用） |

### 姿态激进化

| 参数 | 默认 | 范围 | 推荐 | 说明 |
|------|------|------|------|------|
| `avoid_atti_range` | 20 | 10~60 | 60 | 最大倾斜角度 |
| `quick_spin_tors_rate_limit` | 200 | 90~300 | 300 | 最大旋转速率 (°/s) |
| `near_gnd_vert_acc_limit_amp` | 3 | 1~10 | 10 | 近地加速倍率 |

### 速度/下降调参

| 参数 | 默认 | 范围 | 推荐 | 说明 |
|------|------|------|------|------|
| `ffg_speed_ctrl_perc\|g_config.control.ffg_speed_ctrl_perc` | 40 | 0~100 | 100 | Normal 档前馈增益 |
| `sport_ffg_speed_ctrl_perc\|g_config.control.sport_ffg_speed_ctrl_perc` | 40 | 0~100 | 100 | Sport 档前馈增益 |
| `vert_vel_down_adding\|g_config.control.vert_vel_down_adding` | 0 | -5~5 | 5 | 下降速度加成 (m/s) |
| `vert_vel_down_adding_max` | -6 | -20~0 | -20 | 最大下降速度 (m/s) |

### 刹车灵敏度

| 参数 | 默认 | 范围 | 说明 |
|------|------|------|------|
| `brake_sensitive_fc\|g_config.control.brake_sensitivity_fc` | 0.6 | 0~80 | 飞控刹车力度：0=丝滑滑行，0.6=干脆利落 |
| `brake_sensitive_gain\|g_config.control.brake_sensitivity` | 80 | 0~150 | 刹车增益：越低越松 |

### 限制解除

| 参数 | 默认 | 范围 | 推荐 | 说明 |
|------|------|------|------|------|
| `g_config.flying_limit.max_radius` | 5000 | 15~8000 | 8000 | 最大飞行距离 (m) |
| `g_config.flying_limit.max_height` | 120 | 20~120 | 120 | 最高高度（已到固件上限） |
| `g_config.flying_limit.avoid_ground_and_smart_landing_enable` | 1 | 0~1 | 0 | 智能降落/近地保护 |

### 一键执行（复制粘贴到终端）

```bash
# === 避障全关 ===
python comm_og_service_tool.py --bulk NEO2 FlycParam set --alt "user_avoid_enable|g_config.avoid_obstacle_limit_cfg.user_avoid_enable" 0
python comm_og_service_tool.py --bulk NEO2 FlycParam set --alt "user_down_avoid_enable|g_config.avoid_obstacle_limit_cfg.user_down_avoid_enable" 0
python comm_og_service_tool.py --bulk NEO2 FlycParam set --alt "user_back_avoid_enable|g_config.avoid_obstacle_limit_cfg.user_back_avoid_enable" 0
python comm_og_service_tool.py --bulk NEO2 FlycParam set --alt user_all_avoid_enable 0
python comm_og_service_tool.py --bulk NEO2 FlycParam set --alt g_config.avoid_obstacle_limit_cfg.avoid_obstacle_enable 0
python comm_og_service_tool.py --bulk NEO2 FlycParam set --alt enable_avoid_ground_protection 0
python comm_og_service_tool.py --bulk NEO2 FlycParam set --alt enable_horizontal_obstacle_avoidance 0
python comm_og_service_tool.py --bulk NEO2 FlycParam set --alt enable_downward_vision_position_and_avoidance 0
python comm_og_service_tool.py --bulk NEO2 FlycParam set --alt g_config.flying_limit.roof_limit_enable 0

# === 姿态激進 ===
python comm_og_service_tool.py --bulk NEO2 FlycParam set --alt avoid_atti_range 60
python comm_og_service_tool.py --bulk NEO2 FlycParam set --alt quick_spin_tors_rate_limit 300
python comm_og_service_tool.py --bulk NEO2 FlycParam set --alt near_gnd_vert_acc_limit_amp 10

# === 速度全开 ===
python comm_og_service_tool.py --bulk NEO2 FlycParam set --alt "ffg_speed_ctrl_perc|g_config.control.ffg_speed_ctrl_perc" 100
python comm_og_service_tool.py --bulk NEO2 FlycParam set --alt "sport_ffg_speed_ctrl_perc|g_config.control.sport_ffg_speed_ctrl_perc" 100
python comm_og_service_tool.py --bulk NEO2 FlycParam set --alt "vert_vel_down_adding|g_config.control.vert_vel_down_adding" 5
python comm_og_service_tool.py --bulk NEO2 FlycParam set --alt vert_vel_down_adding_max -20

# === 限制解除 ===
python comm_og_service_tool.py --bulk NEO2 FlycParam set --alt g_config.flying_limit.max_radius 8000
```

## 档位配置（mode 映射）

Neo 2 三档开关映射可用 `control_mode` 参数自定义。当前默认值：

```bash
# 读取当前档位配置
python comm_og_service_tool.py --bulk NEO2 FlycParam get --alt "fswitch_selection|g_config.control.control_mode[0]"  # 档位0(上)
python comm_og_service_tool.py --bulk NEO2 FlycParam get --alt "fswitch_selection_1|g_config.control.control_mode[1]"  # 档位1(中)
python comm_og_service_tool.py --bulk NEO2 FlycParam get --alt "fswitch_selection_2|g_config.control.control_mode[2]"  # 档位2(下)
```

| 档位 | 参数 | 默认 mode | 范围 |
|------|------|-----------|------|
| 上 | `control_mode[0]` | 12 | 0~21 |
| 中 | `control_mode[1]` | 8 | 0~21 |
| 下 | `control_mode[2]` | 7 | 0~21 |

常用 mode 编号推测：

| mode | 含义 |
|------|------|
| 0 | 纯手动（无自稳） |
| 1 | ATTI（姿态保持，无GPS） |
| 7 | Cine/平稳 |
| 8 | Sport/运动 |
| 12 | Normal/P-GPS |

> **注意：** Neo 2 没有每个档位独立的姿态/速度限制参数，只有档位专属的 FFG 前馈增益（`ffg_speed_ctrl_perc` 对应 Normal，`sport_ffg_speed_ctrl_perc` 对应 Sport，`trip_ffg_speed_ctrl_perc` 对应 Cine/Tripod）。如需更深档位自定义，需改固件（`dji_flyc_param_ed.py`）。

## 参数名格式说明

部分参数在固件中有 `短名|完整路径` 格式的命名，执行命令时**必须用完整名称**：

```bash
# ❌ 错误 — 短名找不到
python comm_og_service_tool.py --bulk NEO2 FlycParam set --alt ffg_speed_ctrl_perc 100

# ✅ 正确 — 完整名称（含 | 符，需加引号）
python comm_og_service_tool.py --bulk NEO2 FlycParam set --alt "ffg_speed_ctrl_perc|g_config.control.ffg_speed_ctrl_perc" 100
```

用 `list` 命令可以查看参数的实际完整名称：

```bash
python comm_og_service_tool.py --bulk NEO2 FlycParam list --start=0 --count=300 --fmt=2line | grep ffg
```

## 常见问题

### Q: `No backend available` / `No libusb backend found`

A: 确保安装依赖：
```bash
pip install --user pyusb libusb1
```
然后用 Zadig 安装 libusb-win32 驱动。

### Q: `Could not find any DJI BULK device`

A: 
1. 确保 Neo 2 已开机并 USB 连接
2. 检查 USB 线是否支持数据传输（不是纯充电线）
3. 重新运行 Zadig 安装 libusb-win32 驱动

### Q: `Parameter not found`

A: 使用 `--alt` 参数强制走 2017 协议（全表枚举）。

### Q: 想恢复 DJI Assistant 2 连接

A: Zadig → 选 WinUSB 驱动 → Replace Driver，或重装 DJI Assistant 2。

## 风险提示

- ⚠️ 关闭近地保护后，低空飞行无自动避障，注意碰撞
- ⚠️ 修改驱动可能导致 DJI Assistant 2 暂时不可用（可恢复）
- ✅ 只修改飞控参数，不刷固件，不会变砖
- ✅ 改回默认值即可完全恢复

## 致谢

- [o-gs/dji-firmware-tools](https://github.com/o-gs/dji-firmware-tools) — DJI 飞控逆向工程开源工具
- [MavicPilots 社区](https://mavicpilots.com/) — 参数名称验证
- [Zadig](https://zadig.akeo.ie/) — Windows USB 驱动管理工具
