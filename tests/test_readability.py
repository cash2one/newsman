import sys

def main(url):
    from simplr import Readability
    r = Readability(url)
    print str(r.content)

if __name__ == "__main__":
    main(sys.argv[1])
