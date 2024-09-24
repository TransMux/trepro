import unittest
from unittest.mock import patch
from pathlib import Path
import os
import matplotlib.pyplot as plt
from trepro.matplotlib import (
    patch_savefig,
    load_saved_figure,
    separator_start,
    separator_end,
)


class TestSavefig(unittest.TestCase):
    def setUp(self):
        """Set up the test environment."""
        patch_savefig()  # Patch the savefig function
        self.test_file = "test.png"
        self.fig, self.ax = plt.subplots()
        self.ax.plot([1, 2, 3], [4, 5, 6])

    def tearDown(self):
        """Clean up the test environment."""
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    @patch("trepro.savefig._get_git_info")
    def test_savefig_with_metadata(self, mock_get_git_info):
        """Test saving a figure with metadata."""
        mock_get_git_info.return_value = {
            "git-hash": "dummy-hash",
            "git-date": "dummy-date",
            "git-author": "dummy-author",
            "cwd": "dummy-cwd",
            "os": "dummy-os",
            "git-remote": "dummy-remote",
        }

        self.fig.savefig(self.test_file)

        # Check if the file is created
        self.assertTrue(Path(self.test_file).exists())

        # Check if metadata is saved
        with open(self.test_file, "rb") as f:
            data = f.read()
            self.assertIn(separator_start, data)
            self.assertIn(separator_end, data)

    def test_load_saved_figure(self):
        """Test loading a saved figure with metadata."""
        self.fig.savefig(self.test_file)

        # Load the figure and metadata
        loaded_fig, metadata = load_saved_figure(self.test_file)

        # Check if the figure is loaded correctly
        self.assertIsInstance(loaded_fig, plt.Figure)

        # Check if metadata is loaded correctly
        self.assertIn("save_version", metadata)
        self.assertIn("matplotlib_version", metadata)

    def test_load_nonexistent_file(self):
        """Test loading a nonexistent file."""
        with self.assertRaises(FileNotFoundError):
            load_saved_figure("nonexistent.png")

    def test_load_invalid_file(self):
        """Test loading an invalid file."""
        with open(self.test_file, "wb") as f:
            f.write(b"Invalid content")

        with self.assertRaises(ValueError):
            load_saved_figure(self.test_file)


if __name__ == "__main__":
    unittest.main()
