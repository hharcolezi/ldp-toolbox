## LDP Toolbox: Exploring Utility and Attackability Tradeoffs in Local Differential Privacy

[![PyPI version](https://badge.fury.io/py/ldp-toolbox.svg)](https://badge.fury.io/py/ldp-toolbox)
[![Python Versions](https://img.shields.io/pypi/pyversions/ldp-toolbox.svg)](https://pypi.org/project/ldp-toolbox/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://github.com/hharcolezi/ldp-toolbox/blob/main/LICENSE)
[![GitHub stars](https://img.shields.io/github/stars/hharcolezi/ldp-toolbox.svg)](https://github.com/hharcolezi/ldp-toolbox/stargazers)
[![GitHub issues](https://img.shields.io/github/issues/hharcolezi/ldp-toolbox.svg)](https://github.com/hharcolezi/ldp-toolbox/issues)
[![Downloads](https://pepy.tech/badge/ldp-toolbox)](https://pepy.tech/project/ldp-toolbox)

**LDP Toolbox** is a Python package for analyzing, comparing, and visualizing Local Differential Privacy (LDP) protocols and their trade-offs between utility, privacy, and attackability.

This toolbox provides:
- 📊 Interactive dashboards powered by [Dash](https://dash.plotly.com/)
- ⚙️ Protocol implementations for frequency estimation tasks
- 🗂️ Visual tools to compare utility loss (e.g., MSE, KL-divergence), attackability, and privacy budget ε
- 📈 Upload your own data to explore privacy-utility trade-offs

----

## 📜 Citation
If you use this toolbox or our work in your research, please cite our paper: **Haoying Zhang, Abhishek K. Mishra, and Héber H. Arcolezi. 2025. "Demo: Exploring Utility and Attackability Trade-offs in Local Differential Privacy". In Proceedings of the 2025 ACM SIGSAC Conference on Computer and Communications Security (CCS '25). Association for Computing Machinery, New York, NY, USA, 4728–4730. https://doi.org/10.1145/3719027.3760706**

```bash
@inproceedings{Zhang2025,
author = {Zhang, Haoying and Mishra, Abhishek K. and Arcolezi, H\'{e}ber H.},
title = {Demo: Exploring Utility and Attackability Trade-offs in Local Differential Privacy},
year = {2025},
isbn = {9798400715259},
publisher = {Association for Computing Machinery},
address = {New York, NY, USA},
url = {https://doi.org/10.1145/3719027.3760706},
doi = {10.1145/3719027.3760706},
booktitle = {Proceedings of the 2025 ACM SIGSAC Conference on Computer and Communications Security},
pages = {4728–4730},
numpages = {3},
keywords = {local differential privacy, open source., privacy-utility trade-off},
location = {Taipei, Taiwan},
series = {CCS '25}
}
```

## 🚀 Installation

LDP Toolbox is available on PyPI. Install it with:

```bash
pip install ldp-toolbox
```

## ⚡ Usage

After installation, you can launch the dashboard in two ways:

### ✅ Option 1 — Using the CLI (recommended)

Run directly from the terminal:

```bash
ldp-toolbox
```

### ✅ Option 2 — Using Python module

Alternatively, you can run it as a module:

```bash
python -m ldp_toolbox.toolbox.app
```

Or if you prefer, you can embed the app in your own code:

```python
from ldp_toolbox.toolbox.app import app

if __name__ == "__main__":
    app.run(debug=True)
```

## 📁 Project Structure

- `ldp_toolbox/`
  - `protocols/` — Core LDP protocol implementations
  - `toolbox/` — Dash front-end app (`assets/`, `pages/`, `app.py`)

Example datasets (`data/`) are provided in this repository for demonstration and local testing, but are not shipped with the PyPI package.

### 🎥 Demonstration video

A recorded demonstration video is available at: [Demo](https://youtu.be/LC2NreobdzI)

## 🤝 Contributing
LDP-Toolbox is a work in progress, and we expect to release new versions frequently, incorporating feedback and code contributions from the community.

1. Fork this repo.
2. Create a feature branch.
3. Submit a pull request.

## 📬 Contact Authors
- [Haoying Zhang](https://haoyingzhang.github.io/)
- [Abhishek K. Mishra](https://miishra.github.io/)
- [Héber H. Arcolezi](https://hharcolezi.github.io/)

## 📝 License
This project is licensed under the [MIT License](https://github.com/hharcolezi/ldp-toolbox/blob/main/LICENSE).
