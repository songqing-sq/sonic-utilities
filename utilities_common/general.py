import importlib.machinery
import importlib.util
import os
import sys

from sonic_py_common import multi_asic
from swsscommon import swsscommon
FEATURE_TABLE = "FEATURE"
FEATURE_HAS_PER_ASIC_SCOPE = 'has_per_asic_scope'
FEATURE_HAS_GLOBAL_SCOPE = 'has_global_scope'

def load_module_from_source(module_name, file_path):
    """
    This function will load the Python source file specified by <file_path>
    as a module named <module_name> and return an instance of the module
    """
    # Callers pass installed absolute paths (e.g. /usr/local/bin/sonic-cfggen).
    # Under a test harness that stages those scripts elsewhere, SONIC_BIN_DIR
    # names the directory holding them. Only consulted when the original path
    # is missing, so an installed system behaves exactly as before.
    if not os.path.exists(file_path):
        bin_dir = os.environ.get('SONIC_BIN_DIR')
        if bin_dir:
            staged = os.path.join(bin_dir, os.path.basename(file_path))
            if os.path.exists(staged):
                file_path = staged

    loader = importlib.machinery.SourceFileLoader(module_name, file_path)
    spec = importlib.util.spec_from_loader(loader.name, loader)
    module = importlib.util.module_from_spec(spec)
    loader.exec_module(module)

    sys.modules[module_name] = module

    return module

def load_db_config():
    '''
    Load the correct database config file:
     - database_global.json for multi asic
     - database_config.json for single asic
    '''
    if multi_asic.is_multi_asic():
        if not swsscommon.SonicDBConfig.isGlobalInit():
            swsscommon.SonicDBConfig.load_sonic_global_db_config()
    else:
        if not swsscommon.SonicDBConfig.isInit():
            swsscommon.SonicDBConfig.load_sonic_db_config()

def get_optional_value_for_key_in_config_tbl(config_db, port, key, table):
    info_dict = {}
    info_dict = config_db.get_entry(table, port)
    if info_dict is None:
        return None

    value = info_dict.get(key, None)
    return value


def get_feature_state_data(config_db, feature):
    '''
    Get feature state from FEATURE table from CONFIG_DB.
    return  global_scope, per_asic_scope
    - if feature state is disabled, return "False" for both global_scope and per_asic_scope
    - if is not a multi-asic, return feature state for global_scope ("True/False") and
      "False" for asic_scope
    '''
    global_scope = "False"
    asic_scope = "False"
    info_dict = {}
    info_dict = config_db.get_entry(FEATURE_TABLE, feature)
    if info_dict is None:
        return global_scope, asic_scope
    if multi_asic.is_multi_asic():
        if info_dict['state'].lower() == "enabled":
            global_scope = info_dict[FEATURE_HAS_GLOBAL_SCOPE]
            asic_scope = info_dict[FEATURE_HAS_PER_ASIC_SCOPE]
    else:
        if info_dict['state'].lower() == "enabled":
            global_scope = "True"
    return global_scope, asic_scope
