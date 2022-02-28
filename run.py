#!/usr/bin/env python3

import sys
import json

import gr
import gr_data
import gr_types

# == Main ========================================================================

def main():
    db_file = shift('Graph Database File')
    if db_file is not None:
        while run_cmd(db_file, shift('Command')):
            pass

def run_cmd(db_file, cmd):
    if cmd is None:
        print('exit')
        return False
    if cmd == '':
        print('The command is empty')
    elif cmd in ['clear', 'ls', 'add', 'rem']:
        db = gr_data.FileDB(db_file)
        if cmd == 'clear':
            graph = gr.Graph(db)
            graph.clear()
            gr_types.init_attribute_id_system(graph)
            gr_types.init_type_system(graph)
            gr_types.init_link_sysem(graph)
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
