// Auto-generated: wrapper
// Module: gn_sample_reg_wrap
// Instantiates:
//  - gn_sample_reg_busif (AXI4-Lite bus interface)
//  - gn_sample_reg_core (register core)

module gn_sample_reg_wrap #(
    parameter integer AXI_ADDR_W = 32,
    parameter integer AXI_DATA_W = 32
)(
    input  wire                     clk,
    input  wire                     reset_n,
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
    output wire [AXI_DATA_W-1:0]    w_REG_CTRL_o,
    output wire [AXI_DATA_W-1:0]    w_REG_CFG_o,
    output wire [AXI_DATA_W-1:0]    w_REG_STATUS_o,
    output wire [AXI_DATA_W-1:0]    w_REG_IRQ_STATUS_o,
    output wire [AXI_DATA_W-1:0]    w_REG_IRQ_CLR_o,
    output wire [AXI_DATA_W-1:0]    w_REG_TX_DATA_o
);

    wire                     wr_en;
    wire [AXI_ADDR_W-1:0]    wr_addr;
    wire [AXI_DATA_W-1:0]    wr_data;
    wire [AXI_DATA_W-1:0]    wr_mask;
    wire                     wr_hit;

    wire                     rd_en;
    wire [AXI_ADDR_W-1:0]    rd_addr;
    wire [AXI_DATA_W-1:0]    rd_data;
    wire                     rd_hit;

    gn_sample_reg_busif #(
        .AXI_ADDR_W(AXI_ADDR_W),
        .AXI_DATA_W(AXI_DATA_W)
    ) u_busif (
        .clk(clk),
        .reset_n(reset_n),

        .s_axi_awaddr(s_axi_awaddr),
        .s_axi_awvalid(s_axi_awvalid),
        .s_axi_awready(s_axi_awready),

        .s_axi_wdata(s_axi_wdata),
        .s_axi_wstrb(s_axi_wstrb),
        .s_axi_wvalid(s_axi_wvalid),
        .s_axi_wready(s_axi_wready),

        .s_axi_bresp(s_axi_bresp),
        .s_axi_bvalid(s_axi_bvalid),
        .s_axi_bready(s_axi_bready),

        .s_axi_araddr(s_axi_araddr),
        .s_axi_arvalid(s_axi_arvalid),
        .s_axi_arready(s_axi_arready),

        .s_axi_rdata(s_axi_rdata),
        .s_axi_rresp(s_axi_rresp),
        .s_axi_rvalid(s_axi_rvalid),
        .s_axi_rready(s_axi_rready),

        .wr_en(wr_en),
        .wr_addr(wr_addr),
        .wr_data(wr_data),
        .wr_mask(wr_mask),
        .wr_hit(wr_hit),

        .rd_en(rd_en),
        .rd_addr(rd_addr),
        .rd_data(rd_data),
        .rd_hit(rd_hit)
    );

    gn_sample_reg_core #(
        .AXI_ADDR_W(AXI_ADDR_W),
        .AXI_DATA_W(AXI_DATA_W)
    ) u_core (
        .clk(clk),
        .reset_n(reset_n),

        .wr_en(wr_en),
        .wr_addr(wr_addr),
        .wr_data(wr_data),
        .wr_mask(wr_mask),
        .wr_hit(wr_hit),

        .rd_en(rd_en),
        .rd_addr(rd_addr),
        .rd_data(rd_data),
        .rd_hit(rd_hit),

        .w_REG_CTRL_o(w_REG_CTRL_o),
        .w_REG_CFG_o(w_REG_CFG_o),
        .w_REG_STATUS_o(w_REG_STATUS_o),
        .w_REG_IRQ_STATUS_o(w_REG_IRQ_STATUS_o),
        .w_REG_IRQ_CLR_o(w_REG_IRQ_CLR_o),
        .w_REG_TX_DATA_o(w_REG_TX_DATA_o)
    );

endmodule
