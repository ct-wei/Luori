# FRPv6-Luori 🔍[[ICNP2024]](https://ieeexplore.ieee.org/document/10858548)
This repo contains the official implementation of  [**"Luori: Active Probing and Evaluation of Internet-wide IPv6 Fully Responsive Prefixes"**](https://frpv6.github.io)



</div>

<div align="center">

English | [简体中文](README_zh-CN.md)

</div>


## Quick Start
### Preparation
- Import the IP-ASN32-DAT file into the ```Luori/pyasn_data``` folder.(https://archive.routeviews.org/route-views6/bgpdata/)
- Import the seeded data into the ```Luori/routingprefix_dataset``` folder classified by routing prefix.
  
  To avoid folder symbol ```/``` ,please use ```_```.
  For exmaple, use the name of ```2a00:1c50:94::_48.txt```  instead of ```2a00:1c50:94::/48.txt``` as the name of txt file.

### Step1 : Make Pickle File
```bash
python3 pickle_maker.py
```

### Step2 : Set the config
Set the configuration in ```MCTS_Search/config.py```

Enter the active address escape trap threshold in ```trap_n```

Enter the scanning list filename in ```scanninglist```

Enter the FRP filename in ```fullrespond_path```

Enter the log filename in ```logpath```

Enter the generated filename in ```pickle_file```



### Step3 : Run Luori
- For Seeded Routing Prefix
```bash
python3 MCTS_Search/MCTS_seeded_controller.py
```

- For Unseeded Routing Prefix
```bash
python3 MCTS_Search/MCTS_unseeded_controller.py
```

## Acknowledgement


## Citation

If you find this paper useful in your research, please cite this paper.

```
@INPROCEEDINGS{cheng2024luori,
  author={Cheng, Daguo and He, Lin and Wei, Chentian and Yin, Qilei and Jin, Boran and Wang, Zhaoan and Pan, Xiaoteng and Zhou, Sixu and Liu, Ying and Zhang, Shenglin and Tan, Fuchao and Liu, Wenmao},
  booktitle={2024 IEEE 32nd International Conference on Network Protocols (ICNP)}, 
  title={Luori: Active Probing and Evaluation of Internet-Wide IPv6 Fully Responsive Prefixes}, 
  year={2024},
  volume={},
  number={},
  pages={1-12},
  keywords={Protocols;Current measurement;Reinforcement learning;Transforms;Routing;Optimization;IPv6;fully responsive prefix;active probing},
  doi={10.1109/ICNP61940.2024.10858548}}

```

## License

This project is released under the [Apache 2.0 license](LICENSE).
