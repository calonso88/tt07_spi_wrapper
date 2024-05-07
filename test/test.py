# SPDX-FileCopyrightText: © 2024 Tiny Tapeout
# SPDX-License-Identifier: MIT

import random

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles

def get_bit(value, bit_index):
  temp = value & (1 << bit_index)
  return temp

def set_bit(value, bit_index):
  temp = value | (1 << bit_index)
  return temp

def clear_bit(value, bit_index):
  temp = value & ~(1 << bit_index)
  return temp

def xor_bit(value, bit_index):
  temp = value ^ (1 << bit_index)
  return temp

def pull_cs_high(value):
  temp = set_bit(value, 0)
  return temp

def pull_cs_low(value):
  temp = clear_bit(value, 0)
  return temp

def spi_clk_high(value):
  temp = set_bit(value, 1)
  return temp

def spi_clk_low(value):
  temp = clear_bit(value, 1)
  return temp

def spi_clk_invert(value):
  temp = xor_bit(value, 1)
  return temp

def spi_mosi_high(value):
  temp = set_bit(value, 2)
  return temp

def spi_mosi_low(value):
  temp = clear_bit(value, 2)
  return temp

def spi_miso_read(port):
  return (get_bit (port.value, 3) >> 3)

async def spi_write (clk, port, address, data):

  temp = port.value;
  result = pull_cs_high(temp)
  port.value = result
  await ClockCycles(clk, 10)
  temp = port.value;
  result = pull_cs_low(temp)
  port.value = result
  await ClockCycles(clk, 10)
  
  # Write command bit - bit 7 - MSBIT in first byte
  temp = port.value;
  result = spi_clk_invert(temp)
  result2 = spi_mosi_high(result)
  port.value = result2
  await ClockCycles(clk, 10)
  temp = port.value;
  result = spi_clk_invert(temp)
  port.value = result
  await ClockCycles(clk, 10)
  
  iterator = 0
  while iterator < 4:
    # Don't care - bit 6, bit 5, bit 4 and bit 3
    temp = port.value;
    result = spi_clk_invert(temp)
    result2 = spi_mosi_low(result)
    port.value = result2
    await ClockCycles(clk, 10)
    temp = port.value;
    result = spi_clk_invert(temp)
    port.value = result
    await ClockCycles(clk, 10)
    iterator += 1

  iterator = 2
  while iterator >= 0:
    # Address[iterator] - bit 2, bit 1 and bit 0
    temp = port.value;
    result = spi_clk_invert(temp)
    address_bit = get_bit(address, iterator)
    if (address_bit == 0):
      result2 = spi_mosi_low(result)
    else:
      result2 = spi_mosi_high(result)
    port.value = result2
    await ClockCycles(clk, 10)
    temp = port.value;
    result = spi_clk_invert(temp)
    port.value = result
    await ClockCycles(clk, 10)
    iterator -= 1

  iterator = 7
  while iterator >= 0:
    # Data[iterator]
    temp = port.value;
    result = spi_clk_invert(temp)
    data_bit = get_bit(data, iterator)
    if (data_bit == 0):
      result2 = spi_mosi_low(result)
    else:
      result2 = spi_mosi_high(result)
    port.value = result2
    await ClockCycles(clk, 10)
    temp = port.value;
    result = spi_clk_invert(temp)
    port.value = result
    await ClockCycles(clk, 10)
    iterator -= 1

  temp = port.value;
  result = pull_cs_high(temp)
  port.value = result
  await ClockCycles(clk, 10)  


