#!/usr/bin/python

import spi
from math import sqrt

a = 0.00390830
b = -0.0000005775
c = -0.00000000000418301
rtdR = 400
rtd0 = 100

# registers
REG_CONFIGURATION = 0x00
REG_RTD_MSB = 0x01
REG_RTD_LSB = 0x02
REG_HF_MSB = 0x03
REG_HF_LSB = 0x04
REG_LF_MSB = 0x05
REG_LF_LSB = 0x06
REG_FAULT_STATUS = 0x07

# configuration options
REG_CONF_50HZ_FILTER = (1 << 0)
REG_CONF_FAULT_STATUS_AUTO_CLEAR = (1 << 1)
REG_CONF_3WIRE_RTD = (1 << 4)
REG_CONF_1SHOT = (1 << 5)
REG_CONF_CONVERSION_MODE_AUTO = (1 << 6)
REG_CONF_VBIAS_ON = (1 << 7)

class max31865:

    def __init__(self, name, bus, channel, _3wire=True):
        self.serial = name
        device = "/dev/spidev%s.%s" % (bus, channel)

        spi.openSPI(speed=100000, mode=1, device=device)

        self.config = REG_CONF_VBIAS_ON | REG_CONF_50HZ_FILTER | REG_CONF_CONVERSION_MODE_AUTO
        if(_3wire):
            self.config |= REG_CONF_3WIRE_RTD

        self.__write__(REG_CONFIGURATION, self.config | REG_CONF_FAULT_STATUS_AUTO_CLEAR)
        self.__write__(REG_LF_MSB, 0x00)
        self.__write__(REG_LF_LSB, 0x00)
        self.__write__(REG_HF_MSB, 0xFF)
        self.__write__(REG_HF_LSB, 0xFF)

    def getSerial(self):
        return self.serial

    def __read__(self, address):
        assert (address >= 0 and address <= 0x07)

        return spi.transfer((address, 0))[1]

    def __write__(self, address, n):
        assert (address >= 0 and address <= 0x07)
        assert (n >= 0 and n <= 0xFF)

        spi.transfer((address | 0x80, n))

    def pullf(self):
        msb_rtd = self.__read__(REG_RTD_MSB)
        lsb_rtd = self.__read__(REG_RTD_LSB)
        rtdRaw = ((msb_rtd << 7) + ((lsb_rtd & 0xFE) >> 1))
        rtdT = (rtdRaw * rtdR) / 32768
        temp = -rtd0 * a + sqrt(rtd0 ** 2 * a ** 2 - 4 * rtd0 * b * (rtd0 - rtdT))
        temp = temp / (2 * rtd0 * b);
        return temp * 1.8 + 32;

if __name__ == "__main__":
    probe = max31865("myprobe", 0, 0)
    print probe.pullf()
