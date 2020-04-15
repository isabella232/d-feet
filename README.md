# Welcome to [D-Feet](https://wiki.gnome.org/Apps/DFeet)

Requirements:

 - python >= 2.7
 - python-gi >= 3.3.91
 - gtk >= 3.6

Optional Requirements:

 - gnome-python-libwnck - for displaying application icons next to the application

To run localy for testing, install it using the prefix option:

    meson --prefix=/tmp/d-feet _build && ninja -C _build install

And then execute it:

    /tmp/d-feet/bin/d-feet

To install in the system:

    meson _build && ninja -C _build install
