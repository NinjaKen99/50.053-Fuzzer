# NECCESSARY IMPORTS
from random import randint

# Re-used variables
choices = [1, 2, 4]
bits_in_byte = 8

# FUNCTIONS USED TO ASSIST MUTATION
def to_binary_2d(input):
    byte_count = 0
    # Sample to split into bits
    byte_string = ' '.join(format(ord(x), 'b') for x in input)
    byte_set = byte_string.split(" ")
    bit_set = []
    for byte in byte_set:
        byte_count += 1
        byte_to_bit = byte.split("")
        bit_set.append(byte_to_bit)
    return bit_set, byte_count

def to_binary_1d(input):
    bit_count = 0
    # Sample to split into bits
    byte_string = ' '.join(format(ord(x), 'b') for x in input)
    byte_set = byte_string.split(" ")
    bit_set = []
    for byte in byte_set:
        byte_to_bit = byte.split("")
        for bit in byte_to_bit:
            bit_count += 1
            bit_set.append(bit)
    return bit_set, bit_count


# HERE IS WHERE ALL FUNCTIONS TO PERFORM A MUTATION SHALL BE MADE

# Flip a set number of consecutive bits
def bitflip (input: str):
    b, number = to_binary_1d(input)
    # choose number of bits to change
    count = choices[randint(0,2)]
    start_of_change = randint(0, number - 1 - count)
    for i in range (start_of_change, start_of_change + count):
            if (b[i] == '1'):
                b[i] = '0'
            elif (b[i] == '0'):
                b[i] = '1'
    output = "".join(b)
    return output

# Flip a set number of consecutive bytes
def byteflip (input: str):
    b, number = to_binary_2d(input)
    # choose number of bytes to change
    count = choices[randint(0,2)]
    start_of_change = randint(0, number - 1 - count)
    for i in range (start_of_change, start_of_change + count):
        for j in range(bits_in_byte):
            if (b[i][j] == '1'):
                b[i][j] = '0'
            elif (b[i][j] == '0'):
                b[i][j] = '1'
    output = "".join("".join(x) for x in b)
    return output

# Change a single byte in test case
def random_bytes (input: str):
    b, number = to_binary_2d(input)
    # Create a byte for replacement
    replacement = []
    for i in range(bits_in_byte):
        bit = randint(0,1)
        if (bit == 1):
            replacement.append('1')
        elif (bit == 0):
            replacement.append('0')
    # Choose which byte to replace
    rbyte = randint(o, number-1)
    b[rbyte] = replacement
    output = "".join("".join(x) for x in b)
    return output

# Completely remove a certain number of consecutive bytes
def delete_bytes (input: str):
    b, number = to_binary_2d(input)
    start_point = randint(0, number - 1)
    limit = (number - 1) - start_point
    count = randint(0, limit)
    for i in range(count + 1):
        b.pop(start_point)
    output = "".join("".join(x) for x in b)
    return output

def insert_bytes (input: str, sample: str):
    # Needs other cases to copy bytes from
    b1, number1 = to_binary_2d(input)
    b2, number2 = to_binary_2d(sample)
    b3 = []
    extract = randint(0,number2 -1)
    insertion = randint(0, number1 -1)
    for i in range(0,insertion):
        b3.append(b1[i])
    b3.append(sample[extract])
    for i in range(insertion, number1):
        b3.append[b1[i]]
    output = "".join("".join(x) for x in b3)
    return output

# Change several bytes in a text case
def overwrite_bytes (input: str):
    # Similar to random
    return input