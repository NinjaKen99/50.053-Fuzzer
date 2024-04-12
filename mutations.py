# NECCESSARY IMPORTS
from random import randint

# Re-used variables
choices = [1, 2, 4]
bits_in_byte = 8
ascii_max = 256
ascii_uppercase_range = [65, 90]
ascii_lowercase_range = [97, 122]
ascii_number_range = [48, 57]
whitespace = "00100000"


class mutation:
    
    ### FUNCTIONS USED TO ASSIST MUTATION
    # Covert input string into array of bytes
    @staticmethod
    def str_to_bytes(input: str):
        # Returns an array of strings that represent bytes eg. ['00110011', '11001100]
        byte_set = [bin(ord(x))[2:].zfill(8) for x in input]
        initial_byte_count = len(byte_set)
        added = 128 - initial_byte_count
        adding = ['00000000' for i in range(added)]
        byte_set = adding + byte_set
        byte_count = len(byte_set)
        return byte_set, byte_count
    
    # Convert array of bytes into string
    @staticmethod
    def bytes_to_str(input: list):
        return ''.join([chr(int(x, 2)) for x in input])
    
    # Convert byte object into str
    @staticmethod
    def b_to_str(input):
        return input.decode('utf-8', "strict")
    
    # Convert str to b
    @staticmethod
    def str_to_b(input):
        return input.encode('utf-8', "strict")
    
    # Covert input int into array of bytes
    @staticmethod
    def int_to_bytes(input: int):
        # Returns an array of strings that represent bytes eg. ['00110011', '11001100]
        byte_set = []
        b64 = bin(input)[2:].zfill(64)
        for i in range(byte_count):
            byte_set.append(b64[i*8 : 8 + i*8])
        byte_count = len(byte_set)
        return byte_set, byte_count
    
    # Convert array of bytes into integer
    @staticmethod
    def bytes_to_int(input: list):
        return int(''.join(x for x in input) , 2)
    
    # Convert b to int
    @staticmethod
    def b_to_int(input):
        return int.from_bytes(input, 'big')
    
    # Convert int to b
    @staticmethod
    def int_to_b(input):
        return input.to_bytes(2,'big')
    
    
    @staticmethod
    def convert_bytes(input):
        datatype = type(input)
        if (datatype == bytes):
            try:
                intermediate = mutation.b_to_str(input)
            except:
                intermediate = mutation.b_to_int(input)
        else:
            intermediate = input
        if isinstance(intermediate, str):
            output1, output2 = mutation.str_to_bytes(intermediate)
        elif isinstance(intermediate, int):
            output1, output2 = mutation.int_to_bytes(intermediate)
        return output1, output2, datatype
    
    @staticmethod
    def convert_back(input: list, datatype):
        if (datatype == str):
            output = mutation.bytes_to_str(input)
        elif (datatype == int):
            output = mutation.bytes_to_int(input)
        return output
    
    @staticmethod
    def convert_to_b(input):
        if isinstance(input, str):
            output = mutation.str_to_b(input)
        elif isinstance(input, int):
            output = mutation.int_to_b(input)
        return output
    
    ### FUNCTIONS THAT PERFORM MUTATIONS ON BINARY BYTES
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
        b1, number1, datatype1 = mutation.convert_bytes(input)
        b2, number2, datatype2 = mutation.convert_bytes(sample)
        if (datatype1 == int):
            print("Input may not work")
            return input
        b3 = []
        extract = randint(0,number2 -1)
        insertion = randint(0, number1 -1)
        for i in range(0,insertion):
            b3.append(b1[i])
        b3.append(b2[extract])
        for i in range(insertion, number1):
            b3.append(b1[i])
        output = ''.join([chr(int(x, 2)) for x in b3])
        return output
    
    # Change a single byte in test case
    @staticmethod
    def random_byte_str (input = "testing"):
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
    
    @staticmethod
    def random_byte_int (input = 123467):
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
        rng = randint(0,1)
        if (rng == 1):
            rbyte = randint(0, 3)
        else:
            rbyte = randint(4, 7)
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
    
    @staticmethod
    def random_mutation(input = "testing"):
        mutation_count = 5
        chosen_mutation = randint(1,mutation_count)
        match chosen_mutation:
            case 1:
                return mutation.bitflip(input)
            case 2:
                return mutation.byteflip(input)
            case 3:
                sample = "something"
                return mutation.insert_bytes(input, sample)
            case 4:
                if isinstance(input, str):
                    return mutation.random_byte_str(input)
                elif isinstance(input, int):
                    return mutation.random_byte_int(input)
            case 5:
                return mutation.delete_bytes(input)
            case _:
                # Error
                print("Error in random_mutation has occured.\n")
                pass
        return input
    
    ########## ASCII OPERATIONS ##########
    @staticmethod
    def str_to_ascii(input):
        output = []
        count = 0
        for character in input:
            output.append(ord(character))
            count += 1
        return output, count
    
    @staticmethod
    def int_to_ascii(input):
        string = str(input)
        output, count = mutation.str_to_ascii(input)
        return output, count
    
    @staticmethod
    def ascii_to_str(input):
        return ''.join(map(chr,input))
    
    @staticmethod
    def ascii_to_int(input):
        numstr = mutation.ascii_to_str(input)
        return int(numstr)



#testing = int
#print('test')
#print(testing)
#test_set, test_number = mutation.int_to_bytes(2143765)
#print(mutation.bytes_to_int(test_set))
#print(mutation.delete_bytes(123))

message = "testing"
byte_message = bytes(message, 'utf-8')
number = 383
number = 127
bytes_number = number.to_bytes(2, 'big')
print('test')
print(chr(int('00100011', 2)) + chr(int('00000000', 2)) + chr(int('00100011', 2)))
print('end')
try:
    print(mutation.b_to_str(bytes_number))
except:
    print(mutation.b_to_int(bytes_number))