async def spi_read (clk, port_in, port_out, address, data):
  
  temp = port_in.value;
  result = pull_cs_high(temp)
  port_in.value = result
  await ClockCycles(clk, 10)
  temp = port_in.value;
  result = pull_cs_low(temp)
  port_in.value = result
  await ClockCycles(clk, 10)
  
  # Read command bit - bit 7 - MSBIT in first byte
  temp = port_in.value;
  result = spi_clk_invert(temp)
  result2 = spi_mosi_low(result)
  port_in.value = result2
  await ClockCycles(clk, 10)
  temp = port_in.value;
  result = spi_clk_invert(temp)
  port_in.value = result
  await ClockCycles(clk, 10)
  
  iterator = 0
  while iterator < 4:
    # Don't care - bit 6, bit 5, bit 4 and bit 3
    temp = port_in.value;
    result = spi_clk_invert(temp)
    result2 = spi_mosi_low(result)
    port_in.value = result2
    await ClockCycles(clk, 10)
    temp = port_in.value;
    result = spi_clk_invert(temp)
    port_in.value = result
    await ClockCycles(clk, 10)
    iterator += 1
  
  iterator = 2
  while iterator >= 0:
    # Address[iterator] - bit 2, bit 1 and bit 0
    temp = port_in.value;
    result = spi_clk_invert(temp)
    address_bit = get_bit(address, iterator)
    if (address_bit == 0):
      result2 = spi_mosi_low(result)
    else:
      result2 = spi_mosi_high(result)
    port_in.value = result2
    await ClockCycles(clk, 10)
    temp = port_in.value;
    result = spi_clk_invert(temp)
    port_in.value = result
    await ClockCycles(clk, 10)
    iterator -= 1

  miso_byte = 0
  miso_bit = 0

  iterator = 7
  while iterator >= 0:
    # Data[iterator]
    temp = port_in.value;
    result = spi_clk_invert(temp)
    data_bit = get_bit(data, iterator)
    if (data_bit == 0):
      result2 = spi_mosi_low(result)
    else:
      result2 = spi_mosi_high(result)
    port_in.value = result2
    await ClockCycles(clk, 10)
    miso_bit = spi_miso_read(port_out)
    miso_byte = miso_byte | (miso_bit << iterator)
    temp = port_in.value;
    result = spi_clk_invert(temp)
    port_in.value = result
    await ClockCycles(clk, 10)
    iterator -= 1

  temp = port_in.value;
  result = pull_cs_high(temp)
  port_in.value = result
  await ClockCycles(clk, 10)

  return miso_byte


async def spi_write_cpha0 (clk, port, address, data):

  temp = port.value;
  result = pull_cs_high(temp)
  port.value = result
  await ClockCycles(clk, 10)

  # Pull CS low + Write command bit - bit 7 - MSBIT in first byte
  temp = port.value;
  result = pull_cs_low(temp)
  result2 = spi_mosi_high(result)
  port.value = result2
  await ClockCycles(clk, 10)
  temp = port.value;
  result = spi_clk_invert(temp)
  port.value = result
  await ClockCycles(clk, 10)
  
  iterator = 0
  while iterator < 4:
    # Don't care - bit 6, bit 5, bit 4 and bit 3
    temp = port.value;
    result = spi_clk_invert(temp)
    result2 = spi_mosi_low(result)
    port.value = result2
    await ClockCycles(clk, 10)
    temp = port.value;
    result = spi_clk_invert(temp)
    port.value = result
    await ClockCycles(clk, 10)
    iterator += 1

  iterator = 2
  while iterator >= 0:
    # Address[iterator] - bit 2, bit 1 and bit 0
    temp = port.value;
    result = spi_clk_invert(temp)
    address_bit = get_bit(address, iterator)
    if (address_bit == 0):
      result2 = spi_mosi_low(result)
    else:
      result2 = spi_mosi_high(result)
    port.value = result2
    await ClockCycles(clk, 10)
    temp = port.value;
    result = spi_clk_invert(temp)
    port.value = result
    await ClockCycles(clk, 10)
    iterator -= 1

  iterator = 7
  while iterator >= 0:
    # Data[iterator]
    temp = port.value;
    result = spi_clk_invert(temp)
    data_bit = get_bit(data, iterator)
    if (data_bit == 0):
      result2 = spi_mosi_low(result)
    else:
      result2 = spi_mosi_high(result)
    port.value = result2
    await ClockCycles(clk, 10)
    temp = port.value;
    result = spi_clk_invert(temp)
    port.value = result
    await ClockCycles(clk, 10)
    iterator -= 1

  temp = port.value;
  result = pull_cs_high(temp)
  port.value = result
  await ClockCycles(clk, 10)  


