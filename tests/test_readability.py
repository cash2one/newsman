import sys

def main(url):
    from readability import Readability
    r = Readability(url)
    print str(r.content)
    print str(r.title)

if __name__ == "__main__":
    main(sys.argv[1])
