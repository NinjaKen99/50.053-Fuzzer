# NECCESSARY IMPORTS
from random import randint

# Formatting into binary sample
test = "test"
print(' '.join(format(ord(x), 'b') for x in a))

# FUNCTION TO TRANSFORM INPUT INTO BINARY
def to_binary(input):
    # Sample to split into bits
    byte_string = ' '.join(format(ord(x), 'b') for x in input)
    byte_set = byte_string.split(" ")
    bit_set = []
    for byte in byte_set:
        byte_to_bit = byte.split("")
        bit_set.append(byte_to_bit)
    return bit_set

# HERE IS WHERE ALL FUNCTIONS TO PERFORM A MUTATION SHALL BE MADE

def bitflip (input: str):
    
    return input

def byteflip (input: str):
    
    return input

def arithmetic_inc (input: str):
    
    return input

def arithmetic_dec (input: str):
    
    return input

def random_bytes (input: str):
    
    return input

def delete_bytes (input: str):
    
    return input

def insert_bytes (input: str):
    
    return input

def overwrite_bytes (input: str):
    
    return input