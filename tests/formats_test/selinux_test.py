# pylint: disable=unused-import
import os
from unittest.mock import patch, ANY
import unittest
import selinux

import blivet
import blivet.formats.fs as fs


class SELinuxContextTestCase(unittest.TestCase):
    """Testing SELinux contexts.
    """

    def setUp(self):
        self.installer_mode = blivet.flags.installer_mode
        self.addCleanup(self._clean_up)

    def _clean_up(self):
        blivet.flags.installer_mode = self.installer_mode

    @patch("blivet.util.mount", return_value=0)
    @patch.object(fs.FS, "_pre_setup", return_value=True)
    @patch("os.access", return_value=True)
    # pylint: disable=unused-argument
    # pylint: disable=no-self-use
    def exec_mount_selinux_format(self, formt, *args):
        """ Test of correct selinux context parameter value when mounting """

        lost_found_context = "system_u:object_r:lost_found_t:s0"
        fmt = formt()

        # Patch selinux context setting
        with patch("selinux.lsetfilecon") as lsetfilecon:
            lsetfilecon.return_value = True

            blivet.flags.installer_mode = True
            fmt.setup(mountpoint="dummy")  # param needed to pass string check
            lsetfilecon.assert_called_with(ANY, lost_found_context)

            lsetfilecon.reset_mock()

            blivet.flags.installer_mode = False
            fmt.setup(mountpoint="dummy")  # param needed to pass string check
            lsetfilecon.assert_not_called()

    def test_mount_selinux_ext2fs(self):
        """ Test of correct selinux context parameter value when mounting ext2"""
        self.exec_mount_selinux_format(fs.Ext2FS)

    def test_mount_selinux_xfs(self):
        """ Test of correct selinux context parameter value when mounting XFS"""
        self.exec_mount_selinux_format(fs.XFS)
