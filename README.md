<div align="center">
<h1 align="center">Snap Tool</h1>

  <p align="center">
    Since FK/IK Rig is a very common but necessary setup, so is a tool that allows FK and IK controller
matching. Snap tool is an animation tool that match IK controller
to FK controller and vice versa.
    <br />
    <a href="https://youtu.be/t8vuaqPDf0g">Full Demo</a>
  </p>
</div>

## About The Project

<div align="left">
<img src="https://i.imgur.com/Jww19rH.png" alt="snap-tool" height="280px"/>
</div>

I've come across two methods to achieve FK/IK snapping/matching,
both methods relies on assessing the joint info, 
as controller is a layer on top of the joints and can be drastically
different across rig types.

- Constraint-based: used for easy setup
    - **FK to IK**: use joint position in FK mode to point constraint IK controllers
    - **IK to FK**: use joint rotation in IK mode to orient constraint FK controllers


- Vector math: used for generic setup
    - **FK to IK**: set IK handle and IK root based on joint position in FK mode; calculate
  mid-vector based on joint position in FK mode to set IK pole vector.
    - **IK to FK**: set FK controllers to joint rotations in IK mode

## Getting Started

1. Unzip the **snap-tool** package under
`%USERPROFILE%/Documents/maya/[current maya version]/scripts/`
or a custom directory under `PYTHONPATH` env variable. 

2. Rename the package to something like `snapTool`

3. Launch through script editor:
    ```python
    from snapTool import snapUI
    snapUI.show()
    ```

## Usage

### Step 1: Assign Joints

the tools take a snapshot of the current active
result joint, and record its transform information.

<img src="https://i.imgur.com/o0fjQGs.gif" alt="assign" width="75%" height="75%"/>

### Step 2: Assign Controllers

assign either FK controllers or IK controllers
for matching by selecting it.

### Step 3: Snap!

click 'snap' will force the transform matching to the joint snapshot

<img src="https://i.imgur.com/ZDFv0Oo.gif" alt="switch" width="75%" height="75%"/>

