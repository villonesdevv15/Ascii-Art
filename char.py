import random
import string

# Define symbols and special characters (no letters or numbers)
symbols = ' !@#$%^&*+-=;:,.?~`"'

# Generate a random length between 13 and 18
length = random.randint(13, 18)

# Generate random string of symbols with no repeats
def main():
    random_symbols = ''.join(random.sample(symbols, length))
    print(f"Length: {length}")
    print(f"Random symbols: {random_symbols}")

if __name__ == "__main__":
    main()