async def spi_read_cpha0 (clk, port_in, port_out, address, data):
  
  temp = port_in.value;
  result = pull_cs_high(temp)
  port_in.value = result
  await ClockCycles(clk, 10)
  
  # Pull CS low + Read command bit - bit 7 - MSBIT in first byte
  temp = port_in.value;
  result = pull_cs_low(temp)
  result2 = spi_mosi_low(result)
  port_in.value = result2
  await ClockCycles(clk, 10)
  temp = port_in.value;
  result = spi_clk_invert(temp)
  port_in.value = result
  await ClockCycles(clk, 10)
    
  iterator = 0
  while iterator < 4:
    # Don't care - bit 6, bit 5, bit 4 and bit 3
    temp = port_in.value;
    result = spi_clk_invert(temp)
    result2 = spi_mosi_low(result)
    port_in.value = result2
    await ClockCycles(clk, 10)
    temp = port_in.value;
    result = spi_clk_invert(temp)
    port_in.value = result
    await ClockCycles(clk, 10)
    iterator += 1
  
  iterator = 2
  while iterator >= 0:
    # Address[iterator] - bit 2, bit 1 and bit 0
    temp = port_in.value;
    result = spi_clk_invert(temp)
    address_bit = get_bit(address, iterator)
    if (address_bit == 0):
      result2 = spi_mosi_low(result)
    else:
      result2 = spi_mosi_high(result)
    port_in.value = result2
    await ClockCycles(clk, 10)
    temp = port_in.value;
    result = spi_clk_invert(temp)
    port_in.value = result
    await ClockCycles(clk, 10)
    iterator -= 1

  miso_byte = 0
  miso_bit = 0

  iterator = 7
  while iterator >= 0:
    # Data[iterator]
    temp = port_in.value;
    result = spi_clk_invert(temp)
    data_bit = get_bit(data, iterator)
    if (data_bit == 0):
      result2 = spi_mosi_low(result)
    else:
      result2 = spi_mosi_high(result)
    port_in.value = result2
    await ClockCycles(clk, 10)
    miso_bit = spi_miso_read(port_out)
    miso_byte = miso_byte | (miso_bit << iterator)
    temp = port_in.value;
    result = spi_clk_invert(temp)
    port_in.value = result
    await ClockCycles(clk, 10)
    iterator -= 1

  temp = port_in.value;
  result = pull_cs_high(temp)
  port_in.value = result
  await ClockCycles(clk, 10)

  return miso_byte


