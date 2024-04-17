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
    def str_to_bytes(input: str, numbytes):
        # Returns an array of strings that represent bytes eg. ['00110011', '11001100]
        byte_set = [bin(ord(x))[2:].zfill(8) for x in input]
        initial_byte_count = len(byte_set)
        if numbytes == 64:
            added = 128 - initial_byte_count
        else:
            added = 32 - initial_byte_count


        adding = ['00000000' for i in range(added)]
        byte_set = adding + byte_set
        byte_count = len(byte_set)
        return byte_set, byte_count
    
    # Convert array of bytes into string
    @staticmethod
    def bytes_to_str(input: list):
        new_list =  []
        first = False
        for x in input:
            if first == False and x == "00000000":
                continue
            elif first == True and x == "00000000":
                new_list.append(chr(int("00100000", 2)))
            else:
                new_list.append(chr(int(x, 2)))
                first = True
        return ''.join(new_list)
    
    @staticmethod
    def remove_null_byte(input:list):
        new_list =  []
        first = False
        for x in input:
            if first == False and x == "00000000":
                continue
            elif first == True and x == "00000000":
                new_list.append(chr(int("00100000", 2)))
            else:
                new_list.append(chr(int(x, 2)))
                first = True
        return ''.join(new_list)
    
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
    def int_to_bytes(input: int, numbytes):
        # Returns an array of strings that represent bytes eg. ['00110011', '11001100]
        byte_set = []
        neg = False
        if bin(input)[0] == '-':
            b64 = bin(input)[3:].zfill(64)
            neg = True
        else:
            b64 = bin(input)[2:].zfill(64)
        byte_count = numbytes//8
        for i in range(byte_count):
            byte_set.append(b64[i*8 : 8 + i*8])
        byte_count = len(byte_set)
        return byte_set, byte_count, neg
    
    # Convert array of bytes into integer
    @staticmethod
    def bytes_to_int(input: list, neg):
        no = int(''.join(x for x in input) , 2)
        if neg == True:
            no *= -1
        return no
    
    # Convert b to int
    @staticmethod
    def b_to_int(input):
        return int.from_bytes(input, 'big')
    
    # Convert int to b
    @staticmethod
    def int_to_b(input):
        return input.to_bytes(2,'big')
    
    
    @staticmethod
    def convert_bytes(input, numbytes):
        datatype = type(input)
        if (datatype == bytes):
            try:
                intermediate = mutation.b_to_str(input)
            except:
                intermediate = mutation.b_to_int(input)
        else:
            intermediate = input
        if isinstance(intermediate, str):
            output1, output2 = mutation.str_to_bytes(intermediate, numbytes)
            neg = None
        elif isinstance(intermediate, int):
            output1, output2, neg = mutation.int_to_bytes(intermediate, numbytes)
        
        return output1, output2, datatype, neg
    
    @staticmethod
    def convert_back(input: list, datatype, numbytes, neg):
        if (datatype == str):
            output = mutation.bytes_to_str(input)
        elif (datatype == int):
            output = mutation.bytes_to_int(input, neg)
        elif (datatype == bytes):
            output = b''.join([bytes([int(byte, 2)]) for byte in input])
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
    def bitflip (input = "testing", numbytes = 64):
        b, number, datatype, neg = mutation.convert_bytes(input, numbytes)
        # choose number of bits to change
        if number < 1:
            # Handle the case where the input is empty or the conversion failed
            return input

        # choose number of bits to change
        count = choices[randint(0, 2)]

        if number <= count:
            # If the number of bytes is less than or equal to the number of bytes to flip,
            # just flip all the bits
            index = 0
        else:
            index = randint(0, number - 1)
        byte_chosen = b[index]
        bits_in_byte = len(byte_chosen)
        if bits_in_byte < count:
            # If the number of bits to flip is greater than the number of bits in the byte,
            # just flip all the bits
            start_of_change = 0
        else:
            start_of_change = randint(0, bits_in_byte - count)
        replacement = byte_chosen[:start_of_change]
        for i in range (start_of_change, start_of_change + count):
            if (byte_chosen[i] == '1'):
                replacement += '0'
            elif (byte_chosen[i] == '0'):
                replacement += '1'
        replacement += byte_chosen[start_of_change + count:]
        b[index] = replacement
        return mutation.convert_back(b, datatype, numbytes, neg)
    
    # Flip a set number of consecutive bytes
    @staticmethod
    def byteflip (input = "testing", numbytes = 64):
        b, number, datatype, neg = mutation.convert_bytes(input, numbytes)
        if len(b) < 1:
            # Handle the case where the input is empty or the conversion failed
            return input
        # choose number of bytes to change
        count = choices[randint(0,2)]
        output = ""
        if number <= count:
            # If the number of bytes is less than or equal to the number of bytes to flip,
            # just flip all the bytes
            start_of_change = 0
        else:
            start_of_change = randint(0, number - count - 1)
        for bytes in range (start_of_change, start_of_change + count):
            if bytes >= len(b):
                # Handle the case where the index is out of range
                break
            temp = ""
            for bit in b[bytes]:
                if (bit == '1'):
                    temp += '0'
                elif (bit == '0'):
                    temp += '1'
            b[bytes] = '0' + temp[1:] # Prevent exceed charmap
        return mutation.convert_back(b, datatype, numbytes, neg)
    
    # Insert byte from different test case ONLY WORKS FOR STRING
    @staticmethod
    def insert_bytes (input = "testing", sample = "anything", numbytes = 64):
        # Needs other cases to copy bytes from
        b1, number1, datatype1, neg = mutation.convert_bytes(input, numbytes)
        b2, number2, datatype2, neg = mutation.convert_bytes(sample, numbytes)
        if (datatype1 == int):
            print("Input type may result in failure.")
        b3 = []
        extract = randint(0,number2 -1)
        insertion = randint(0, number1 -1)
        for i in range(0,insertion):
            b3.append(b1[i])
        b3.append(b2[extract])
        for i in range(insertion, number1):
            b3.append(b1[i])
        output = mutation.convert_back(b3, datatype1, numbytes, neg)
        return output
    
    # Change a single byte in test case
    @staticmethod
    def random_byte_str (input = "testing", numbytes=64):
        b, number, datatype, neg = mutation.convert_bytes(input, numbytes)
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
        return mutation.convert_back(b, datatype, numbytes, neg)
    
    @staticmethod
    def random_byte_int (input = 123467, numbytes = 64):
        b, number, datatype, neg = mutation.convert_bytes(input, numbytes)
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
        return mutation.convert_back(b, datatype, numbytes, neg)
    
    
    # Completely remove a certain number of consecutive bytes
    @staticmethod
    def delete_bytes (input = "testing", numbytes=64):
        b, number, datatype, neg = mutation.convert_bytes(input, numbytes)
        if number <= 0:
            return mutation.convert_back(b, datatype)
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
        else:
            start_point = randint(0, number - 1)
            limit = (number - 2) - start_point
            if limit <= 0:
                count = 0
            else:
                count = randint(0, limit)
        for i in range(count + 1):
            b.pop(start_point)
        return mutation.convert_back(b, datatype, numbytes, neg)
    
    @staticmethod
    def random_mutation(input = "testing", num_bytes = 64):
        mutation_count = 5
        chosen_mutation = randint(1,mutation_count)
        match chosen_mutation:
            case 1:
                return mutation.bitflip(input, num_bytes)
            case 2:
                return mutation.byteflip(input, num_bytes)
            case 3:
                sample = "something"
                return mutation.insert_bytes(input, sample, num_bytes)
            case 4:
                if isinstance(input, str):
                    return mutation.random_byte_str(input, num_bytes)
                elif isinstance(input, int):
                    return mutation.random_byte_int(input, num_bytes)
            case 5:
                return mutation.delete_bytes(input, num_bytes)
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

# message = "testing"
# byte_message = bytes(message, 'utf-8')
# number = 383
# number = 127
# bytes_number = number.to_bytes(2, 'big')
# print(type(bytes_number))
# try:
#     print(mutation.b_to_str(bytes_number))
# except:
#     print(mutation.b_to_int(bytes_number))