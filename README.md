# DJI Neo 2 调参工具 🚁

基于 [o-gs/dji-firmware-tools](https://github.com/o-gs/dji-firmware-tools) 魔改，**专门为 DJI Neo / Neo 2 添加支持的飞控参数修改工具**。

## 能干什么

通过 USB 直连 DJI Neo 2，读写飞控隐藏参数，**不改固件不刷机，安全可恢复**。

| 功能 | 说明 |
|------|------|
| 🔓 关闭近地保护 | `avoid_ground_and_smart_landing_enable` = 0，贴地飞行不再自动抬升 |
| 🏎️ FPV 性能调参 | 改倾斜角、偏航速度、升降速度等 |
| 🔍 参数扫描 | 列出 Neo 2 所有可修改的飞控参数 |

## 快速开始

### 1. 装依赖

```bash
pip install --user pyusb pyserial libusb1
```

### 2. 装驱动（Windows）

用 [Zadig](https://zadig.akeo.ie/) 把 Neo 2 的 WinUSB 驱动换成 libusb-win32。5 分钟搞定。

### 3. 连 Neo 2，关近地保护

```bash
# 读当前值
python comm_og_service_tool.py --bulk NEO2 FlycParam get --alt \
  g_config.flying_limit.avoid_ground_and_smart_landing_enable

# 关闭（1→0）
python comm_og_service_tool.py --bulk NEO2 FlycParam set --alt \
  g_config.flying_limit.avoid_ground_and_smart_landing_enable 0
```

### 4. 搞定，去飞

详细教程见 **[USAGE.md](USAGE.md)**。

## 支持的机型

| 机型 | 命令 |
|------|------|
| DJI Neo（初代） | `NEO` |
| DJI Neo 2 | `NEO2` |
| 其他 DJI 机型 | 见[原项目](https://github.com/o-gs/dji-firmware-tools) |

## 原理

DJI 飞控有数百个隐藏参数，通过 DUML 协议可以在线读写。本工具就是 DUML 协议的命令行客户端。

```
USB 连 Neo 2 → DUML 协议 → 读飞控参数表 → 改 g_config.flying_limit.avoid_ground_and_smart_landing_enable → 写入
```

只改参数，不刷固件。断电重启值还在，改回 1 就恢复。

## 致谢

- [o-gs/dji-firmware-tools](https://github.com/o-gs/dji-firmware-tools) — DJI 飞控逆向工程开源项目
- [MavicPilots 社区](https://mavicpilots.com/) — 参数名验证
- [Zadig](https://zadig.akeo.ie/) — Windows USB 驱动管理

## 协议

GPL v3，跟原项目一致。详见 [LICENSE](LICENSE)。