@cocotb.test()
async def test_project(dut):
    dut._log.info("Start")

    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units="us")
    cocotb.start_soon(clock.start())

    # Reset
    dut._log.info("Reset")
    dut.ena.value = 1
    dut.ui_in.value = 0
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    dut._log.info("Test project behavior")

    # Wait for some time
    await ClockCycles(dut.clk, 10)
    await ClockCycles(dut.clk, 10)

    # Config CPOL and CPHA
    CPOL = 0
    CPHA = 1
    dut.ui_in.value = ((CPHA << 4) + (CPOL << 3))

    # CPOL = 0, SPI_CLK low in idle
    temp = dut.ui_in.value;
    result = spi_clk_low(temp)
    dut.ui_in.value.value = result
  
    # Wait for some time
    await ClockCycles(dut.clk, 10)
    await ClockCycles(dut.clk, 10)

    # ITERATIONS 
    iterations = 0
  
    while iterations < 10:
        data0 = random.randint(0x00, 0xFF)
        data1 = random.randint(0x00, 0xFF)
        data2 = random.randint(0x00, 0xFF)
        data3 = random.randint(0x00, 0xFF)
        data4 = random.randint(0x00, 0xFF)
        data5 = random.randint(0x00, 0xFF)
        data6 = random.randint(0x00, 0xFF)
        data7 = random.randint(0x00, 0xFF)
        
        # Write reg[0] = 0xF0
        await spi_write (dut.clk, dut.ui_in, 0, data0)
        # Write reg[1] = 0xDE
        await spi_write (dut.clk, dut.ui_in, 1, data1)
        # Write reg[2] = 0xAD
        await spi_write (dut.clk, dut.ui_in, 2, data2)
        # Write reg[3] = 0xBE
        await spi_write (dut.clk, dut.ui_in, 3, data3)
        # Write reg[4] = 0xEF
        await spi_write (dut.clk, dut.ui_in, 4, data4)
        # Write reg[5] = 0x55
        await spi_write (dut.clk, dut.ui_in, 5, data5)
        # Write reg[6] = 0xAA
        await spi_write (dut.clk, dut.ui_in, 6, data6)
        # Write reg[7] = 0x0F
        await spi_write (dut.clk, dut.ui_in, 7, data7)
      
        # Read reg[0]
        reg0 = await spi_read (dut.clk, dut.ui_in, dut.uo_out, 0, 0x00)
        # Read reg[1]
        reg1 = await spi_read (dut.clk, dut.ui_in, dut.uo_out, 1, 0x00)
        # Read reg[2]
        reg2 = await spi_read (dut.clk, dut.ui_in, dut.uo_out, 2, 0x00)
        # Read reg[3]
        reg3 = await spi_read (dut.clk, dut.ui_in, dut.uo_out, 3, 0x00)
        # Read reg[4]
        reg4 = await spi_read (dut.clk, dut.ui_in, dut.uo_out, 4, 0x00)
        # Read reg[5]
        reg5 = await spi_read (dut.clk, dut.ui_in, dut.uo_out, 5, 0x00)
        # Read reg[6]
        reg6 = await spi_read (dut.clk, dut.ui_in, dut.uo_out, 6, 0x00)
        # Read reg[7]
        reg7 = await spi_read (dut.clk, dut.ui_in, dut.uo_out, 7, 0x00)
    
        # Wait for some time
        await ClockCycles(dut.clk, 10)
        await ClockCycles(dut.clk, 10)
    
        assert reg0 == data0
        assert reg1 == data1
        assert reg2 == data2
        assert reg3 == data3
        assert reg4 == data4
        assert reg5 == data5
        assert reg6 == data6
        assert reg7 == data7

        iterations = iterations + 1


    # Wait for some time
    await ClockCycles(dut.clk, 10)
    await ClockCycles(dut.clk, 10)

    # Config CPOL and CPHA
    CPOL = 1
    CPHA = 1
    dut.ui_in.value = ((CPHA << 4) + (CPOL << 3))

    # CPOL = 0, SPI_CLK low in idle
    temp = dut.ui_in.value;
    result = spi_clk_high(temp)
    dut.ui_in.value.value = result
  
    # Wait for some time
    await ClockCycles(dut.clk, 10)
    await ClockCycles(dut.clk, 10)

    # ITERATIONS 
    iterations = 0
  
    while iterations < 10:
        data0 = random.randint(0x00, 0xFF)
        data1 = random.randint(0x00, 0xFF)
        data2 = random.randint(0x00, 0xFF)
        data3 = random.randint(0x00, 0xFF)
        data4 = random.randint(0x00, 0xFF)
        data5 = random.randint(0x00, 0xFF)
        data6 = random.randint(0x00, 0xFF)
        data7 = random.randint(0x00, 0xFF)
        
        # Write reg[0] = 0xF0
        await spi_write (dut.clk, dut.ui_in, 0, data0)
        # Write reg[1] = 0xDE
        await spi_write (dut.clk, dut.ui_in, 1, data1)
        # Write reg[2] = 0xAD
        await spi_write (dut.clk, dut.ui_in, 2, data2)
        # Write reg[3] = 0xBE
        await spi_write (dut.clk, dut.ui_in, 3, data3)
        # Write reg[4] = 0xEF
        await spi_write (dut.clk, dut.ui_in, 4, data4)
        # Write reg[5] = 0x55
        await spi_write (dut.clk, dut.ui_in, 5, data5)
        # Write reg[6] = 0xAA
        await spi_write (dut.clk, dut.ui_in, 6, data6)
        # Write reg[7] = 0x0F
        await spi_write (dut.clk, dut.ui_in, 7, data7)
      
        # Read reg[0]
        reg0 = await spi_read (dut.clk, dut.ui_in, dut.uo_out, 0, 0x00)
        # Read reg[1]
        reg1 = await spi_read (dut.clk, dut.ui_in, dut.uo_out, 1, 0x00)
        # Read reg[2]
        reg2 = await spi_read (dut.clk, dut.ui_in, dut.uo_out, 2, 0x00)
        # Read reg[3]
        reg3 = await spi_read (dut.clk, dut.ui_in, dut.uo_out, 3, 0x00)
        # Read reg[4]
        reg4 = await spi_read (dut.clk, dut.ui_in, dut.uo_out, 4, 0x00)
        # Read reg[5]
        reg5 = await spi_read (dut.clk, dut.ui_in, dut.uo_out, 5, 0x00)
        # Read reg[6]
        reg6 = await spi_read (dut.clk, dut.ui_in, dut.uo_out, 6, 0x00)
        # Read reg[7]
        reg7 = await spi_read (dut.clk, dut.ui_in, dut.uo_out, 7, 0x00)
    
        # Wait for some time
        await ClockCycles(dut.clk, 10)
        await ClockCycles(dut.clk, 10)
    
        assert reg0 == data0
        assert reg1 == data1
        assert reg2 == data2
        assert reg3 == data3
        assert reg4 == data4
        assert reg5 == data5
        assert reg6 == data6
        assert reg7 == data7

        iterations = iterations + 1
  

    # Wait for some time
    await ClockCycles(dut.clk, 10)
    await ClockCycles(dut.clk, 10)
  
    # Config CPOL and CPHA
    CPOL = 0
    CPHA = 0
    dut.ui_in.value = ((CPHA << 4) + (CPOL << 3))

    # CPOL = 0, SPI_CLK low in idle
    temp = dut.ui_in.value;
    result = spi_clk_low(temp)
    dut.ui_in.value.value = result
  
    # Wait for some time
    await ClockCycles(dut.clk, 10)
    await ClockCycles(dut.clk, 10)

    # ITERATIONS 
    iterations = 0
  
    while iterations < 10:
        data0 = random.randint(0x00, 0xFF)
        data1 = random.randint(0x00, 0xFF)
        data2 = random.randint(0x00, 0xFF)
        data3 = random.randint(0x00, 0xFF)
        data4 = random.randint(0x00, 0xFF)
        data5 = random.randint(0x00, 0xFF)
        data6 = random.randint(0x00, 0xFF)
        data7 = random.randint(0x00, 0xFF)
        
        # Write reg[0] = 0xF0
        await spi_write_cpha0 (dut.clk, dut.ui_in, 0, data0)
        # Write reg[1] = 0xDE
        await spi_write_cpha0 (dut.clk, dut.ui_in, 1, data1)
        # Write reg[2] = 0xAD
        await spi_write_cpha0 (dut.clk, dut.ui_in, 2, data2)
        # Write reg[3] = 0xBE
        await spi_write_cpha0 (dut.clk, dut.ui_in, 3, data3)
        # Write reg[4] = 0xEF
        await spi_write_cpha0 (dut.clk, dut.ui_in, 4, data4)
        # Write reg[5] = 0x55
        await spi_write_cpha0 (dut.clk, dut.ui_in, 5, data5)
        # Write reg[6] = 0xAA
        await spi_write_cpha0 (dut.clk, dut.ui_in, 6, data6)
        # Write reg[7] = 0x0F
        await spi_write_cpha0 (dut.clk, dut.ui_in, 7, data7)
      
        # Read reg[0]
        reg0 = await spi_read_cpha0 (dut.clk, dut.ui_in, dut.uo_out, 0, 0x00)
        # Read reg[1]
        reg1 = await spi_read_cpha0 (dut.clk, dut.ui_in, dut.uo_out, 1, 0x00)
        # Read reg[2]
        reg2 = await spi_read_cpha0 (dut.clk, dut.ui_in, dut.uo_out, 2, 0x00)
        # Read reg[3]
        reg3 = await spi_read_cpha0 (dut.clk, dut.ui_in, dut.uo_out, 3, 0x00)
        # Read reg[4]
        reg4 = await spi_read_cpha0 (dut.clk, dut.ui_in, dut.uo_out, 4, 0x00)
        # Read reg[5]
        reg5 = await spi_read_cpha0 (dut.clk, dut.ui_in, dut.uo_out, 5, 0x00)
        # Read reg[6]
        reg6 = await spi_read_cpha0 (dut.clk, dut.ui_in, dut.uo_out, 6, 0x00)
        # Read reg[7]
        reg7 = await spi_read_cpha0 (dut.clk, dut.ui_in, dut.uo_out, 7, 0x00)
    
        await ClockCycles(dut.clk, 10)
    
        assert reg0 == data0
        assert reg1 == data1
        assert reg2 == data2
        assert reg3 == data3
        assert reg4 == data4
        assert reg5 == data5
        assert reg6 == data6
        assert reg7 == data7

        iterations = iterations + 1


    # Wait for some time
    await ClockCycles(dut.clk, 10)
    await ClockCycles(dut.clk, 10)

    # Config CPOL and CPHA
    CPOL = 1
    CPHA = 0
    dut.ui_in.value = ((CPHA << 4) + (CPOL << 3))

    # CPOL = 0, SPI_CLK low in idle
    temp = dut.ui_in.value;
    result = spi_clk_high(temp)
    dut.ui_in.value.value = result
  
    # Wait for some time
    await ClockCycles(dut.clk, 10)
    await ClockCycles(dut.clk, 10)

    # ITERATIONS 
    iterations = 0
  
    while iterations < 10:
        data0 = random.randint(0x00, 0xFF)
        data1 = random.randint(0x00, 0xFF)
        data2 = random.randint(0x00, 0xFF)
        data3 = random.randint(0x00, 0xFF)
        data4 = random.randint(0x00, 0xFF)
        data5 = random.randint(0x00, 0xFF)
        data6 = random.randint(0x00, 0xFF)
        data7 = random.randint(0x00, 0xFF)
        
        # Write reg[0] = 0xF0
        await spi_write_cpha0 (dut.clk, dut.ui_in, 0, data0)
        # Write reg[1] = 0xDE
        await spi_write_cpha0 (dut.clk, dut.ui_in, 1, data1)
        # Write reg[2] = 0xAD
        await spi_write_cpha0 (dut.clk, dut.ui_in, 2, data2)
        # Write reg[3] = 0xBE
        await spi_write_cpha0 (dut.clk, dut.ui_in, 3, data3)
        # Write reg[4] = 0xEF
        await spi_write_cpha0 (dut.clk, dut.ui_in, 4, data4)
        # Write reg[5] = 0x55
        await spi_write_cpha0 (dut.clk, dut.ui_in, 5, data5)
        # Write reg[6] = 0xAA
        await spi_write_cpha0 (dut.clk, dut.ui_in, 6, data6)
        # Write reg[7] = 0x0F
        await spi_write_cpha0 (dut.clk, dut.ui_in, 7, data7)
      
        # Read reg[0]
        reg0 = await spi_read_cpha0 (dut.clk, dut.ui_in, dut.uo_out, 0, 0x00)
        # Read reg[1]
        reg1 = await spi_read_cpha0 (dut.clk, dut.ui_in, dut.uo_out, 1, 0x00)
        # Read reg[2]
        reg2 = await spi_read_cpha0 (dut.clk, dut.ui_in, dut.uo_out, 2, 0x00)
        # Read reg[3]
        reg3 = await spi_read_cpha0 (dut.clk, dut.ui_in, dut.uo_out, 3, 0x00)
        # Read reg[4]
        reg4 = await spi_read_cpha0 (dut.clk, dut.ui_in, dut.uo_out, 4, 0x00)
        # Read reg[5]
        reg5 = await spi_read_cpha0 (dut.clk, dut.ui_in, dut.uo_out, 5, 0x00)
        # Read reg[6]
        reg6 = await spi_read_cpha0 (dut.clk, dut.ui_in, dut.uo_out, 6, 0x00)
        # Read reg[7]
        reg7 = await spi_read_cpha0 (dut.clk, dut.ui_in, dut.uo_out, 7, 0x00)

        # Wait for some time
        await ClockCycles(dut.clk, 10)
        await ClockCycles(dut.clk, 10)

        assert reg0 == data0
        assert reg1 == data1
        assert reg2 == data2
        assert reg3 == data3
        assert reg4 == data4
        assert reg5 == data5
        assert reg6 == data6
        assert reg7 == data7

        iterations = iterations + 1

    # Wait for some time
    await ClockCycles(dut.clk, 10)
    await ClockCycles(dut.clk, 10)
