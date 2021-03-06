import pathlib
import pynwb
from pynwb import NWBHDF5IO
import warnings
import os
from datajoint.settings import config as _config
from datajoint.attribute_adapter import AttributeAdapter
from .meta import pkg_name as _pkg_name

warnings.filterwarnings('ignore')
os.environ['DJ_SUPPORT_FILEPATH_MANAGEMENT'] = "TRUE"

# This NWB Adapter plugin makes use of the `filepath` feature in DataJoint
# Thus requiring the end-user to setup a store as part of their `dj.config['stores']`
# And also to specify to this plugin the store name to be used, in:
# dj.config['plugin_params'][pkg_name]['store_name']
# where "pkg_name" is the name of this plugin package upon installation

try:
    _store_name = _config['plugin_kwargs'][_pkg_name]['store_name']
except KeyError as e:
    raise KeyError(f"Store name not found for NWB adapter plugin: {str(e)}. Expecting: dj.config['plugin_kwargs'][pkg_name]['store_name']")

_exported_nwb_dir = _config['stores'][_store_name]['stage']

_nwb_session_dir = pathlib.Path(_exported_nwb_dir, 'session')
_nwb_mp_dir = pathlib.Path(_exported_nwb_dir, 'membrane_potential')

_nwb_session_dir.mkdir(parents=True, exist_ok=True)
_nwb_mp_dir.mkdir(parents=True, exist_ok=True)


class _NWBFile(AttributeAdapter):
    """ Adapter for: pynwb.file.NWBFile"""
    attribute_type = 'filepath@nwb_store'

    def put(self, nwb):
        save_file_name = ''.join([nwb.identifier, '.nwb'])
        save_fp = _nwb_session_dir / save_file_name

        print(f'Write NWBFile: {save_file_name}')
        _write_nwb(save_fp, nwb)
        return save_fp.as_posix()

    def get(self, path):
        io = NWBHDF5IO(str(pathlib.Path(path)), mode='r')
        nwb = io.read()
        nwb.io = io
        return nwb


class _Device(AttributeAdapter):
    """ Adapter for: pynwb.device.Device"""
    attribute_type = 'longblob'

    def put(self, nwb_device):
        return {'name': nwb_device.name}

    def get(self, device_dict):
        return pynwb.device.Device(name=device_dict['name'])


class _IntracellularElectrode(AttributeAdapter):
    """ Adapter for: pynwb.icephys.IntracellularElectrode"""
    attribute_type = 'longblob'

    def put(self, electrode):
        return dict(name=electrode.name, device=Device().put(electrode.device),
                    description=electrode.description, filtering=electrode.filtering,
                    location=electrode.location)

    def get(self, ic_electrode_dict):
        return pynwb.icephys.IntracellularElectrode(
            name=ic_electrode_dict['name'],
            device=Device().get(ic_electrode_dict['device']),
            description=ic_electrode_dict['description'],
            filtering=ic_electrode_dict['filtering'],
            location=ic_electrode_dict['location'])


class _PatchClampSeries(AttributeAdapter):
    """ Adapter for: pynwb.icephys.PatchClampSeries"""
    attribute_type = 'filepath@nwb_store'

    def put(self, patch_clamp):
        nwb = patch_clamp.parent

        nwb.add_device(patch_clamp.electrode.device)
        nwb.add_ic_electrode(patch_clamp.electrode)
        nwb.add_acquisition(patch_clamp)

        save_file_name = ''.join([nwb.identifier + '_{}'.format(patch_clamp.name), '.nwb'])
        save_fp = _nwb_mp_dir / save_file_name

        print(f'Write PatchClampSeries: {save_file_name}')
        _write_nwb(save_fp, nwb, manager=nwb.io.manager)
        return save_fp.as_posix()

    def get(self, path):
        io = NWBHDF5IO(str(pathlib.Path(path)), mode='r')
        nwb = io.read()
        patch_clamp = [obj for obj in nwb.objects.values()
                       if obj.neurodata_type == 'PatchClampSeries'][0]
        patch_clamp.io = io
        return patch_clamp


# ============= HELPER FUNCTIONS ===============

def _write_nwb(save_fp, nwb2write, manager=None):
    try:
        with NWBHDF5IO(save_fp.as_posix(), mode='w', manager=manager) as io:
            io.write(nwb2write)
    except Exception as e:
        if save_fp.exists():
            save_fp.unlink()
        raise e


# ==== instantiate dj.AttributeAdapter objects ====

nwbfile = _NWBFile()
device = _Device()
patch_clamp_series = _PatchClampSeries()
ic_electrode = _IntracellularElectrode()
