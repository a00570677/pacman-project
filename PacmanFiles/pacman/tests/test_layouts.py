import os

import pytest

from pacman import layouts

layout_names = []
for filename in os.listdir(layouts.LAYOUT_DIR):
    name, ext = os.path.splitext(filename)
    if ext == layouts.LAYOUT_SUFFIX:
        layout_names.append(name)


@pytest.mark.parametrize('layout_name', layout_names)
def test_loading_all_layouts(layout_name):
    layouts.load_layout(layout_name)
