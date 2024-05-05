module spi_wrapper #(parameter int NUM_REGS = 8, parameter int WIDTH = 8) (rstb, clk, ena, mode, spi_cs_n, spi_clk, spi_mosi, spi_miso, config_regs, status_regs);

  input logic rstb;
  input logic clk;
  input logic ena;

  input logic [1:0] mode;
  input logic spi_cs_n;
  input logic spi_clk;
  input logic spi_mosi;
  output logic spi_miso;

  output logic [NUM_REGS*WIDTH-1:0] config_regs;
  output logic [WIDTH-1:0] status_regs;

  // Address width for register bank
  localparam int ADDR_WIDTH = $clog2(NUM_REGS);
  localparam int REG_WIDTH = WIDTH;
    
  // Auxiliar variables for SPIREG
  logic [ADDR_WIDTH-1:0] reg_addr;
  logic [REG_WIDTH-1:0] reg_data_i, reg_data_o;
  logic reg_data_o_vld;
  logic [REG_WIDTH-1:0] status;
  logic [REG_WIDTH-1:0] mem [NUM_REGS];

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

  // Register read access
  assign reg_data_i = mem[reg_addr];

  // Index for reset register array
  int i;

  // Register write
  always_ff @(posedge clk or negedge rstb) begin
    if (!rstb) begin
      for (i = 0; i < 2**ADDR_WIDTH; i++) begin
        mem[i] <= 0;
      end
    end else begin
      if (ena == 1'b1) begin
        if (reg_data_o_vld) begin
          mem[reg_addr] <= reg_data_o;
        end
      end
    end
  end

  // Assign config regs
  assign config_regs[7:0] = mem[0];
  assign config_regs[15:8] = mem[1];
  assign config_regs[23:16] = mem[2];
  assign config_regs[31:24] = mem[3];
  assign config_regs[39:32] = mem[4];
  assign config_regs[47:40] = mem[5];
  assign config_regs[55:48] = mem[6];
  assign config_regs[63:56] = mem[7];

  // Assign status regs
  assign status_regs = '0;

endmodule
