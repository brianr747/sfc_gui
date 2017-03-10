# coding=utf-8
"""
install_examples.py

Dialogs that installs scripts to a desired directory. Simple front end to
sfc_models.examples.install_example_scripts

Migrated to sfc_models.examples


License/Disclaimer
------------------

Copyright 2017 Brian Romanchuk

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""
from __future__ import print_function

import sys
if sys.version_info[0] < 3:
    import Tkinter as tk
    from Tkinter import *
    import Tkinter.messagebox as mbox
    import Tkinter.filedialog as fdog
else:
    import tkinter as tk
    from tkinter import *
    import tkinter.messagebox as mbox
    import tkinter.filedialog as fdog

from sfc_models.examples import install_example_scripts

validate_str = """
This command will install sfc_models to a directory that you specify. It will also create a sub-directory named "output" (which is where log files are directed).

It will not overwrite existing files; it is recommended that you clear out your local copy of the examples directory before installing an updated examples set.
"""


def install_examples():
    """
    Pops up windows to allow the user to choose a directory for installation
    of sfc_models examples.

    Uses tkinter, which is installed in base Python (modern versions).
    :return:
    """
    if not mbox.askokcancel(title='sfc_models Example Installation',
                            message=validate_str):
        return
    target = fdog.askdirectory(title='Choose directory to for sfc_models examples installation')
    if target == () or target == '':
        return
    install_example_scripts.install(target)


if __name__ == '__main__':
    install_examples()
