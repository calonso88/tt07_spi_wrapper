# SPDX-FileCopyrightText: © 2024 Tiny Tapeout
# SPDX-License-Identifier: MIT

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

def pull_cs_high(port):
  temp = set_bit(port.value, 0)
  port.value = temp

def pull_cs_low(port):
  temp = clear_bit(port.value, 0)
  port.value = temp

def spi_clk_high(port):
  temp = set_bit(port.value, 1)
  port.value = temp

def spi_clk_low(port):
  temp = clear_bit(port.value, 1)
  port.value = temp

def spi_mosi_high(port):
  temp = set_bit(port.value, 2)
  port.value = temp

def spi_mosi_low(port):
  temp = clear_bit(port.value, 2)
  port.value = temp

def spi_miso_read(port):
  return (get_bit (port.value, 3) >> 3)

async def spi_write (clk, port, address, data):
  
  await ClockCycles(clk, 10)
  pull_cs_high(port)
  await ClockCycles(clk, 10)
  pull_cs_low(port)
  await ClockCycles(clk, 10)
  
  # Write command bit - bit 7 - MSBIT in first byte
  spi_mosi_high(port)
  await ClockCycles(clk, 10)
  spi_clk_high(port)
  await ClockCycles(clk, 10)
  spi_clk_low(port)
  
  iterator = 0
  while iterator < 4:
    # Don't care - bit 6, bit 5, bit 4 and bit 3
    await ClockCycles(clk, 10)
    spi_mosi_low(port)
    await ClockCycles(clk, 10)
    spi_clk_high(port)
    await ClockCycles(clk, 10)
    spi_clk_low(port)
    iterator += 1

  iterator = 2
  while iterator >= 0:
    # Address[iterator] - bit 2, bit 1 and bit 0
    await ClockCycles(clk, 10)
    address_bit = get_bit(address, iterator)
    if (address_bit == 0):
      spi_mosi_low(port)
    else:
      spi_mosi_high(port)
    await ClockCycles(clk, 10)
    spi_clk_high(port)
    await ClockCycles(clk, 10)
    spi_clk_low(port)
    iterator -= 1

  iterator = 7
  while iterator >= 0:
    # Data[iterator]
    await ClockCycles(clk, 10)
    data_bit = get_bit(data, iterator)
    if (data_bit == 0):
      spi_mosi_low(port)
    else:
      spi_mosi_high(port)
    await ClockCycles(clk, 10)
    spi_clk_high(port)
    await ClockCycles(clk, 10)
    spi_clk_low(port)
    iterator -= 1

  await ClockCycles(clk, 10)
  pull_cs_high(port)
  await ClockCycles(clk, 10)  


async def spi_read (clk, port_in, port_out, address, data):
  
  await ClockCycles(clk, 10)
  pull_cs_high(port_in)
  await ClockCycles(clk, 10)
  pull_cs_low(port_in)
  await ClockCycles(clk, 10)
  
  # Read command bit - bit 7 - MSBIT in first byte
  spi_mosi_low(port_in)
  await ClockCycles(clk, 10)
  spi_clk_high(port_in)
  await ClockCycles(clk, 10)
  spi_clk_low(port_in)

  iterator = 0
  while iterator < 4:
    # Don't care - bit 6, bit 5, bit 4 and bit 3
    await ClockCycles(clk, 10)
    spi_mosi_low(port_in)
    await ClockCycles(clk, 10)
    spi_clk_high(port_in)
    await ClockCycles(clk, 10)
    spi_clk_low(port_in)
    iterator += 1
  
  iterator = 2
  while iterator >= 0:
    # Address[iterator] - bit 2, bit 1 and bit 0
    await ClockCycles(clk, 10)
    address_bit = get_bit(address, iterator)
    if (address_bit == 0):
      spi_mosi_low(port_in)
    else:
      spi_mosi_high(port_in)
    await ClockCycles(clk, 10)
    spi_clk_high(port_in)
    await ClockCycles(clk, 10)
    spi_clk_low(port_in)
    iterator -= 1

  miso_byte = 0
  miso_bit = 0

  iterator = 7
  while iterator >= 0:
    # Data[iterator]
    await ClockCycles(clk, 10)
    data_bit = get_bit(data, iterator)
    if (data_bit == 0):
      spi_mosi_low(port_in)
    else:
      spi_mosi_high(port_in)
    await ClockCycles(clk, 10)
    spi_clk_high(port_in)
    miso_bit = spi_miso_read(port_out)
    miso_byte = miso_byte | (miso_bit << iterator)
    await ClockCycles(clk, 10)
    spi_clk_low(port_in)
    iterator -= 1

  await ClockCycles(clk, 10)
  pull_cs_high(port_in)
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

    # Wait for one clock cycle to see the output values
    await ClockCycles(dut.clk, 10)

    # Write reg[0] = 0xF0
    await spi_write (dut.clk, dut.ui_in, 0, 0xF0)
    # Write reg[1] = 0xDE
    await spi_write (dut.clk, dut.ui_in, 1, 0xDE)
    # Write reg[2] = 0xAD
    await spi_write (dut.clk, dut.ui_in, 2, 0xAD)
    # Write reg[3] = 0xBE
    await spi_write (dut.clk, dut.ui_in, 3, 0xBE)
    # Write reg[4] = 0xEF
    await spi_write (dut.clk, dut.ui_in, 4, 0xEF)
    # Write reg[5] = 0x55
    await spi_write (dut.clk, dut.ui_in, 5, 0x55)
    # Write reg[6] = 0xAA
    await spi_write (dut.clk, dut.ui_in, 6, 0xAA)
    # Write reg[7] = 0x0F
    await spi_write (dut.clk, dut.ui_in, 7, 0x0F)
  
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

    await ClockCycles(dut.clk, 10)

    assert reg0 == 0xF0
    assert reg1 == 0xDE
    assert reg2 == 0xAD
    assert reg3 == 0xBE
    assert reg4 == 0xEF
    assert reg5 == 0x55
    assert reg6 == 0xAA
    assert reg7 == 0x0F


    await ClockCycles(dut.clk, 10)
    
