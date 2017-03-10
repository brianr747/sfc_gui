# coding=utf-8sfc_gui: GUI For The SFC Models Package
=======================================

Introduction
------------

This package is expected to turn into a graphical interface for the *sfc_models* library. (This is
a library to construct and solve Stock-Flow Consistent models in Python.)

The GUI's that work properly may migrate to be embedded within *sfc_models*. As a result, this repository
may be abandoned and work will instead go into *sfc_models*. (In other words, this could have been a
branch.) However, I may want to draw a line between the robust model code, and this GUI code, which is
likely to be more fragile. Creating a new repository was the easiest way to make this distinction obvious.

The other downside of incorporation into *sfc_models* is that matplotlib would obviously be a requirement.
(Previously, only Quick2DPlot() failed without matplotlib, and it had a built-in handler. The GUI's will
largely be non-functional without it. (I have had a hard time getting matplotlib to install on the first
try on Windows, and so there is an argument that I draw a line between convenience GUI code (which needs matplotlib),
and the core library, which runs without it. Some users may want to run the library solely on the command
line, and view data in another package (like R), so they have no need to install matplotlib.

You Say "Spaghetti", I Say "Prototyping..."
-------------------------------------------

This package is currently prototype code, as I learn how to the use the tk library. The code is
messy, and the output may not look particularly great, and may crash. Basically, use at your own risk.

Pieces of code are based on various online examples. Attribution will be noted within the comments.
Since the code is likely to be completely rebuilt over time, there is no point in putting attributions
within the limited static documentation of the package (e.g., this file).

Documentation is otherwise non-existent; will only be implemented if the GUI elements are stable.

I have no idea how to run unit tests on GUI's; so there is currently no test suite.

GUI's Planned
-------------

- A file open GUI to allow users to choose where to install example code. (This may migrate to *sfc_models*,
  it has no dependence upon matplotlib.
- (Under construction). A time series plotter that just shows the final output. There may be a few variants.
- (Possible) A builder that takes a Model, and allows the user to step through the main() operations.
  This will allow them to trace the creation of equations (without going into the log file). This is
  cute functionality, aimed at more casual users. This might be built before Version 1.0.
- (Possible) An advanced builder that allows you to configure a model completely from the GUI. The model will
  be saved as a *.py* file in a standard format. We can hack needed code into the Python file during
  development, allowing us to have a functional GUI almost from the beginning. Unlikely to be incorporated
  into the Version 1.0 release of *sfc_models*.


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

