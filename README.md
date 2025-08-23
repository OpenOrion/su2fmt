<h1 align="center">🕸️ su2fmt</h1>

<p align="center">the open source SU2 mesh format parser and exporter</p>



# About
su2fmt parses and exports the SU2 mesh format in accordance with the spec here:
https://su2code.github.io/docs/Mesh-File/.


# Install
```
pip install git+https://github.com/OpenOrion/su2fmt.git#egg=su2fmt
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
#### Note: `visualize_mesh` has been moved to [ezmesh](https://github.com/OpenOrion/ezmesh)


# Devlopement Setup
```
git clone https://github.com/OpenOrion/su2fmt.git
cd su2fmt
pip install -r requirements_dev.txt
```
