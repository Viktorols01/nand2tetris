# jag ser INTE hur jag ska lösa detta utan karaktär för karaktär med peek
# men det finns ju givetvis inte... FAN
# vibe coded
class PeekableFile:
    def __init__(self, file):
        self.file = file
        self.buffer = []   # holds characters already peeked

    def peek(self, n=1):
        # ensure buffer has at least n characters
        while len(self.buffer) < n:
            ch = self.file.read(1)
            if ch == "":
                break
            self.buffer.append(ch)
        return "".join(self.buffer[:n])

    def read(self, n=1):
        out = []

        # consume from buffer first
        while n > 0 and self.buffer:
            out.append(self.buffer.pop(0))
            n -= 1

        # then read remaining from file
        if n > 0:
            chunk = self.file.read(n)
            out.append(chunk)

        return "".join(out)

    def readline(self):
        line = []

        # consume buffered chars until newline
        while self.buffer:
            ch = self.buffer.pop(0)
            line.append(ch)
            if ch == "\n":
                return "".join(line)

        # now read from file normally
        return "".join(line) + self.file.readline()
