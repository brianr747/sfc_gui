"""

License/Disclaimer
------------------

Copyright 2016 Brian Romanchuk

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

import copy


def sort_series(serlist):
    """
    Sort a list of series names alphabetically, except for 'k' and 't' (at the front).

    Works on a copy, and returns it. (Not an in-place sort.)

    This should be moved to sfc_models, since the same code appears there.

    :param serlist: list
    :return:
    """
    new_serlist = copy.copy(serlist)
    new_serlist.sort()
    if 't' in new_serlist:
        new_serlist.remove('t')
        new_serlist.insert(0, 't')
    if 'k' in new_serlist:
        new_serlist.remove('k')
        new_serlist.insert(0,'k')
    return new_serlist