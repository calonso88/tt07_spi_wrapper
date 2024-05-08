module spi_wrapper #(parameter int NUM_CFG = 8, parameter int NUM_STATUS = 8, parameter int REG_WIDTH = 8) (rstb, clk, ena, mode, spi_cs_n, spi_clk, spi_mosi, spi_miso, config_regs, status_regs);

  input logic rstb;
  input logic clk;
  input logic ena;

  input logic [1:0] mode;
  input logic spi_cs_n;
  input logic spi_clk;
  input logic spi_mosi;
  output logic spi_miso;

  output logic [NUM_CFG*REG_WIDTH-1:0] config_regs;
  output logic [NUM_STATUS*REG_WIDTH-1:0] status_regs;

  // Address width for register bank
  localparam int NUM_REGS = NUM_CFG+NUM_STATUS;
  localparam int ADDR_WIDTH = $clog2(NUM_REGS);

  // Auxiliar variables for SPIREG
  logic [ADDR_WIDTH-1:0] reg_addr;
  logic [REG_WIDTH-1:0] reg_data_i, reg_data_o;
  logic reg_data_o_vld;
  logic [REG_WIDTH-1:0] config_mem [NUM_CFG];
  logic [REG_WIDTH-1:0] status_int [NUM_STATUS];
  
  // Serial interface
  spi_reg #(
    .ADDR_W(ADDR_WIDTH),
    .REG_W(REG_WIDTH)
  ) spi_reg_inst (
    .clk(clk),
    .rstb(rstb),
    .ena(ena),
    .mode(mode),
    .spi_mosi(spi_mosi),
    .spi_miso(spi_miso),
    .spi_clk(spi_clk),
    .spi_cs_n(spi_cs_n),
    .reg_addr(reg_addr),
    .reg_data_i(reg_data_i),
    .reg_data_o(reg_data_o),
    .reg_data_o_dv(reg_data_o_vld),
    .status('0)
  );

  // CFG or Status Register read access
  assign reg_data_i = (reg_addr < NUM_CFG) ? config_mem[reg_addr] : status_int[reg_addr-NUM_CFG];

  // Index for reset register array
  int i;

  // Register write
  always_ff @(posedge clk or negedge rstb) begin
    if (!rstb) begin
      for (i = 0; i < NUM_CFG; i++) begin
        config_mem[i] <= 0;
      end
    end else begin
      if (ena == 1'b1) begin
        if (reg_data_o_vld) begin
          config_mem[reg_addr] <= reg_data_o;
        end
      end
    end
  end

  // Assign config regs
  assign config_regs[7:0]   = config_mem[0];
  assign config_regs[15:8]  = config_mem[1];
  assign config_regs[23:16] = config_mem[2];
  assign config_regs[31:24] = config_mem[3];
  assign config_regs[39:32] = config_mem[4];
  assign config_regs[47:40] = config_mem[5];
  assign config_regs[55:48] = config_mem[6];
  assign config_regs[63:56] = config_mem[7];

  // Assign status regs
  assign status_int[0] = 8'hCA;
  assign status_int[1] = 8'h10;
  assign status_int[2] = 8'hAA;
  assign status_int[3] = 8'h55;
  assign status_int[4] = 8'hFF;
  assign status_int[5] = 8'h00;
  assign status_int[6} = 8'hA5;
  assign status_int[7] = 8'h5A;
  
  assign status_regs[7:0]   = status_int[0];
  assign status_regs[15:8]  = status_int[1];
  assign status_regs[23:16] = status_int[2];
  assign status_regs[31:24] = status_int[3];
  assign status_regs[39:32] = status_int[4];
  assign status_regs[47:40] = status_int[5];
  assign status_regs[55:48] = status_int[6];
  assign status_regs[63:56] = status_int[7];

endmodule
