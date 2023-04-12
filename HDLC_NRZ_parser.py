import sys
import libscrc


FLAG_BIN = '01111110'
FLAG_TXT = '[FLAG]'
FFFFFF_TXT = '[FFFFF...]'
Time = 0
RxD = 1
RxC = 2
CTS = 3

HDLC_data = []
line = ''
last_string = ''
num_last_string = 1

def return_char (t):
    c = int(t,16)
    if 127 < c  or c < 32:
        c = ord('.')
    return (chr(c))

  
def HDLC_conversion (temp):
    if temp:
        if '0' in temp:
            temp = temp.replace('111110', '11111')
            lst = []
            for j in range (len(temp) // 8):
                lst.append('{0:0{1}X}'.format(int(temp[7::-1],2),2))
                temp = temp[8:]
            HDLC_data.append(lst)
        else:
            HDLC_data.append(FFFFFF_TXT)
    else:
        HDLC_data.append(FLAG_TXT)


# Input file was created by SALEAE
# HDLC_NRZ_parser.py v35_cisco.txt
if len(sys.argv)<2 or len(sys.argv)>2:
    print ("Usage:\n ", sys.argv[0], "filename")
    sys.exit(0);

infile = sys.argv[1]

with open (infile) as f:
    data = [(s.rstrip('\n')).replace(' ', '').split(',') for s in f]

for i in range (1, len(data)):
    if (data[i][RxC] == '1' and data[i - 1][RxC] != '1'):
        line += data[i][RxD]

while True:
    if FLAG_BIN in line:
        ind = line.index(FLAG_BIN)
        HDLC_conversion(line[:ind])
        line = line[ind + 8:]
    else:
        HDLC_conversion(line)
        break

for txt in HDLC_data:
    if FLAG_TXT in txt or FFFFFF_TXT in txt:
        if  last_string == txt:
            num_last_string += 1
        elif num_last_string > 1:
            print(txt, '=', num_last_string, '\n' + '-' * 52)
            num_last_string = 1
        last_string = txt
    else:
        hldc_crc = (''.join(txt[:-3:-1]))
        for_crc = (''.join(txt[:-2]))
        crc16x25 = libscrc.x25(bytes.fromhex(for_crc))
        while txt:
            l_col = ''
            r_col = ''
            for i in range (16):
                if txt:
                    l_col += txt[0]
                    r_col += return_char(txt.pop(0))
                else:
                    l_col += '  '
                    r_col += '  '
            print(l_col, '|', r_col)


        last_string = ''
        if (int.from_bytes(bytes.fromhex(hldc_crc), byteorder='big')) == crc16x25:
            print ('CRC OK\n' + '-' * 52)
        else:
            print('CRC ERROR','crc16x25 =', hex(crc16x25), 'hldc_crc =', hldc_crc)
