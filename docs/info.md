<!---

This file is used to generate your project datasheet. Please fill in the information below and delete any unused
sections.

You can also include images in this folder and reference them in the markdown. Each image must be less than
512 kb in size, and the combined size of all images must be less than 1 MB.
-->

## How it works

SPI Slave implementation that support all 4 SPI modes of operation.
8 Configurable (Read/Write) registers.
8 Status (Read only) registers.

## Limitations:
 - Single register access per SPI transaction.
 - SPI transaction is limited to 16 bits transfer at a time (Addr + Data). Please refer to SPI Commands for timing diagrams.
 - Design tested for 8 configuration registers + 8 status registers.
 - Even though the number of configuration registers and status registers is configurable, design only supports equal number of configuration and status registers for now.
 - Writes targeting Read Only address are dropped, i.e., no configuration registers gets updated.

Address Space:
0 - Configurable Read/Write register [0]
1 - Configurable Read/Write register [1]
2 - Configurable Read/Write register [2]
3 - Configurable Read/Write register [3]
4 - Configurable Read/Write register [4]
5 - Configurable Read/Write register [5]
6 - Configurable Read/Write register [6]
7 - Configurable Read/Write register [7]
8 - Status Read Only register [0]
9 - Status Read Only register [1]
10 - Status Read Only register [2]
11 - Status Read Only register [3]
12 - Status Read Only register [4]
13 - Status Read Only register [5]
14 - Status Read Only register [6]
15 - Status Read Only register [7]

## Connection

MCU <--SPI--> SPI_WRAPPER <--regaccess--> User logic

* SPI: MOSI MISO SCLK CS
* regaccess: config_regs (used to drive/control user logic), status_regs (used to read/monitor user logic)

## Protocol

### SPI settings

* Address Bits = 4 and Databits = 8, MSB First
* Tested SPI frequency: spi_clk <= clk / 20

### SPI commands

* Write data
cmd = 0x80+addr, addr = 0 ~ 7

```txt
    Bit:  | <15>      <14>         <13>         <12>        <11>     <10>       <9>       <8>       <7>       <6>       <5>       <4>       <3>       <2>       <1>       <0>   |
    MOSI: |   1  | Don't Care | Don't Care | Don't Care | addr[3] | addr[2] | addr[1] | addr[0] | data[7] | data[6] | data[5] | data[4] | data[3] | data[2] | data[1] | data[0] |
    MISO: |   0  |      0     |      0     |      0     |    0    |    0    |    0    |    0    |    0    |    0    |    0    |    0    |    0    |    0    |    0    |    0    |
```

* Read data
cmd = 0x00+addr, addr = 0 ~ 15

```txt
    Bit:  | <15>      <14>         <13>         <12>       <11>       <10>      <9>       <8>           <7>             <6>             <5>             <4>             <3>             <2>             <1>             <0>     |
    MOSI: |   0  | Don't Care | Don't Care | Don't Care | addr[3] | addr[2] | addr[1] | addr[0] |   Don't Care  |   Don't Care  |   Don't Care  |   Don't Care  |   Don't Care  |   Don't Care  |   Don't Care  |   Don't Care  |
    MISO: |   0  |      0     |      0     |      0     |   0     |    0    |    0    |    0    | data[addr][7] | data[addr][6] | data[addr][5] | data[addr][4] | data[addr][3] | data[addr][2] | data[addr][1] | data[addr][0] |
```


## How to test

Use SPI Master peripheral in RP2040 to start communication on SPI interface towards this design. Remember to configure the SPI mode using the switches in DIP switch and configure the SPI mode in the RP2040 accordingly.

## External hardware

Not required.
