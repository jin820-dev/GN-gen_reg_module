// Auto-generated: AXI4-Lite bus interface (template)
// Module: gn_sample_reg_busif
// - Single outstanding read/write
// - AW and W may arrive independently; write occurs when both captured
// - Uses core-side hit flags to generate SLVERR on undefined address
// - Verilog-2001

module gn_sample_reg_busif #(
    parameter integer AXI_ADDR_W = 32,
    parameter integer AXI_DATA_W = 32
)(
    input  wire                     clk,
    input  wire                     reset_n,

    // AXI4-Lite (slave)
    input  wire [AXI_ADDR_W-1:0]    s_axi_awaddr,
    input  wire                     s_axi_awvalid,
    output wire                     s_axi_awready,

    input  wire [AXI_DATA_W-1:0]    s_axi_wdata,
    input  wire [AXI_DATA_W/8-1:0]  s_axi_wstrb,
    input  wire                     s_axi_wvalid,
    output wire                     s_axi_wready,

    output wire [1:0]               s_axi_bresp,
    output wire                     s_axi_bvalid,
    input  wire                     s_axi_bready,

    input  wire [AXI_ADDR_W-1:0]    s_axi_araddr,
    input  wire                     s_axi_arvalid,
    output wire                     s_axi_arready,

    output wire [AXI_DATA_W-1:0]    s_axi_rdata,
    output wire [1:0]               s_axi_rresp,
    output wire                     s_axi_rvalid,
    input  wire                     s_axi_rready,

    // Core-side interface
    output wire                     wr_en,
    output wire [AXI_ADDR_W-1:0]    wr_addr,
    output wire [AXI_DATA_W-1:0]    wr_data,
    output wire [AXI_DATA_W-1:0]    wr_mask,
    input  wire                     wr_hit,

    output wire                     rd_en,
    output wire [AXI_ADDR_W-1:0]    rd_addr,
    input  wire [AXI_DATA_W-1:0]    rd_data,
    input  wire                     rd_hit
);

    // ----------------------------
    // Sanity checks
    // ----------------------------
    initial begin
        if ((AXI_DATA_W % 8) != 0) begin
            $display("ERROR: AXI_DATA_W must be multiple of 8. AXI_DATA_W=%0d", AXI_DATA_W);
            $finish;
        end
    end

    localparam integer AXI_STRB_W = AXI_DATA_W/8;

    // ----------------------------
    // WSTRB -> bit mask
    // ----------------------------
    function [AXI_DATA_W-1:0] strb_to_mask;
        input [AXI_STRB_W-1:0] strb;
        integer i;
        begin
            strb_to_mask = {AXI_DATA_W{1'b0}};
            for (i = 0; i < AXI_STRB_W; i = i + 1) begin
                strb_to_mask[i*8 +: 8] = {8{strb[i]}};
            end
        end
    endfunction

    // ----------------------------
    // Latches (single outstanding)
    // ----------------------------
    reg [AXI_ADDR_W-1:0]    awaddr_lat;
    reg [AXI_DATA_W-1:0]    wdata_lat;
    reg [AXI_STRB_W-1:0]    wstrb_lat;
    reg                     have_aw;
    reg                     have_w;

    reg [AXI_ADDR_W-1:0]    araddr_lat;
    reg                     have_ar;

    reg [1:0]               bresp_i;
    reg                     bvalid_i;

    reg [1:0]               rresp_i;
    reg                     rvalid_i;
    reg [AXI_DATA_W-1:0]    rdata_i;

    assign s_axi_bresp  = bresp_i;
    assign s_axi_bvalid = bvalid_i;

    assign s_axi_rresp  = rresp_i;
    assign s_axi_rvalid = rvalid_i;
    assign s_axi_rdata  = rdata_i;

    // Ready when we are not holding a pending response
    assign s_axi_awready = (~have_aw) & (~bvalid_i);
    assign s_axi_wready  = (~have_w)  & (~bvalid_i);
    assign s_axi_arready = (~have_ar) & (~rvalid_i);

    // Core interface outputs
    assign wr_addr = awaddr_lat;
    assign wr_data = wdata_lat;
    assign wr_mask = strb_to_mask(wstrb_lat);

    assign rd_addr = araddr_lat;

    wire do_write;
    wire do_read;

    assign do_write = have_aw & have_w & (~bvalid_i);
    assign do_read  = have_ar & (~rvalid_i);

    assign wr_en = do_write;
    assign rd_en = do_read;

    // Capture AW/W
    always @(posedge clk) begin
        if (!reset_n) begin
            have_aw <= 1'b0;
            have_w  <= 1'b0;
            awaddr_lat <= {AXI_ADDR_W{1'b0}};
            wdata_lat  <= {AXI_DATA_W{1'b0}};
            wstrb_lat  <= {AXI_STRB_W{1'b0}};
        end else begin
            if (s_axi_awvalid && s_axi_awready) begin
                awaddr_lat <= s_axi_awaddr;
                have_aw    <= 1'b1;
            end
            if (s_axi_wvalid && s_axi_wready) begin
                wdata_lat  <= s_axi_wdata;
                wstrb_lat  <= s_axi_wstrb;
                have_w     <= 1'b1;
            end

            // Clear after write response accepted
            if (bvalid_i && s_axi_bready) begin
                have_aw <= 1'b0;
                have_w  <= 1'b0;
            end
        end
    end

    // Write response
    always @(posedge clk) begin
        if (!reset_n) begin
            bvalid_i <= 1'b0;
            bresp_i  <= 2'b00;
        end else begin
            if (bvalid_i && s_axi_bready) begin
                bvalid_i <= 1'b0;
                bresp_i  <= 2'b00;
            end

            if (do_write) begin
                bvalid_i <= 1'b1;
                // OKAY if hit, else SLVERR
                bresp_i  <= (wr_hit ? 2'b00 : 2'b10);
            end
        end
    end

    // Capture AR
    always @(posedge clk) begin
        if (!reset_n) begin
            have_ar <= 1'b0;
            araddr_lat <= {AXI_ADDR_W{1'b0}};
        end else begin
            if (s_axi_arvalid && s_axi_arready) begin
                araddr_lat <= s_axi_araddr;
                have_ar    <= 1'b1;
            end
            if (rvalid_i && s_axi_rready) begin
                have_ar <= 1'b0;
            end
        end
    end

    // Read response
    always @(posedge clk) begin
        if (!reset_n) begin
            rvalid_i <= 1'b0;
            rresp_i  <= 2'b00;
            rdata_i  <= {AXI_DATA_W{1'b0}};
        end else begin
            if (rvalid_i && s_axi_rready) begin
                rvalid_i <= 1'b0;
                rresp_i  <= 2'b00;
            end

            if (do_read) begin
                rvalid_i <= 1'b1;
                rdata_i  <= rd_data;
                rresp_i  <= (rd_hit ? 2'b00 : 2'b10);
            end
        end
    end

endmodule
