## LDP Toolbox: Exploring Utility and Attackability Tradeoffs in Local Differential Privacy

[![PyPI version](https://badge.fury.io/py/ldp-toolbox.svg)](https://badge.fury.io/py/ldp-toolbox)

**LDP Toolbox** is a Python package for analyzing, comparing, and visualizing Local Differential Privacy (LDP) protocols and their trade-offs between utility, privacy, and attackability.

This toolbox provides:
- 📊 Interactive dashboards powered by [Dash](https://dash.plotly.com/)
- ⚙️ Protocol implementations for frequency estimation tasks
- 🗂️ Visual tools to compare utility loss (e.g., MSE, KL-divergence), attackability, and privacy budget ε
- 📈 Upload your own data to explore privacy-utility trade-offs

---

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

---

## 📬 Contact Authors:
- [Haoying Zhang](https://www.linkedin.com/in/haoying-zhang-2a6aa1176/): haoying.zhang [at] inria [dot] fr
- [Abhishek K. Mishra](https://miishra.github.io/): abhishek.mishra [at] inria [dot] fr
- [Héber H. Arcolezi](https://hharcolezi.github.io/): heber.hwang-arcolezi [at] inria [dot] fr


## 📝 License
This project is licensed under the [MIT License](https://github.com/hharcolezi/ldp-toolbox/blob/main/LICENSE).
