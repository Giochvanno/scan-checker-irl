text = "═хшчтхёЄэюх ьхёЄюяюыюцхэ"

# Попробуйте декодировать в разные кодировки
try:
    decoded_text = text.encode('windows-1251').decode('utf-8')
    print("Decoded text (windows-1251 to utf-8):", decoded_text)
except UnicodeDecodeError as e:
    print("Error in decoding:", e)

