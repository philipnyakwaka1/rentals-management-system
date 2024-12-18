#!/usr/bin/env python3
from uuid import uuid4

for i in range(50):
    s = str(uuid4())
    print(len(s))