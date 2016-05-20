import os
import sys
import types
import unittest

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), '../armada_backend'))


class UnitTests(unittest.TestCase):
    def test_backend_scripts_are_parsing(self):
        import armada_backend.armada_api
        self.assertIsInstance(armada_backend.armada_api.main, types.FunctionType)
        import cleaner
        self.assertIsInstance(cleaner.main, types.FunctionType)
        import hermes_init
        self.assertIsInstance(hermes_init.main, types.FunctionType)
        import recover_saved_containers
        self.assertIsInstance(recover_saved_containers.main, types.FunctionType)
        import run_consul
        self.assertIsInstance(run_consul.main, types.FunctionType)
        import runtime_settings
        self.assertIsInstance(runtime_settings.main, types.FunctionType)
        import save_running_containers
        self.assertIsInstance(save_running_containers.main, types.FunctionType)

    def test_initialize_backend_classes(self):
        from api_base import ApiCommand
        ApiCommand()
        from api_create import Create
        Create()
        from api_images import GetInfo
        GetInfo()
        from api_info import GetEnv
        GetEnv()
        from api_info import GetVersion
        GetVersion()
        from api_list import List
        List()
        from api_recover import Recover
        Recover()
        from api_restart import Restart
        Restart()
        from api_run import Run
        Run()
        from api_run_hermes import Volumes
        Volumes()
        from api_ship import Name, Join, Promote, Shutdown
        Name()
        Join()
        Promote()
        Shutdown()
        from api_ssh import Address
        Address()
        from api_ssh import HermesAddress
        HermesAddress()
        from api_start import Start
        Start()
        from api_stop import Stop
        Stop()
        from armada_backend.armada_api import Health
        Health()


if __name__ == '__main__':
    unittest.main()
