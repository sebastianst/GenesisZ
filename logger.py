# Copyright (C) 2016-2018 Sebastian Stammler
#
# This file is part of GenesisZ.
# logger.py - helper methods for log output
#
# It is subject to the license terms in the LICENSE file found in the top-level
# directory of this distribution.
#
# No part of GenesisZ, including this file, may be copied, modified,
# propagated, or distributed except according to the terms contained in the
# LICENSE file.

import sys

verbose = False

def warn(msg):
    sys.stderr.write(msg + '\n')

def fatal(msg):
    sys.stderr.write(msg + '\n')
    sys.exit(1)

def verb(msg):
    if verbose:
        # sys.stderr.write(msg + '\n')
        print(msg)
