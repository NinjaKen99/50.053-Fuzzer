# NECCESSARY IMPORTS
from random import randint

# Re-used variables
choices = [1, 2, 4]
bits_in_byte = 8


class mutation:
    
    ### FUNCTIONS USED TO ASSIST MUTATION
    # Covert input string into array of bytes
    @staticmethod
    def str_to_bytes(input: str):
        # Returns an array of strings that represent bytes eg. ['00110011', '11001100]
        byte_set = [bin(ord(x))[2:].zfill(8) for x in input]
        byte_count = len(byte_set)
        return byte_set, byte_count
    
    # Convert array of bytes into string
    @staticmethod
    def bytes_to_str(input: list):
        return ''.join([chr(int(x, 2)) for x in input])
    
    # Covert input int into array of bytes
    @staticmethod
    def int_to_bytes(input: int):
        # Returns an array of strings that represent bytes eg. ['00110011', '11001100]
        byte_set = []
        byte_count = 4
        b32 = bin(input)[2:].zfill(32)
        for i in range(byte_count):
            byte_set.append(b32[i*8 : 8 + i*8])
        return byte_set, byte_count
    
    # Convert array of bytes into integer
    @staticmethod
    def bytes_to_int(input: list):
        return int(''.join(x for x in input) , 2)
    
    @staticmethod
    def convert_bytes(input):
        datatype = type(input)
        if isinstance(input, str):
            output1, output2 = mutation.str_to_bytes(input)
        elif isinstance(input, int):
            output1, output2 = mutation.int_to_bytes(input)
        return output1, output2, datatype
    
    @staticmethod
    def convert_back(input: list, datatype):
        if (datatype == str):
            output = mutation.bytes_to_str(input)
        elif (datatype == int):
            output = mutation.bytes_to_int(input)
        return output
    
    ### HERE IS WHERE ALL FUNCTIONS TO PERFORM A MUTATION SHALL BE MADE
    # Flip a set number of consecutive bits within a byte
    @staticmethod
    def bitflip (input = "testing"):
        b, number, datatype = mutation.convert_bytes(input)
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
        return mutation.convert_back(b, datatype)
    
    # Flip a set number of consecutive bytes
    @staticmethod
    def byteflip (input = "testing"):
        b, number, datatype = mutation.convert_bytes(input)
        # choose number of bytes to change
        count = choices[randint(0,2)]
        output = ""
        if (datatype == int and count == 4):
            start_of_change = 0
        else:
            start_of_change = randint(0, number - 1 - count)
        for bytes in range (start_of_change, start_of_change + count):
            temp = ""
            for bit in b[bytes]:
                if (bit == '1'):
                    temp += '0'
                elif (bit == '0'):
                    temp += '1'
            b[bytes] = '0' + temp[1:] # Prevent exceed charmap
        return mutation.convert_back(b, datatype)
    
    # Insert byte from different test case ONLY WORKS FOR STRING
    @staticmethod
    def insert_bytes (input = "testing", sample = "anything"):
        # Needs other cases to copy bytes from
        b1, number1 = mutation.str_to_bytes(input)
        b2, number2 = mutation.str_to_bytes(sample)
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
        b, number, datatype = mutation.convert_bytes(input)
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
        return mutation.convert_back(b, datatype)
    
    # Completely remove a certain number of consecutive bytes
    @staticmethod
    def delete_bytes (input = "testing"):
        b, number, datatype = mutation.convert_bytes(input)
        if (datatype == str):
            start_point = randint(0, number - 1)
            limit = (number - 1) - start_point
            count = randint(0, limit)
        elif (datatype == int):
            start_point = randint(0, number - 1)
            limit = (number - 2) - start_point
            if limit <= 0:
                count = 0
            else:
                count = randint(0, limit)
        for i in range(count + 1):
            b.pop(start_point)
        return mutation.convert_back(b, datatype)
    
    # Change several bytes in a text case
    #def overwrite_bytes (input = ""):
        # Similar to random
    #    return input


#testing = int
print('test')
#print(testing)
#test_set, test_number = mutation.int_to_bytes(2143765)
#print(mutation.bytes_to_int(test_set))
print(mutation.delete_bytes(123))