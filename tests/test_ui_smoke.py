"""Smoke test for the Directory GUI - verifies GUI can be created and destroyed without error.

Note: This test is a lightweight smoke check and should be run in an environment with a display.
"""
import tkinter as tk
from app import DirectoryGUI


def test_gui_smoke():
    root = tk.Tk()
    # avoid showing window during automated runs
    root.withdraw()
    app = DirectoryGUI(root)
    # check some basic attributes
    assert hasattr(app, 'tree')
    assert hasattr(app, 'username_entry')
    assert hasattr(app, 'phone_entry')
    # cleanup
    root.destroy()


if __name__ == '__main__':
    test_gui_smoke()
    print('GUI smoke test passed')
