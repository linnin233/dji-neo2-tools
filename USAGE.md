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

## FPV 性能调参推荐

除了关闭近地保护，以下参数可提升 FPV 飞行体验：

| 参数 | 默认 | 推荐 | 说明 |
|------|------|------|------|
| `fpv_mode_tilt_range` | 65 | 85 | 更大倾斜角度 |
| `fpv_mode_yaw_gyro_range` | 55 | 99 | 更快偏航响应 |
| `fpv_vert_vel_down` | -6 | -10 | 更快垂直下降 |
| `fpv_vert_vel_up` | 8 | 10 | 更快垂直上升 |

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
