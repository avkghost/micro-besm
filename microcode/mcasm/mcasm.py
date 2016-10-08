#!/usr/bin/python
# -*- encoding: utf-8 -*-
#
# Translate Micro-BESM microcode sources into binary files.
#
#from tables import *
#from helpers import *
import sys, codecs, re

# Check parameters.
if len(sys.argv) != 2:
    print "Usage: mcasm file"
    sys.exit(1)

field = {}                      # Field declarations
const = {}                      # Constants
equ = {}                        # Equivalences
const_index = 0                 # ROM index of next constant

#
# Process the input file.
#
def main(filename):
    a = prepare_file(filename)
    a = map(do_field, a)
    a = map(do_const, a)
    a = map(do_equ, a)
    a = map(do_flist, a)
    a = map(do_check, a)
    a = map(do_macro, a)
    #print "Fields:", field
    #print "Constants:", const
    #translate(a)
    #write_results()
    print "--- Unknown instructions:"
    for s in a:
        if s: print s

#
# Process an input line;
# strip out comments and monitor instructions.
#
def remove_comments(s):
    if s[0] == ';' or s[0] == '*':
        return ''
    idx = s.find(";")
    if idx >= 0:
        s = s[:idx]
    return s
#
# Replace cyrillic letters with latin.
#
def replace_char(c):
    if c == u"А": return "A"
    if c == u"В": return "B"
    if c == u"Е": return "E"
    if c == u"К": return "K"
    if c == u"М": return "M"
    if c == u"Н": return "H"
    if c == u"О": return "O"
    if c == u"Р": return "P"
    if c == u"С": return "C"
    if c == u"Т": return "T"
    if c == u"У": return "Y"
    if c == u"Х": return "X"
    return c

#
# Process an input line;
# replace cyrillic letters with latin.
#
def convert_encoding(s):
    s = s.strip()
    s = unicode(s, "utf-8")
    s = ''.join(map(replace_char, s))
    s = s.encode("ascii")
    return s

#
# Join continuation lines
#
def join_continuations(a):
    i = 1
    while i < len(a):
        if a[i][0] == ">":
            a[i-1].extend(a[i][1:])
            del a[i]
        else:
            i += 1
    return a

#
# Read the contents of the input file.
# Remove comments.
#
def prepare_file(filename):
    file = open(filename)
    a = file.readlines()
    a = map(remove_comments, a)

    # Convert encoding, strip white space.
    a = map(convert_encoding, a)

    # Remove empty lines.
    a = filter(lambda x : x != '', a)

    # Split instruction lines.
    a = [ re.split("[: ,]", i) for i in [ x for x in a ] ]

    # Join continuation lines
    a = join_continuations(a)
    return a

#
# Process FIELD instruction.
#
def do_field(op):
    if len(op) < 2 or op[1] != "FIELD":
        return op

    # Store the field description in the global dictionary.
    name = op[0]
    upper = op[2]
    lower = op[3]
    try:
        dflt = int(op[4])
    except:
        dflt = 0
    field[name] = {'upper':upper, 'lower':lower, 'default':dflt}
    #print name, field[name]['upper'], field[name]['lower'], field[name]['default']
    return ''

#
# Process CONST instruction.
#
def do_const(op):
    global const_index
    if len(op) < 2 or op[1] != "CONST":
        return op

    # Store the const description in the global dictionary.
    name = op[0]
    value = int(op[2], 16)
    const[name] = {'value':value, 'index':const_index}
    const_index += 1
    #print name, "%x"%const[name]['value'], const[name]['index']
    return ''

#
# Process EQU instruction.
#
def do_equ(op):
    global const_index
    if len(op) < 2 or op[1] != "EQU":
        return op

    # Store the symbol value in the global dictionary.
    name = op[0]
    try:
        if op[2][0] == '$':
            # Hex value
            value = int(op[2][1:], 16)
        else:
            # Decimal value
            value = int(op[2])
    except:
        # Name of constant or another equivalence
        if op[2] in equ.keys():
            value = equ[op[2]]
        else:
            value = const[op[2]]['index']

    equ[name] = value
    #print name, equ[name]
    return ''

#
# Process FLIST instruction.
#
def do_flist(op):
    #TODO
    return op

#
# Process CHECK instruction.
#
def do_check(op):
    #TODO
    return op

#
# Process MACRO instruction.
#
def do_macro(op):
    #TODO
    return op

def translate(a):
    #TODO
    return

def make_atable(a):
    start = 16 #start address for symbolic variables
    for i in a: # add to symbols table
        if is_a_command(i): #A_Command
            val = i[1:]
            if try_parse_int(val) is not None:
                atable[i] = to_b(int(val))
            elif val in predef_table.keys(): #not int, variable
                atable[i] = to_b(predef_table[val])
            elif i in atable.keys():
                continue
            else:
                atable[i] = to_b(start)
                start += 1

def make_ctable(a):
    for i in a:
        if is_c_command(i):
            semi = i.find(';')
            equa = i.find('=')

            if equa != -1 and semi != -1: #dest=comp;jump
                dest = i[:equa]
                comp = i[equa+1:semi]
                jump = i[semi+1:]
                abit = set_abit(comp)
                ctable[i] = first + abit + comp_table[comp] + dest_table[dest] + jump_table[jump]

            if equa == -1 and semi != -1: #comp;jump
                comp = i[:semi]
                jump = i[semi+1:]
                abit = set_abit(comp)
                ctable[i] = first + abit + comp_table[comp] + dest_table["null"] + jump_table[jump]

            if equa != -1 and semi == -1: #dest=comp
                dest = i[:equa]
                comp = i[equa+1:]
                abit = set_abit(comp)
                ctable[i] = first + abit + comp_table[comp] + dest_table[dest] + jump_table["null"]

def write_results():
    #name = filename + ".hack"
    #file = open(name,'w')
    #for i in a:
    #    file.write(i+"\n")
    #file.close()
    #TODO
    return

if __name__ == "__main__":
    main(sys.argv[1])
