# NECCESSARY IMPORTS
from random import randint

# Re-used variables
choices = [1, 2, 4]
bits_in_byte = 8


class mutation:
    
    ### FUNCTIONS USED TO ASSIST MUTATION
    # Covert input string into 
    @staticmethod
    def to_bytes(input: str):
        # Returns an array of strings that represent bytes eg. ['00110011', '11001100]
        byte_set = [bin(ord(x))[2:].zfill(8) for x in input]
        byte_count = len(byte_set)
        return byte_set, byte_count
    
    ### HERE IS WHERE ALL FUNCTIONS TO PERFORM A MUTATION SHALL BE MADE
    # Flip a set number of consecutive bits within a byte
    @staticmethod
    def bitflip (input = "testing"):
        b, number = mutation.to_bytes(input)
        # choose number of bits to change
        count = choices[randint(0,2)]
        index = randint(0, number-1)
        byte_chosen = b[index]
        start_of_change = randint(1, bits_in_byte - count)
        replacement = byte_chosen[:start_of_change]
        for i in range (start_of_change, start_of_change + count):
                if (byte_chosen[i] == '1'):
                    replacement += '0'
                elif (byte_chosen[i] == '0'):
                    replacement += '1'
        replacement += byte_chosen[start_of_change + count:]
        b[index] = replacement
        output = ''.join([chr(int(x, 2)) for x in b])
        return output
    
    # Flip a set number of consecutive bytes
    @staticmethod
    def byteflip (input = "testing"):
        b, number = mutation.to_bytes(input)
        # choose number of bytes to change
        count = choices[randint(0,2)]
        output = ""
        start_of_change = randint(0, number - 1 - count)
        for bytes in range (start_of_change, start_of_change + count):
            temp = ""
            for bit in b[bytes]:
                if (bit == '1'):
                    temp += '0'
                elif (bit == '0'):
                    temp += '1'
            b[bytes] = '0' + temp[1:] # Prevent exceed charmap
        output = ''.join([chr(int(x, 2)) for x in b])
        return output
    
    # Insert byte from different test case
    @staticmethod
    def insert_bytes (input = "testing", sample = "anything"):
        # Needs other cases to copy bytes from
        b1, number1 = mutation.to_bytes(input)
        b2, number2 = mutation.to_bytes(sample)
        b3 = []
        extract = randint(0,number2 -1)
        insertion = randint(0, number1 -1)
        for i in range(0,insertion):
            b3.append(b1[i])
        b3.append(b2[extract])
        for i in range(insertion, number1):
            b3.append[b1[i]]
        output = ''.join([chr(int(x, 2)) for x in b3])
        return output
    
    # Change a single byte in test case
    @staticmethod
    def random_byte (input = "testing"): 
        b, number = mutation.to_bytes(input)
        # Create a byte for replacement
        replacement = ""
        for i in range(bits_in_byte):
            bit = randint(0,1)
            if (bit == 1):
                replacement += '1'
            elif (bit == 0):
                replacement += '0'
        # Choose which byte to replace
        rbyte = randint(0, number-1)
        b[rbyte] = replacement
        output = ''.join([chr(int(x, 2)) for x in b])
        return output
    
    # Completely remove a certain number of consecutive bytes
    @staticmethod
    def delete_bytes (input = "testing"):
        b, number = mutation.to_bytes(input)
        start_point = randint(0, number - 1)
        limit = (number - 1) - start_point
        count = randint(0, limit)
        for i in range(count + 1):
            b.pop(start_point)
        output = ''.join([chr(int(x, 2)) for x in b])
        return output
    
    # Change several bytes in a text case
    #def overwrite_bytes (input = ""):
        # Similar to random
    #    return input


print("test")
print(mutation.byteflip("testing"))