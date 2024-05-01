  module spi_wrapper #(parameter int NUM_REGS = 8, parameter int WIDTH = 8) (rstb, clk, ena, spi_cs_n, spi_clk, spi_mosi, spi_miso, config_regs, status_regs);

  input logic rstb;
  input logic clk;
  input logic ena;

  input logic spi_cs_n;
  input logic spi_clk;
  input logic spi_mosi;
  output logic spi_miso;

  output logic [2:0][WIDTH-1:0] config_regs;
  //output logic [($clog2(NUM_REGS)-1):0][WIDTH-1:0] config_regs [NUM_REGS];
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
  logic [((2**ADDR_WIDTH)-1):0][REG_WIDTH-1:0] mem ;

  // Serial interface
  spi_reg #(
    .ADDR_W(ADDR_WIDTH),
    .REG_W(REG_WIDTH)
  ) spi_reg_inst (
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
  always_comb begin
    for (i = 0; i < 2**ADDR_WIDTH; i++) begin
      assign config_regs[i] = mem[i];
    end
  end

  // Assign status regs
  assign status_regs = '0;

endmodule
