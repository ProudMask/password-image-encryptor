from PIL import Image

def encrypt_password_to_image(password, image_path, output_path):
    """Encrypts a password into an image using the least significant bit 
technique."""
    # Open the image
    with Image.open(image_path) as img:
        # Get the pixels of the image
        pixels = img.load()
        # Convert the password to binary
        binary_password = "".join([format(ord(char), '08b') for char in 
password])
        # Add null characters to the end of the password to ensure it fits 
in the image
        null_count = (len(binary_password) // 3 + 1) * 3 - 
len(binary_password)
        binary_password += "0" * null_count
        # Iterate over each pixel and replace the least significant bit of 
each color channel with a bit from the password
        for y in range(img.size[1]):
            for x in range(img.size[0]):
                r, g, b = pixels[x, y]
                if binary_password:
                    r = (r & ~1) | int(binary_password[0])
                    binary_password = binary_password[1:]
                if binary_password:
                    g = (g & ~1) | int(binary_password[0])
                    binary_password = binary_password[1:]
                if binary_password:
                    b = (b & ~1) | int(binary_password[0])
                    binary_password = binary_password[1:]
                pixels[x, y] = (r, g, b)
        # Save the modified image to a file
        img.save(output_path)

def decrypt_password_from_image(image_path):
    """Decrypts a password from an image using the least significant bit 
technique."""
    # Open the image
    with Image.open(image_path) as img:
        # Get the pixels of the image
        pixels = img.load()
        # Extract the password from the least significant bit of each 
color channel
        binary_password = ""
        for y in range(img.size[1]):
            for x in range(img.size[0]):
                r, g, b = pixels[x, y]
                binary_password += str(r & 1)
                binary_password += str(g & 1)
                binary_password += str(b & 1)
        # Convert the binary password back to ASCII characters
        password = ""
        for i in range(0, len(binary_password), 8):
            password += chr(int(binary_password[i:i+8], 2))
            if password.endswith("\0"):
                break
        return password.rstrip("\0")

# Example usage
encrypt_password_to_image("password123", "input_image.png", 
"output_image.png")
print(decrypt_password_from_image("output_image.png"))
