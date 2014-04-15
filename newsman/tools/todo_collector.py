#!/usr/bin/env python
#-*- coding: utf-8 -*-

"""
todo_collector finds all lines with todo and adds them to readme
"""
# @author chengdujin
# @contact chengdujin@gmail.com
# @created Jul., 2013


import sys

reload(sys)
sys.setdefaultencoding('UTF-8')
sys.path.append('..')

import os
import re

# CONSTANTS
from config.settings import LOCAL

HOME = LOCAL % 'newsman/newsman'
OUTPUT = LOCAL % 'newsman/TODO.md'


def docs_output(docs, output):
    """
    output collected docs to the output file
    """
    if os.path.exists(output):
        f = open(output, 'r')
        lines = f.readlines()
        f.close()
        new_lines = []
        for line in lines:
            if 'ToDos - Generated from docs' in line:
                new_lines.append(line)
                new_lines.append('--------------------------\n')
                for path in docs:
                    new_lines.append('* `%s`\n' % path)
                    for index, method in enumerate(docs[path]):
                        method_line, method_docs = docs[path][method]
                        new_lines.append('    %i. Line %i: %s\n' %
                                         (index + 1, int(method_line), method))
                        for method_doc in method_docs:
                            new_lines.append('        - %s\n' % method_doc)
                    new_lines.append('\n')
                break
            else:
                new_lines.append(line)
        f = open(output, 'w')
        for new_line in new_lines:
            f.write(new_line)
        f.close()
    else:
        print '%s does not exist!' % output


def pattern_scrape(path, pattern):
    """
    find line number, def and todos in a method
    """
    f = open(path, 'r')
    lines = f.readlines()

    methods = {}
    todos = []
    for index, line in enumerate(lines):
        if line.startswith(pattern):
            todo = line.replace(pattern, '').strip()
            todos.append(todo)
        elif line.startswith('def '):
            if todos:
                method = re.split('\(', line)[0].lstrip('def ').strip()
                methods[method] = index + 1, todos
                todos = []
    return methods


def tree_digg(directory):
    """
    explore every subdirectory and files
    """
    if os.path.exists(directory):
        try:
            docs = {}
            subdirectories = os.listdir(directory)
            for subdirectory in subdirectories:
                if subdirectory == '.' or subdirectory == '..':
                    continue
                path = '%s/%s' % (directory, subdirectory)
                if os.path.isdir(path):
                    path_docs = tree_digg(path)
                    docs.update(path_docs)
                else:
                    if path.endswith('.py'):
                        methods = pattern_scrape(path, '# TODO: ')
                        if methods:
                            docs[path.replace('%s/' % HOME, '')] = methods
            return docs
        except OSError as k:
            print k
    else:
        print '%s does not exist!' % HOME


if __name__ == '__main__':
    docs = tree_digg(HOME)
    docs_output(docs, OUTPUT)
