#!/usr/bin/python3

import sys, re

USAGE="""
Usage: pyliton <filename>
       pyliton will process filename and generate 2 files:
       <filename>.out: program to be compiled/interpreted
       <filename>.rst: Literate description of the programa in Sphinx format
"""


REGEX_BLOCK_NAME="(?P<blockname>[a-zA-Z0-9\. ]+)"
REGEX_DEFINE_BLOCK="^---"+REGEX_BLOCK_NAME+"---(?P<language>[a-zA-Z]*)"
REGEX_DEFINE_END_BLOCK="^---$"

REGEX_MACRO_TO_EXPAND="(?P<spaces>\s*)\@\{"+REGEX_BLOCK_NAME+"\}"
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
    def get_name(self):
        return self.name
    def get_lines(self):
        return self.lines
    def __str__(self):
        text=""
        text+="".join(self.lines)
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


def get_text_from_list_of_blocks(block_name, defined_blocks, spaces_prefix):
    for b in defined_blocks:
        if b.get_name()==block_name:
            block_lines=b.get_lines()
            lines_with_prefix=[spaces_prefix+line for line in block_lines]
            return "".join(lines_with_prefix)
    return "Undefined block:"+block_name


def get_block(block_name, defined_blocks):
    for b in defined_blocks:
        if b.get_name()==block_name:
            return b
    return None

def expand_block(block, defined_blocks):
    result_lines=[]
    re_expand_block         =   re.compile(REGEX_MACRO_TO_EXPAND)
    lines=block.get_lines()
    for l in lines:
        result=re_expand_block.match(l)
        if result!=None:
            spaces_prefix=result.group("spaces")
            block_name=result.group("blockname")
            block_object=get_block(block_name, defined_blocks)
            lines_in_nested_block=expand_block(block_object, defined_blocks)
            lines_with_prefix=[spaces_prefix+line for line in lines_in_nested_block]
            result_lines.extend(lines_with_prefix)
        if result==None:
            result_lines.append(l)
    #end for
    return result_lines

def expand_blocks(lines, defined_blocks):
    result_text=""
    re_expand_block         =   re.compile(REGEX_MACRO_TO_EXPAND)
    counter=0
    max_lines=len(lines)
    
    while counter < max_lines:
        current_line=lines[counter]
        result=re_expand_block.match(current_line)
        if result!=None:
            spaces_prefix=result.group("spaces")
            block_name=result.group("blockname")
            
            expanded_text=get_text_from_list_of_blocks(block_name, defined_blocks, spaces_prefix)
            #print("Resultado expandido:"+expanded_text + " a partir de la macro:"+block_name)
            result_text=result_text+expanded_text
            counter=counter+1
        else:
            #print("Linea              :"+current_line)
            result_text=result_text+current_line
        counter=counter+1
    #End of while
    return result_text

def pyliton(filename):
    #print(filename)
    with open(filename) as file:
        lines=file.readlines()
        defined_blocks=read_defined_blocks(lines)
        first_block=defined_blocks[0]
        
        blocklines=first_block.get_lines()
        #text=expand_blocks(blocklines, defined_blocks)
        result_lines=expand_block(first_block, defined_blocks)
        #print(result_lines)
        final_text="".join(result_lines)
        print(final_text)
        

if __name__ == "__main__":
    if len(sys.argv)!=2:
        print (USAGE)
    else:
        pyliton(sys.argv[1])