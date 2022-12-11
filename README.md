![Example Bridge Banner Image](BannerExample.png?raw=true "Example Bridge Test")
<h1 align="center">Bridge Truss Solver</h1>
<h2 align="center">Built on Python</h2>
<h3>This truss-simulation includes:</h3>
<ul>
  <li>Tension and compression calculations for each member in a truss</li>
  <li>Support for one rolling and one fixed node</li>
  <li>Supports as many load forces as you want</li>
  <li>Only allows for completely vertical load vectors (wip)</li>
  <li>No units</li>
  <li>Visualize stress on individual members</li>
  <li>Visualize members in tension and compression</li>
</ul>

Four test bridges are provided that are ready to simulate.<br>
Open the <code>BridgeSim.py</code> file and change the name of the data you want to run.<br>

``` python
#Load Bridge Data
try:
    f = open('Bridges/TestBridgeData1.json') <--- #You can change the bridge here
except:
    raise Exception("No bridge data file could be found.")
else:
    bridgeData = json.load(f)
    f.close()
```

The project now supports **materials!** <br>
The general format for materials are as follows:<br>
``` json
{
    "Name": "Balsa",
    "CrossSectionalDimensions": [0.003175, 0.003175],
    "Density": 0.13,
    "CompressionStrength": 7,
    "TensileStrength": 14
}
```
Units: <br>
<ul>
    <li>Dimensions: meter x meter</li>
    <li>Density: grams per cubic centimeter</li>
    <li>Tensile & Compression Strength: Mega Pascal</li>
</ul>
The materials folder contains balsa wood you can experiment with for now. As of the current version, density is not used and will throw an error if not included in your material file. 
If you would like to add your own materials you can use the balsa wood as an example.<br>
You can change the material for the bridge:<br>

``` python
#Load Material Data
try:
    f = open('Materials/Balsa.json') <--- #You can change the material here
except:
    raise Exception("No material data file could be found.")
else:
    materialData = json.load(f)
    f.close()
```

While using a material you can visualize the general stress on each member.<br>
I am very new to Github and am learning the ropes. <3<br>
*If you have any questions about the project or wish to contact me, leave a comment somewhere. I might find it. Hopefully anyone who stumbles across this will find it useful.*
