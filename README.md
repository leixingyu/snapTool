## Snap Tool

An animation tool that allows you to snap or match IK controller
to FK controller and vice versa. 

### Launch

```python
from snapTool import snap
snap.show()
```

### Step 1: 

**Assign Joints**: the tools take a snapshot of the current active
result joint, and record its transform information.

![assign](https://i.imgur.com/o0fjQGs.gif)

### Step 2: 

**Assign Controllers**: assign either FK controllers or IK controllers
for matching by selecting it.

### Step 3: 

**Snap!**: click snap will force the transform matching to the joint snapshot

![switch](https://i.imgur.com/ZDFv0Oo.gif)
