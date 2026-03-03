#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Point d'entrée legacy — délègue à gentxt.main."""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gentxt.main import main  # noqa: E402

if __name__ == "__main__":
    main()