# Password Image Encryptor
This Python script provides functions for encrypting a password into an image and decrypting a password from an image. It uses the least significant bit technique to modify the color channels of the image pixels and embed the password.

## Installation 
To use this script, you'll need to have Python 3 and the Pillow library installed. You can install Pillow using pip:

```
pip install pillow
```

## Usage
### Encrypting a Password into an Image
To encrypt a password into an image, you can use the encrypt_password_to_image function:

```
from password_image_encryption import encrypt_password_to_image

# Encrypt the password "mysecretpassword" into the image file "input_image.png" and save the result to "output_image.png"
encrypt_password_to_image("mysecretpassword", "input_image.png", "output_image.png")
```
This function takes three arguments:

password: The password string to encrypt.
image_path: The path to the input image file.
output_path: The path to the output image file, which will contain the encrypted password.

### Decrypt a Password from an Image
To decrypt a password from an image, you can use the decrypt_password_from_image function:

```
from password_image_encryption import decrypt_password_from_image

# Decrypt the password from the image file "output_image.png"
password = decrypt_password_from_image("output_image.png")
print(password)
```

This function takes one argument:

image_path: The path to the image file containing the encrypted password.
The function returns the decrypted password as a string.

## Limitations
This script uses the least significant bit technique to embed the password into the image pixels, which means that the encrypted password may be visible if the image is viewed at high magnification or if the image is compressed. Additionally, the script assumes that the input image is in the RGB color space, and it may not work correctly with images in other color spaces.
