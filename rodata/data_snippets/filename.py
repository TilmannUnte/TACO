# Copyright (c) 2025-2026 Tilmann Unte, Antonia Geßwein
# SPDX-License-Identifier:  Apache-2.0

import os

for filename in os.listdir("."):
    if filename.endswith(".c"):
        name = os.path.splitext(filename)[0]

        with open(filename, "a", encoding="utf-8") as f:
            f.write(f'\nconst char file_name[] = "{name}";\n')

        print(f"Updated: {filename}")
