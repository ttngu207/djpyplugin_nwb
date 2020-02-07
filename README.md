# djpyplugin_nwb
NWB attribute adapter plugin for DataJoint

## This plugin defines 4 data types:

+ ***nwbfile*** - type `filepath@store` - models `pynwb.file.NWBFile`
+ ***device*** - type `longblob` - models `pynwb.device.Device`
+ ***ic_electrode*** - type `longblob` - models `pynwb.icephys.IntracellularElectrode`
+ ***patch_clamp_series*** - type `filepath@store` - models `pynwb.icephys.PatchClampSeries`

## Setup
The NWB types make use of DataJoint feature `filepath`, thus users are required to
1. setup ***store*** in the `dj.config['stores']`
2. specify the store name in the `plugin_kwargs` portion of the config, i.e.:
>"plugin_kwargs": {"dj_nwb_adapter": {"store_name": "nwb_store"}

#### An example config:
```json
"plugin": {
    "attribute_adapter": ["dj_nwb_adapter"]
},
"plugin_kwargs": {
    "dj_nwb_adapter": {"store_name": "nwb_store"}
},
"stores": {
    "nwb_store": {
        "protocol": "file",
        "location": "/path/nwb_dir",
        "stage": "/path/nwb_dir"
    }
},
```

## Usage
Install this plugin:
>pip install git+https://github.com/ttngu207/djpyplugin_nwb.git

Import datajoint and use these nwb type in table definition, e.g.:

```python
schema = dj.schema('test')

@schema
class Session(dj.Manual):
    definition = """
    session_id: int
    ---
    nwb_file: <dj_nwb_adapter.nwb.nwbfile>
    """
    
@schema
class MembranePotential(dj.Manual):
    definition = """
    -> Session
    ---
    patch_clamp_series: <dj_nwb_adapter.nwb.patch_clamp_series>
    """
```

Note: make sure to set the environment variable `DJ_SUPPORT_ADAPTED_TYPES` to `True` 

## Known Issues
1. Silently failed when using `dj.create_virtual_module()` without enabling `DJ_SUPPORT_ADAPTED_TYPES`
```python
import datajoint as dj
schema = dj.create_virtual_module('schema', 'test')
```

`schema.Session()` returns None