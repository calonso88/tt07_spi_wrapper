module spi_reg #(
    parameter int ADDR_W = 3,
    parameter int REG_W = 8
) (
    input  logic clk,
    input  logic rstb,
    input  logic ena,
    input  logic [1:0] mode,
    input  logic spi_mosi,
    output logic spi_miso,
    input  logic spi_clk,
    input  logic spi_cs_n,
    output logic [ADDR_W-1:0] reg_addr,
    input  logic [REG_W-1:0] reg_data_i,
    output logic [REG_W-1:0] reg_data_o,
    output logic reg_data_o_dv,
    input  logic [7:0] status
);

  // Map to outputs
  assign reg_addr = addr;
  assign reg_data_o = data;
  assign reg_data_o_dv = dv;
  assign spi_miso = tx_buffer[REG_W-1];

  // SPI Configuration
  // https://www.zipcores.com/datasheets/spi_slave.pdf - Table on CPOL and CPHA
  //parameter logic CPOL = 1'b0;
  //parameter logic CPHA = 1'b1;

  // Start of frame - negedge of spi_cs_n
  logic sof;
  // Pulse on start of frame
  falling_edge_detector falling_edge_detector_sof (.rstb(rstb), .clk(clk), .ena(ena), .data(spi_cs_n), .neg_edge(sof));
  // End of frame - posedge of spi_cs_n
  logic eof;
  // Pulse on end of frame
  rising_edge_detector rising_edge_detector_eof (.rstb(rstb), .clk(clk), .ena(ena), .data(spi_cs_n), .pos_edge(eof));
  
  // Pulses on rising and falling edge of spi_clk
  logic spi_clk_pos;
  logic spi_clk_neg;
  // Pulse on rising edge of spi_clk
  rising_edge_detector rising_edge_detector_spi_clk (.rstb(rstb), .clk(clk), .ena(ena), .data(spi_clk), .pos_edge(spi_clk_pos));
  // Pulse on falling edge of spi_clk
  falling_edge_detector falling_edge_detector_spi_clk (.rstb(rstb), .clk(clk), .ena(ena), .data(spi_clk), .neg_edge(spi_clk_neg));

  // Sample data
  logic spi_data_sample;
  // Change data
  logic spi_data_change;
  // Assert according to SPI Config
  always_comb begin
      case ( mode )
      2'b00 : begin
        spi_data_sample = spi_clk_pos;
        spi_data_change = spi_clk_neg;
      end
      2'b01 : begin
        spi_data_sample = spi_clk_neg;
        spi_data_change = spi_clk_pos;
      end
      2'b10 : begin
        spi_data_sample = spi_clk_neg;
        spi_data_change = spi_clk_pos;
      end
      2'b11 : begin
        spi_data_sample = spi_clk_pos;
        spi_data_change = spi_clk_neg;
      end 
      default : begin
        spi_data_sample = spi_clk_neg;
        spi_data_change = spi_clk_pos;
      end
    endcase
  end

  // FSM states type
  typedef enum logic [2:0] {
    STATE_IDLE, STATE_ADDR, STATE_CMD, STATE_RX_DATA, STATE_TX_DATA
  } fsm_state;

  // FSM states
  fsm_state state_new, next_state;

  // Next state transition
  always_ff @(negedge(rstb) or posedge(clk)) begin
    if (!rstb) begin
      state_new <= STATE_IDLE;
    end else begin
      if (ena == 1'b1) begin
        state_new <= next_state;
      end
    end
  end

  // Sample addr and data
  logic rx_buffer_shift_en;
  logic tx_buffer_load;
  logic sample_addr;
  logic sample_data;

  // Next state logic
  always_comb begin
    // default assignments
    next_state = state_new;
    rx_buffer_shift_en = 1'b0;
    tx_buffer_load = 1'b0;
    sample_addr = 1'b0;
    sample_data = 1'b0;

    case (state_new)
      STATE_IDLE : begin
        if (sof == 1'b1) begin
          next_state = STATE_ADDR;
        end
      end
      STATE_ADDR : begin
        rx_buffer_shift_en = 1'b1;
        if (rx_buffer_counter == 4'd8) begin
          sample_addr = 1'b1;
          next_state = STATE_CMD;
        end else if (eof == 1'b1) begin
          next_state = STATE_IDLE;
        end
      end
      STATE_CMD : begin
        if (reg_rw == 1'b0) begin
          next_state = STATE_TX_DATA;
        end else if (reg_rw == 1'b1) begin
          next_state = STATE_RX_DATA;
        end else if (eof == 1'b1) begin
          next_state = STATE_IDLE;
        end
      end
      STATE_RX_DATA : begin
        rx_buffer_shift_en = 1'b1;
        if (rx_buffer_counter == 4'd8) begin
          sample_data = 1'b1;
          next_state = STATE_IDLE;
        end else if (eof == 1'b1) begin
          next_state = STATE_IDLE;
        end
      end
      STATE_TX_DATA : begin
        if (tx_buffer_counter == 4'd0) begin
          tx_buffer_load = 1'b1;
        end else if (rx_buffer_counter == 4'd8) begin
          next_state = STATE_IDLE;
        end else if (eof == 1'b1) begin
          next_state = STATE_IDLE;
        end
      end
      default : begin
        next_state = STATE_IDLE;
      end
    endcase
  end

  // RX Buffer
  logic [REG_W-1:0] rx_buffer;

  // RX Buffer
  always_ff @(negedge(rstb) or posedge(clk)) begin
    if (!rstb) begin
      rx_buffer <= '0;
    end else begin
      if (ena == 1'b1) begin
        if (rx_buffer_shift_en == 1'b1) begin
          if (spi_data_sample == 1'b1) begin
            rx_buffer <= {rx_buffer[REG_W-2:0], spi_mosi};
          end
        end
      end
    end
  end

  // General counter
  logic [3:0] rx_buffer_counter;

  // RX Buffer
  always_ff @(negedge(rstb) or posedge(clk)) begin
    if (!rstb) begin
      rx_buffer_counter <= '0;
    end else begin
      if (ena == 1'b1) begin
        if (rx_buffer_counter == 4'd8) begin
          rx_buffer_counter <= '0;
        end else if (spi_data_sample == 1'b1) begin
          rx_buffer_counter <= rx_buffer_counter + 1'b1;
        end
      end
    end
  end

  // Addr register
  logic [ADDR_W-1:0] addr;
  logic reg_rw;

  // Addr Register
  always_ff @(negedge(rstb) or posedge(clk)) begin
    if (!rstb) begin
      addr <= '0;
      reg_rw <= '0;
    end else begin
      if (ena == 1'b1) begin
        if (sample_addr == 1'b1) begin
          addr <= rx_buffer[ADDR_W-1:0];
          reg_rw <= rx_buffer[REG_W-1];
        end
      end
    end
  end

  // Data register and data valid strobe
  logic [REG_W-1:0] data;
  logic dv;

  // Data Register
  always_ff @(negedge(rstb) or posedge(clk)) begin
    if (!rstb) begin
      data <= '0;
      dv <= '0;
    end else begin
      if (ena == 1'b1) begin
        dv <= '0;
        if (sample_data == 1'b1) begin
          data <= rx_buffer;
          dv <= (1'b1 & reg_rw);
        end
      end
    end
  end

  // General counter
  logic [3:0] tx_buffer_counter;
    
  // RX Buffer
  always_ff @(negedge(rstb) or posedge(clk)) begin
    if (!rstb) begin
      tx_buffer_counter <= '0;
    end else begin
      if (ena == 1'b1) begin
        if (tx_buffer_counter == 4'd8) begin
          tx_buffer_counter <= '0;
        end else if (spi_data_sample == 1'b1) begin
          tx_buffer_counter <= tx_buffer_counter + 1'b1;
        end
      end
    end
  end 

  // TX Buffer
  logic [REG_W-1:0] tx_buffer;

  // TX Buffer
  always_ff @(negedge(rstb) or posedge(clk)) begin
    if (!rstb) begin
      tx_buffer <= '0;
    end else begin
      if (ena == 1'b1) begin
        if (sof == 1'b1) begin
          tx_buffer <= status;
        end else if (tx_buffer_load == 1'b1) begin
          tx_buffer <= reg_data_i;
        end else if (spi_data_change == 1'b1) begin
          tx_buffer <= {tx_buffer[REG_W-2:0], 1'b0};
        end
      end
    end
  end

endmodule
