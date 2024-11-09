import himage as hi # type: ignore
import numpy as np
import numpy.typing as npt

ImageArray = npt.NDArray[np.uint8]
InputImageArray = ImageArray | npt.NDArray[np.float32]
BinArray = npt.NDArray[np.uint8] | npt.NDArray[np.bool_]

class Steganographer:

    def __init__(self) -> None:
        self.start: int
        self.end: int
        self.n_used_lsb: int
        self.clear_msg: str
        self.shape: tuple[int,int,int] | tuple[int, int]
        self.mask_size: int
        self.flat_im: ImageArray # we manipulate the flattened image, that way it doesn't matter wether its colored or grayscale
        self.msg:str
        self.bin_msg: BinArray

    def set_im(self, im:InputImageArray):
        """
        set the image to be used for steganography
        """
        vmin, vmax = hi.deduce_limits(im) # type: ignore
        if vmax <= 1:
            im = np.asarray(im*255, dtype=np.uint8)
        else:
            im = np.asarray(im, dtype=np.uint8)
        self.shape = im.shape
        self.flat_im = im.flatten()
        return self

    def set_msg(self, msg:str):
        """
        set the message to be written to the image
        """
        self.msg = msg
        byte_string = bytes(msg, 'utf-8')
        self.bin_msg = np.unpackbits(np.frombuffer(byte_string, dtype=np.uint8))
        return self

    def write_msg(self):
        """
        write the actuall message to the image
        """
        self.clean_lsb()
        mask = self.message_to_mask()
        self.apply_mask(mask)
        return self

    def read_msg(self):
        """
        read the message from the image
        """
        # read the last bit of each value in the image
        mask = np.asarray(self.flat_im%2, dtype=np.uint8) 

        bin_msg_size = self.decode_size(mask[:64])

        # Convert the numpy array to bytes
        byte_string = np.packbits(mask[64: 64 + int(bin_msg_size)])

        return byte_string.tobytes().decode('utf-8')

    def export(self, path: str):
        hi.imwrite(self.flat_im.reshape(self.shape), path) # type: ignore

    @staticmethod
    def encode_size(size:int):
        # Convert the number to an array of one integer
        int_array = np.array([size], dtype=np.uint64)

        # Convert the array of integers to a binary array
        bits_array = np.unpackbits(int_array.view(np.uint8))
        return bits_array
    
    @staticmethod
    def decode_size(bits_array: BinArray):
        """
        input : 64 bits array that represents the bite length of the message encoded to the image
        output : int, the size of the message encoded to the image
        """
        return np.packbits(bits_array).view(np.uint64)[0]
    
    def message_to_mask(self):
        # Convert the string to bytes
        byte_string = bytes(self.msg, 'utf-8')

        self.bin_msg = np.unpackbits(np.frombuffer(byte_string, dtype=np.uint8))

        mask = np.zeros((self.flat_im.size), dtype=self.bin_msg.dtype)

        size_and_bin_msg = np.hstack((self.encode_size(self.bin_msg.size), self.bin_msg))

        mask[:size_and_bin_msg.size] = size_and_bin_msg

        return mask 

    def clean_lsb(self):
        self.flat_im -= self.flat_im%2 # type: ignore

    def apply_mask(self, mask: ImageArray):
        self.flat_im = self.flat_im + mask
