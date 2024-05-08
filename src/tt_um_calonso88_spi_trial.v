/*
 * Copyright (c) 2024 Your Name
 * SPDX-License-Identifier: Apache-2.0
 */

`default_nettype none

module tt_um_calonso88_spi_trial (
    input  wire [7:0] ui_in,    // Dedicated inputs
    output wire [7:0] uo_out,   // Dedicated outputs
    input  wire [7:0] uio_in,   // IOs: Input path
    output wire [7:0] uio_out,  // IOs: Output path
    output wire [7:0] uio_oe,   // IOs: Enable path (active high: 0=input, 1=output)
    input  wire       ena,      // always 1 when the design is powered, so you can ignore it
    input  wire       clk,      // clock
    input  wire       rst_n     // reset_n - low to reset
);

  // SPI Auxiliars
  wire spi_cs_n;
  wire spi_clk;
  wire spi_miso;
  wire spi_mosi;
  wire cpol;
  wire cpha;
    
  // Sync'ed
  wire spi_cs_n_sync;
  wire spi_clk_sync;
  wire spi_mosi_sync;
  wire cpol_sync;
  wire cpha_sync;
  
  // Amount of CFG Regs and Status Regs + Regs Width
  localparam int NUM_CFG = 8;
  localparam int NUM_STATUS = 8;    
  localparam int REG_WIDTH = 8;

  // All output pins must be assigned. If not used, assign to 0.
  assign uo_out[2:0]  = '0;
  assign uo_out[7:5]  = '0;

  // Output ports
  assign uo_out[3] = spi_miso;
  assign uo_out[4] = '0;

  // Assign IOs as output
  assign uio_oe       = '1;
  // Assign spare to output
  assign uio_out[7:0] = '0;

  // Input ports
  assign spi_cs_n   = ui_in[0];
  assign spi_clk    = ui_in[1];
  assign spi_mosi   = ui_in[2];
  assign cpol       = ui_in[3];
  assign cpha       = ui_in[4];

  // Synchronizers
  synchronizer #(.WIDTH(1)) synchronizer_spi_cs_n_inst (.rstb(rst_n), .clk(clk), .ena(ena), .data_in(spi_cs_n), .data_out(spi_cs_n_sync));
  synchronizer #(.WIDTH(1)) synchronizer_spi_clk_inst  (.rstb(rst_n), .clk(clk), .ena(ena), .data_in(spi_clk),  .data_out(spi_clk_sync));
  synchronizer #(.WIDTH(1)) synchronizer_spi_mosi_inst (.rstb(rst_n), .clk(clk), .ena(ena), .data_in(spi_mosi), .data_out(spi_mosi_sync));
  synchronizer #(.WIDTH(1)) synchronizer_spi_mode_cpol (.rstb(rst_n), .clk(clk), .ena(ena), .data_in(cpol), .data_out(cpol_sync));
  synchronizer #(.WIDTH(1)) synchronizer_spi_mode_cpha (.rstb(rst_n), .clk(clk), .ena(ena), .data_in(cpha), .data_out(cpha_sync));

  // SPI wrapper
  spi_wrapper #(.NUM_CFG(NUM_CFG), .NUM_CFG(NUM_STATUS), .REG_WIDTH(REG_WIDTH)) spi_wrapper_i (.rstb(rst_n), .clk(clk), .ena(ena), .mode({cpol_sync, cpha_sync}), .spi_cs_n(spi_cs_n_sync), .spi_clk(spi_clk_sync), .spi_mosi(spi_mosi_sync), .spi_miso(spi_miso), .config_regs(), .status_regs());
    
endmodule
