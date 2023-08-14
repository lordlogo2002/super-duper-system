import unittest
import string
import logger

log = logger.create_logger("gen", "gen.log")

def encrypt(message:str, *, shift_by:int=1) -> str:
    abc = string.printable
    abc_length = len(abc)

    def shift_char(char, shift):
        abc_index = abc.find(char)
        distance_to_end = abc_length - abc_index
        target_index = abc_index + shift
        if target_index >= len(abc):
            target_index = shift - distance_to_end
        return abc[target_index]

    encrypted_message = "".join(shift_char(char, shift_by) for char in message)
    return encrypted_message

class Test(unittest.TestCase):
    def setUp(self):
        self.my_message = "banana bread yo mama isa 2 fat 4 me " + string.printable

    def test_inputExists(self):
        self.assertIsNotNone(self.my_message)

    def test_inputType(self):
        self.assertIsInstance(self.my_message, str)

    def test_functionReturnsSomething(self):
        self.assertIsNotNone(encrypt(self.my_message))

    def test_lenIO(self):
        self.assertEqual(len(self.my_message), len(encrypt(self.my_message)))

    def test_differentIO(self):
        self.assertNotIn(self.my_message, encrypt(self.my_message))

    def test_outputType(self):
        self.assertIsInstance(encrypt(self.my_message), str)

    def test_shiftedCipher(self):
        abc = string.printable

        def shift_char(char):
            target_index = abc.find(char) + 1
            if target_index >= len(abc):
                target_index = 0
            return abc[target_index]

        for char in self.my_message:
            encrypted_message = "".join(shift_char(char) for char in self.my_message)
        self.assertEqual(encrypted_message, encrypt(self.my_message))

    def test_multiShiftedCipherByPositive(self):
        abc = string.printable
        abc_length = len(abc)

        def shift_char(char, shift):
            abc_index = abc.find(char)
            distance_to_end = abc_length - abc_index
            target_index = abc_index + shift
            if target_index >= len(abc):
                target_index = shift - distance_to_end
            return abc[target_index]

        for test_shift in (2, 4, 8, 16, 32, 64, 128):
            log.info(f"Trying to shift by {test_shift}")

            test_script_result = "".join(shift_char(char, test_shift) for char in self.my_message)
            encrypt_function_result = encrypt(self.my_message, shift_by=test_shift)

            if test_script_result != encrypt_function_result:
                log.error(f"failed on shifting {test_shift}")

            self.assertEqual(test_script_result, test_script_result)

def main():
    unittest.main()

if __name__ == "__main__":
    main()