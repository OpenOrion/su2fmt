<h1 align="center">🕸️ su2fmt</h1>

<p align="center">the open source SU2 mesh format parser and exporter</p>

<p align="center">
    <a href="https://discord.gg/H7qRauGkQ6">
        <img src="https://img.shields.io/discord/913193916885524552?logo=discord"
            alt="chat on Discord">
    </a>
    <a href="https://www.patreon.com/turbodesigner">
        <img src="https://img.shields.io/badge/dynamic/json?color=%23e85b46&label=Patreon&query=data.attributes.patron_count&suffix=%20patrons&url=https%3A%2F%2Fwww.patreon.com%2Fapi%2Fcampaigns%2F9860430"
            alt="donate to Patreon">
    </a>
</p>



# About
su2fmt parses and exports the SU2 mesh format in accordance with the spec here:
https://su2code.github.io/docs/Mesh-File/.


# Install
```
pip install git+https://github.com/Turbodesigner/su2fmt.git#egg=su2fmt
```

# Example
See more examples in the [examples](/examples) directory

```python
from su2fmt import parse_mesh, export_mesh

# parses mesh file
mesh = parse_mesh("example.su2")

# export mesh file
export_mesh(mesh, "example_generated.su2")
```
#### Note: `visualize_mesh` has been moved to [ezmesh](https://github.com/Turbodesigner/ezmesh)


# Devlopement Setup
```
git clone https://github.com/Turbodesigner/su2fmt.git
cd su2fmt
pip install -r requirements_dev.txt
```
