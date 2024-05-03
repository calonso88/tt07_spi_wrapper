module falling_edge_detector (rstb, clk, ena, data, neg_edge);

  input rstb;
  input clk;
  input ena;
  input data;

  output neg_edge;

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

  assign neg_edge = (!data) & data_dly;

endmodule
