# Copyright (C) 2016-2018 Sebastian Stammler
#
# This file is part of GenesisZ.
# solvers.py - classes to run the solvers (currently silentarmy and tromp)
#
# It is subject to the license terms in the LICENSE file found in the top-level
# directory of this distribution.
#
# No part of GenesisZ, including this file, may be copied, modified,
# propagated, or distributed except according to the terms contained in the
# LICENSE file.

from abc import ABCMeta, abstractmethod
import asyncio, re

from bitcoin.core import x, b2x, b2lx
from bitcoin.core.serialize import uint256_from_str
from zcash.core import GetSolutionSize, IsValidSolution, IncrementNonce

from logger import warn, fatal, verb

def stri(b):
    return b.decode('ascii').rstrip()

class Solver(metaclass=ABCMeta):
    def __init__(self, path, header, rounds=1, start_nonce=32*b'\x00', threads=1):
        self.path = path
        self.header = header
        self.start_nonce = start_nonce
        self.rounds = rounds
        self.threads = threads

        self.cmdline = self.build_cmdline()

    async def run(self):
        verb('Starting solver with command {}'.format(self.cmdline))
        create = asyncio.create_subprocess_exec(
                *self.cmdline,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.STDOUT)
        try:
            self.solver = await create
            verb('Solver started.')
        except FileNotFoundError as e:
            raise SolverException("Could not find binary {}; is the path correct?".format(self.cmdline[0]))
        except Exception as e:
            raise SolverException("Failed to execute '{}': {}".format(self.cmdline, e))

        self.banner = await self.eat_banner()
        verb('Banner:\n' + self.banner)

        try:
            while True:
                nonce, sols = await self.parse_solutions()
                verb('Solver returned {:d} solutions for nonce {}'
                        .format(len(sols), b2lx(nonce)))
                for sol in sols:
                    if IsValidSolution(self.header, nonce, sol):
                        return (sol, nonce)
        finally:
            self.solver.terminate()
            await self.solver.communicate() # .wait() would deadlock if pipe is full

    @abstractmethod
    def build_cmdline(self): pass
    """Should assemble all parameters set in __init__ to the command line to
    start the solver with, stored as a string list, and return it."""

    @abstractmethod
    async def eat_banner(self): pass
    """Should read from self.solver.stdout until the last line before content
    appears that parse_solution understands. Should return the banner as a
    single string."""

    @abstractmethod
    async def parse_solutions(self): pass
    """"Should parse self.solver.stdout for solutions and return the current
    nonce and list of solutions (as byte strings) when all solutions for this
    nonce have been printed."""

class SolverException(Exception):
    pass

class SilentarmySolver(Solver):
    def build_cmdline(self):
        return self.path + ['--nonces', str(self.rounds),
                '-i', b2x(self.header.serialize())]

    async def eat_banner(self):
        # consume banner input until solutions pop up
        banner = []
        async for line in self.solver.stdout:
            banner.append(stri(line))
            # Last line before solutions pop up in sa-solver
            if line.startswith(b'Running'):
                break
        return '\n'.join(banner)

    async def parse_solutions(self):
        sols, sol_size = [], GetSolutionSize()
        async for line in self.solver.stdout:
            line = stri(line)
            if line.startswith('Nonce'):
                break
            if line.startswith('Total'):
                raise SolverException('Solver stopped before valid solution found.')
            if len(line) != sol_size*2:
                raise SolverException("Solver returned unexpected solution of size != {:d}:\n{}"
                        .format(sol_size, line))
            sols.append(x(line))
        _, nonce, solc, _ = line.split()
        nonce = x(nonce[:-1]) # TODO or lx?

        return (nonce, sols)

class TrompSolver(Solver):
    def build_cmdline(self):
        return self.path + ['-s', '-c',
                '-n', str(uint256_from_str(self.start_nonce)),
                '-r', str(self.rounds),
                '-t', str(self.threads),
                '-x', b2x(self.header.serialize())]

    async def eat_banner(self):
        banner = []
        async for line in self.solver.stdout:
            banner.append(stri(line))
            # Last line before solutions pop up in tromp solver
            if stri(line).startswith('Using'):
                break
        # need to count nonce for tromp as it is not part of output
        self.nonce = self.start_nonce
        return '\n'.join(banner)

    async def parse_solutions(self):
        sols, sol_size, nonce = [], GetSolutionSize(), self.nonce
        async for line in self.solver.stdout:
            line = stri(line)
            if re.match(r'Digit \d+', line):
                continue
            if re.match(r'\d+ solutions', line): # last line
                # increment nonce for next round
                self.nonce = IncrementNonce(self.nonce)
                break
            if re.match(r'\d+ total solutions', line):
                raise SolverException('Solver stopped before valid solution found.')
            if not line.startswith('Solution'):
                raise SolverException('Unexpected solver output:\n' + line)
            line = line.split()[1]
            if len(line) != sol_size*2:
                raise SolverException("Solver returned unexpected solution of size != {:d}:\n{}"
                        .format(sol_size, line))
            sols.append(x(line))

        return (nonce, sols)
