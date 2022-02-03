#!/usr/bin/env python3

import sys
import json

import gr
import gr_data

# == Main ========================================================================

def main():
    while run_cmd(shift('Command')):
        pass

def run_cmd(cmd):
    if cmd is None:
        print('exit')
        return False
    if cmd == '':
        print('The command is empty')
    elif cmd in ['reset', 'ls', 'add', 'rem']:
        db = gr_data.FileDB("data.json")
        if cmd == 'reset':
            graph = gr.Graph(db)
            graph.reset()
            return True
        elif cmd == 'ls':
            data = gr.Graph(db)
            all_nodes = data.find()
            print(json.dumps(all_nodes, indent=4))
        elif cmd == 'add':
            data = gr.Graph(db)
            entry = json.loads(input())
            data.insert(entry)
        elif cmd == 'rem':
            pass
        else:
            pass
    elif cmd == 'exit':
        return False
    else:
        print('The command "{}" is unknown'.format(cmd))
    return True

def shift(what):
    if len(sys.argv) == 1:
        try:
            return input(what + ': ')
        except EOFError:
            return None
    res = sys.argv[1]
    sys.argv = [sys.argv[0]] + sys.argv[2:]
    return res

# == Main Initialization =========================================================

if __name__ == '__main__':
    main()