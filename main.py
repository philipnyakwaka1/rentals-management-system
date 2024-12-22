#!/usr/bin/env python3
from dotenv import load_dotenv
import os
load_dotenv()
DB_ENGINE=os.getenv('DB_ENGINE')
print(DB_ENGINE)
print(type(DB_ENGINE))