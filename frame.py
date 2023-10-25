import os
import buffers

def EbitConversion(size):
    binary = ""
    divisor = 128
    while (divisor > 0):
        if (size - divisor > -1):
            size = size - divisor
            binary += "1"
        else:
            binary += "0"
        divisor = divisor//2
    return binary

def convertBack(size):
    total = 0
    convert = 128
    if (size == 0):
        return size
    for character in size:
        if (character == "1"):
            total += convert
        convert = convert//2
    return total

def framer(sd, files):                          #takes a socket descriptor and list of filenames to send
    buffWtr = buffer.BufferedFdWriter(sd)
    for target in files:
        #opening file to read with file descriptor
        fd = os.open(target, os.O_RDONLY)
        #creating instances of buffered reader and writer
        buffRdr = buffer.BufferedFdReader(fd)

        
        #writing size of filename
        fileNameSize = EbitConversion(len(target)).encode()
        for byte in fileNameSize:
            buffWtr.writeByte(byte)
        
        #converting file name to a byte array and writing it to fd
        fileName = target.encode()
        for byte in fileName:
            buffWtr.writeByte(byte)

        #Finding size of file, representing in binary and writing it to fd
        targetFileSize = EbitConversion(os.path.getsize(target)).encode()
        for byte in targetFileSize:
            buffWtr.writeByte(byte)

        #create buffered reader to moderate reading, same for writing
        
        #Now that fileNameSize, fileName, and targetFileSize are written into buffer, we can just copy over file contents with Copy
        bufferedCopy(buffRdr, buffWtr)  

        #Repeat the process for the rest of the files

    buffWtr.flush()


def deframer(sd):                                               #takes socket descriptor
    while(True):
        nameSize = convertBack(os.read(sd, 8).decode())
        if(nameSize == 0):                                      
            return 0                                            #returns 0 on zero read (end of connection)
        fileName = os.read(sd, nameSize).decode()
        #Not going to use buffered reader here because I know file name can only be up to 256 bytes max, and the 8 before I know are there

        #fd for target file
        fileName = os.open(fileName, os.O_WRONLY)
            

        fileSize = convertBack(os.read(sd, 8).decode())

        bytesRead = 0
        buffRdr = buffer.BufferedFdReader(sd)          #reading from connection
        buffWtr = buffer.BufferedFdWriter(fileName)    #writing to "new" file
        while (bytesRead < fileSize ):
            byte = buffRdr.readByte()
            buffWtr.writeByte(byte)
            bytesRead += 1
        buffWtr.flush()                 



def frame(command, sd):         #command refers to either c or x and sd refers to socket descriptor
    files = []
    files.append("foo.txt")
    if (command == "c"):
        framer(sd, files)
    elif (command == "x"):
        deframer(sd)
    
    exit()
