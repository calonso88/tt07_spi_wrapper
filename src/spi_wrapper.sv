module spi_wrapper #(parameter int WIDTH = 8) (rstb, clk, ena, spi_cs_n, spi_clk, spi_mosi, spi_miso, spi_start_cmd, spi_stop_cmd, rsa_p, rsa_e, rsa_m, rsa_const, rsa_c, irq, spare);

  input rstb;
  input clk;
  input ena;

  input spi_cs_n;
  input spi_clk;
  input spi_mosi;
  output spi_miso;

  output spi_start_cmd;
  output spi_stop_cmd;

  output [WIDTH-1:0] rsa_p;
  output [WIDTH-1:0] rsa_e;
  output [WIDTH-1:0] rsa_m;
  output [WIDTH-1:0] rsa_const;
  input [WIDTH-1:0] rsa_c;

  input irq;
  output [WIDTH-1:0] spare;

  // Address width for register bank
  localparam int ADDR_WIDTH = 3;
  localparam int REG_WIDTH = WIDTH;

  //  Address map:
  //  Addr 0 - Read Status, Write is Spare register
  //  Addr 1 - Actions, Bit0 (Start), Bit1 (Stop)
  //  Addr 2 - P;
  //  Addr 3 - E;
  //  Addr 4 - M;
  //  Addr 5 - Const;
  //  Addr 6 - C;
  //  Addr 7 - Spare;

  // Auxiliar variables for SPIREG
  logic [ADDR_WIDTH-1:0] reg_addr;
  logic [REG_WIDTH-1:0] reg_data_i, reg_data_o;
  logic reg_data_o_vld;
  logic [REG_WIDTH-1:0] status;
  logic [REG_WIDTH-1:0] mem [0:(2**ADDR_WIDTH-1)];

  // Auxiliar start and stop commands through SPI
  logic spi_start;
  logic spi_stop;

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
  assign reg_data_i = (reg_addr == 0) ? status : mem[reg_addr];

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

  // SPI start and stop commands
  assign spi_start = mem[1][0];
  assign spi_stop = mem[1][1];

  // Generate SPI start and stop commands
  rising_edge_detector spi_start_cmd_i (.rstb(rstb), .clk(clk), .ena(ena), .data(spi_start), .pos_edge(spi_start_cmd));
  rising_edge_detector spi_stop_cmd_i (.rstb(rstb), .clk(clk), .ena(ena), .data(spi_stop), .pos_edge(spi_stop_cmd));

  // Map outputs to RSA unit
  assign rsa_p = mem[2];
  assign rsa_e = mem[3];
  assign rsa_m = mem[4];
  assign rsa_const = mem[5];

  // Status
  assign status[0] = irq;
  assign status[REG_WIDTH-1:1] = '0;

  // Spare
  assign spare = mem[7];

endmodule
