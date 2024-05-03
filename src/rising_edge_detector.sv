module rising_edge_detector (rstb, clk, ena, data, pos_edge);

  input rstb;
  input clk;
  input ena;
  input data;

  output pos_edge;

  logic data_dly;

  always_ff @(negedge(rstb) or posedge(clk)) begin
    if (!rstb) begin
      data_dly <= '0;
    end else begin
      if (ena == 1'b1) begin
        data_dly <= data;
      end
    end
  end

  assign pos_edge = data & (!data_dly);

endmodule
