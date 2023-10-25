#! /user/bin/env python3

import frame
import buffers
import sys
import os

buffWtr = buffers.BufferedFdWriter(1)
message = "Hello World".encode()
for byte in message:
    buffWtr.writeByte(byte)
buffWtr.flush()
