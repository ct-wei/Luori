
# FRPv6-Luori 🔍
这个仓库包含了 [**"Luori: Active Probing and Evaluation of Internet-wide IPv6 Fully Responsive Prefixes"**](https://frpv6.github.io) 的官方实现。

</div>

<div align="center">

[English](README.md) | 简体中文

</div>

## 快速开始
### 准备工作
- 将 ```IP-ASN32-DAT```文件导入到 ```Luori/pyasn_data``` 文件夹中。
- 将种子数据按照```路由前缀```分类导入到 ```Luori/routingprefix_dataset``` 文件夹中。
  
  为了避免文件夹符号 ```/``` ，请使用 ```_```。
  例如，使用 ```2a00:1c50:94::_48.txt``` 作为 txt 文件的名称，而不是 ```2a00:1c50:94::/48.txt```。

### 第1步：制作 Pickle 文件
```bash
python3 pickle_maker.py
```
### 第2步：设置配置

在 ```MCTS_Search/config.py``` 中设置配置

在 ```trap_n``` 中输入活跃地址跳出陷阱阈值

在 ```scanninglist``` 中输入扫描列表文件名

在 ```fullrespond_path``` 中输入FRP文件名

在 ```logpath``` 中输入日志文件名

在 ```pickle_file``` 中输入生成的文件名

### 第3步：运行 Luori
- 对于有种子的路由前缀
```bash
python3 MCTS_Search/MCTS_seeded_controller.py
```
- 对于无种子的路由前缀
```bash
python3 MCTS_Search/MCTS_unseeded_controller.py
```

## 致谢

## 引用
如果您在研究中发现这篇论文有用，请引用这篇论文。
```
@inproceedings{cheng2024luori,
  title = {Luori: Active Probing and Evaluation of Internet-wide IPv6 Fully Responsive Prefixes},
  author = {Cheng, Daguo and He, Lin and Wei, Chentian and Yin, Qilei and Jin, Boran and Wang, Zhaoan and Pan, Xiaoteng and Zhou, Sixu and Liu, Ying and Zhang, Shenglin and Tan, Fuchao and Liu, Wenmao},
  booktitle = {Proceedings of the 32nd IEEE International Conference on Network Protocols (ICNP)},
  year = {2024},
  pages = {},
  doi = {},
  address = {Charleroi, Belgium},
  date = {October 28-31},
}
```
## 许可证
这个项目是在 [Apache 2.0 许可证](LICENSE) 下发布的。
