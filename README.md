<h1 align="center">Bridge Truss Solver</h1>
<h2 align="center">Built on Python</h2>
<h3>This truss-simulation includes:</h3>
<ul>
  <li>Tension and compression calculations for each member in a truss</li>
  <li>Support for one rolling and one fixed node</li>
  <li>Supports as many load forces as you want</li>
  <li>Only allows for completely vertical load vectors (wip)</li>
  <li>No units</li>
</ul>

Three test bridges are provided that are ready to simulate.<br>
Open the <code>BridgeSim.py</code> file and change the name of the data you want to run.<br>

``` python
#Load Bridge Data
try:
    f = open('TestBridgeData1.json') <--- #You can change to test data 1,2, or 3
except:
    raise Exception("No bridge data file could be found.")
else:
    data = json.load(f)
    f.close()
```

I am very new to Github and am learning the ropes. <br>
*If you have any questions about the project or wish to contact me, I will not know where to find you. Hopefully anyone who stumbles across this will find it useful.*
