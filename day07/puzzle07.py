"""https://adventofcode.com/2022/day/7"""
from collections import defaultdict
from dataclasses import dataclass
import itertools
from enum import Enum
from pathlib import PurePosixPath
import re
from typing import Any, Iterator, Iterable

@dataclass
class ChangeDir:
    to_dir: str

@dataclass
class ListDir:
    pass

@dataclass
class DirEntry:
    dirname: str

@dataclass
class FileEntry:
    filename: str
    size: int

Token = ChangeDir | DirEntry | FileEntry

def tokenize_commands(lines: Iterable[str]) -> Iterator[Token]:
    """tokenizes into a list of tokens"""
    changedir_re = re.compile(r"^\$ cd\s+(?P<dir>\S+)")
    ls_re = re.compile(r"^\$ ls")
    dir_re = re.compile(r"^dir\s+(?P<dirname>\w+)")
    file_re = re.compile(r"(?P<size>\d+)\s+(?P<filename>\S+)")
    for line in lines:
        if m := changedir_re.match(line):
            yield ChangeDir(m.group("dir"))
        elif m := ls_re.match(line):
            yield ListDir()
        elif m := dir_re.match(line):
            yield DirEntry(m.group("dirname"))
        elif m := file_re.match(line):
            yield FileEntry(m.group("filename"), int(m.group("size")))
        else:
            raise ValueError(f"can't handle line `{line}`")

def parse_tokens(tokens: Iterable[Token]) -> dict[str, Any]:
    """parse the tokens into a nested dictionary"""
    cwd = PurePosixPath("/")
    dir_contents: dict[str, dict | int] = None
    dirs = defaultdict(dict)
    for token in tokens:
        match token:
            case ChangeDir(to_dir):
                if dir_contents:
                    cd = dirs
                    for p in cwd.parts:
                        new_cd = cd.get(p, {})
                        cd[p] = new_cd
                        cd = new_cd
                    cd.update({k: v for (k, v) in dir_contents.items() if k not in cd})
                    dir_contents = None
                if to_dir == "..":
                    cwd = cwd.parent
                else:
                    cwd /= to_dir
            case ListDir():
                dir_contents = {}
            case DirEntry(dirname):
                if dir_contents is None:
                    raise ValueError(f"got a dir entry outside of ListDir: {dirname}")
                dir_contents[dirname] = {}
            case FileEntry(filename, size):
                if dir_contents is None:
                    raise ValueError(f"got a file entry outside of ListDir: {filename}")
                dir_contents[filename] = size
            case _:
                raise ValueError(f"unknown token `{token}`")
    
    if dir_contents:
        cd = dirs
        for p in cwd.parts:
            new_cd = cd.get(p, {})
            cd[p] = new_cd
            cd = new_cd
        cd.update({k: v for (k, v) in dir_contents.items() if k not in cd})
        dir_contents = None
    return dirs

class CustPath:
    """yep"""
    # it's such a pain to write a subclass for Path that I'm gonna skip it
    @classmethod
    def from_logfile(cls, logfile: str | list[str]):
        if isinstance(logfile, str):
            logfile = logfile.splitlines()
        tokens = tokenize_commands(logfile)
        parsed = parse_tokens(tokens)['/']
        return cls(PurePosixPath("/"), parsed)
    def __init__(self, cwd: PurePosixPath, parsed: dict[str, Any]):
        self._dict = parsed
        self._cwd = cwd
    def _normalized(self) -> list[str]:
        keys = []
        # normalize path
        for part in self._cwd.parts[1:]:
            if part == "..":
                keys.pop()
            else:
                keys.append(part)
        return keys
    def _get_entry(self) -> dict[str, Any] | int:
        """fetches the entry for this path"""
        dirs = self._dict
        for k in self._normalized():
            dirs = dirs[k]
        return dirs
    def iterdir(self) -> Iterator['CustPath']:
        entry = self._get_entry()
        return (CustPath(self._cwd / k, self._dict) for k in entry.keys())
    def __truediv__(self, d: str) -> 'CustPath':
        return CustPath(self._cwd / d, self._dict)
    @property
    def parts(self) -> list[str]:
        return self._cwd.parts
    @property
    def parent(self) -> 'CustPath':
        return CustPath(self._cwd.parent, self._dict)
    @property
    def parents(self) -> list['CustPath']:
        return [CustPath(p, self._dict) for p in self._cwd.parents]
    @property
    def name(self) -> str:
        return self._cwd.name
    @property
    def suffix(self) -> str:
        return self._cwd.suffix
    @property
    def suffixes(self) -> list[str]:
        return self._cwd.suffixes
    @property
    def stem(self) -> str:
        return self._cwd.stem
    def joinpath(self, *other):
        return CustPath(self._cwd.joinpath(*other), self._dict)
    def match(self, pattern):
        return self._cwd.match(pattern)
    def with_name(self, name):
        return CustPath(self._cwd.with_name(name), self._dict)
    def with_stem(self, stem):
        return CustPath(self._cwd.with_stem(stem), self._dict)
    def with_suffix(self, suffix):
        return CustPath(self._cwd.with_stem(suffix), self._dict)
    def __repr__(self) -> str:
        parts = '/'.join(self.parts[1:])
        return f"CustPath(/{parts})"
    def exists(self) -> bool:
        try:
            self._get_entry()
            return True
        except KeyError:
            return False
    def is_file(self) -> bool:
        return isinstance(self._get_entry(), int)
    def is_dir(self) -> bool:
        return isinstance(self._get_entry(), dict)
    def size(self) -> int:
        if not self.is_file():
            return sum(p.size() for p in self.iterdir())
        return self._get_entry()

def dirs_smaller_than(fs: CustPath, size: int) -> list[CustPath]:
    smolbois = []
    children = list(fs.iterdir())
    while children:
        smol = (c for c in children if c.is_dir() and c.size() < size)
        smolbois.extend(smol)
        children = list(itertools.chain.from_iterable(ch.iterdir() for ch in children if ch.is_dir()))
    return smolbois

def iterdir_recursive(fs: CustPath) -> list[CustPath]:
    all_paths = [fs]
    children = [c for c in fs.iterdir()]
    while children:
        all_paths.extend(children)
        children = [ch for ch in children if ch.is_dir()]
        children = list(itertools.chain.from_iterable(ch.iterdir() for ch in children))
    return all_paths

if __name__ == '__main__':
    with open('input.txt') as fptr:
        input = fptr.read().splitlines()
    fs = CustPath.from_logfile(input)
    # part 1
    smolbois = dirs_smaller_than(fs, 100_000)
    total_size = sum(p.size() for p in smolbois)
    print(f"total of dirs smaller than 100_000: {total_size}")
    # part 2
    total = 70_000_000
    used = fs.size()
    free = total - used
    print(f"free space = {free} (need 30_000_000 free)")
    to_free = 30_000_000 - free
    if to_free < 0:
        raise ValueError("lol this isn't right")
    print(f"need to free additional {to_free}")
    # find all directories
    all_paths = iterdir_recursive(fs)
    all_dirs = [p for p in all_paths if p.is_dir()]
    all_dirs.sort(key=lambda d: d.size())
    large_enough_dirs = filter(lambda d: d.size() > to_free, all_dirs)
    dir_to_delete = next(large_enough_dirs)
    print(f"can delete {dir_to_delete} to free enough data, of size {dir_to_delete.size()}")