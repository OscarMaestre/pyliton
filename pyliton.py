#!/usr/bin/python3

import sys, re

USAGE="""
Usage: pyliton <filename>
       pyliton will process filename and generate 2 files:
       <filename>.out: program to be compiled/interpreted
       <filename>.rst: Literate description of the programa in Sphinx format
"""


REGEX_DEFINE_BLOCK="^---(?P<blockname>[a-zA-Z0-9 ]+)---(?P<language>[a-zA-Z]*)"
REGEX_DEFINE_END_BLOCK="^---$"


STATE_READING_LINES=0
STATE_READING_BLOCK=STATE_READING_LINES+1

class State(object):
    def __init__(self):
        super().__init__()
        self.current_state=STATE_READING_LINES
    def get_state(self):
        return self.current_state
    def to_reading_lines_mode(self):
        self.current_state=STATE_READING_LINES
    def to_reading_block_mode(self):
        self.current_state=STATE_READING_BLOCK

class Block(object):
    def __init__(self, name):
        super().__init__()
        self.name=name
        self.lines=[]
    def append_line(self, line):
        self.lines.append(line)
    def __str__(self):
        text="--Block:{0}\n".format(self.name)
        text+="".join(self.lines)
        text+="--End block"
        return text

def read_defined_blocks(lines):
    re_define_block         =   re.compile(REGEX_DEFINE_BLOCK)
    re_define_end_block     =   re.compile(REGEX_DEFINE_END_BLOCK)

    counter=0
    max_lines=len(lines)
    state=State()
    blocks=[]
    current_block=None
    while counter < max_lines:
        current_line=lines[counter]        
        result=re_define_block.match(current_line)
        if result!=None:
            #We found the start of a "define block"
            name=result.group("blockname")
            #print("Match:"+name)
            state.to_reading_block_mode()
            current_block=Block(name)
            counter=counter+1
            continue
        result=re_define_end_block.match(current_line)
        if result!=None and state.get_state()==STATE_READING_BLOCK:
            state.to_reading_lines_mode()
            blocks.append(current_block)
            current_block=None

        if state.get_state()==STATE_READING_BLOCK:
            current_block.append_line(current_line)

        counter=counter+1
    #End of while
    return blocks

def pyliton(filename):
    #print(filename)
    with open(filename) as file:
        lines=file.readlines()
        defined_blocks=read_defined_blocks(lines)
        print("Blocks")
        for b in defined_blocks:
            print(b)
        

if __name__ == "__main__":
    if len(sys.argv)!=2:
        print (USAGE)
    else:
        pyliton(sys.argv[1])