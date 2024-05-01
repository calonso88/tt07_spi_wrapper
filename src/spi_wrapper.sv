  module spi_wrapper #(parameter int NUM_REGS = 8, parameter int WIDTH = 8) (rstb, clk, ena, spi_cs_n, spi_clk, spi_mosi, spi_miso, config_regs, status_regs);

  input logic rstb;
  input logic clk;
  input logic ena;

  input logic spi_cs_n;
  input logic spi_clk;
  input logic spi_mosi;
  output logic spi_miso;

  output logic [WIDTH-1:0] config_regs [NUM_REGS];
  //output logic [WIDTH-1:0] status_regs [NUM_REGS];
  output logic [WIDTH-1:0] status_regs;

  // Address width for register bank
  //localparam int ADDR_WIDTH = $clog2(NUM_REGS);
  localparam int ADDR_WIDTH = 3;
  localparam int REG_WIDTH = WIDTH;

  // Auxiliar variables for SPIREG
  logic [ADDR_WIDTH-1:0] reg_addr;
  logic [REG_WIDTH-1:0] reg_data_i, reg_data_o;
  logic reg_data_o_vld;
  logic [REG_WIDTH-1:0] status;
  logic [REG_WIDTH-1:0] mem [0:(2**ADDR_WIDTH-1)];

  // Serial interface
  spireg #(
    .ADDR_W(ADDR_WIDTH),
    .REG_W(REG_WIDTH)
  ) spireg_inst (
    .clk(clk),
    .nrst(rstb),
    .mosi(spi_mosi),
    .miso(spi_miso),
    .sclk(spi_clk),
    .nss(spi_cs_n),
    .reg_addr(reg_addr),
    .reg_data_i(reg_data_i),
    .reg_data_o(reg_data_o),
    .reg_data_o_vld(reg_data_o_vld),
    .status(status),
    .fastcmd(),
    .fastcmd_vld()
  );

  // Register read access
  assign reg_data_i = mem[reg_addr];

  // Index for reset unpacked register array
  int i;

  // Register write and update encryption with irq
  always_ff @(posedge clk or negedge rstb) begin
    if (!rstb) begin
      for (i = 0; i < 2**ADDR_WIDTH; i++) begin
        mem[i] <= 0;
      end
    end else begin
      if (ena == 1'b1) begin
        if (reg_data_o_vld) begin
          mem[reg_addr] <= reg_data_o;
        end else if (irq == 1'b1) begin
          mem[6] <= rsa_c;
        end
      end
    end
  end

  // Assign cfg regs
  assign config_regs = mem;
  assign status_regs = '0;

endmodule
