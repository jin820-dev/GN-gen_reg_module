// Auto-generated: register core (from CSV)
// Module: gn_sample_reg_core
// Rules:
// - Register names in CSV are expected like 'REG_*'
// - Internal registers: r_REG_*
// - External reference outputs: w_REG_*_o
// - WRITE logic: one always block per register (no case)
// - READ logic: case allowed (combinational)
// - Verilog-2001

module gn_sample_reg_core #(
    parameter integer AXI_ADDR_W = 32,
    parameter integer AXI_DATA_W = 32
)(
    input  wire                     clk,
    input  wire                     reset_n,
    input  wire                     wr_en,
    input  wire [AXI_ADDR_W-1:0]    wr_addr,
    input  wire [AXI_DATA_W-1:0]    wr_data,
    input  wire [AXI_DATA_W-1:0]    wr_mask,
    output reg                      wr_hit,
    input  wire                     rd_en,
    input  wire [AXI_ADDR_W-1:0]    rd_addr,
    output reg  [AXI_DATA_W-1:0]    rd_data,
    output reg                      rd_hit,
    output wire [AXI_DATA_W-1:0]    w_REG_CTRL_o,
    output wire [AXI_DATA_W-1:0]    w_REG_CFG_o,
    output wire [AXI_DATA_W-1:0]    w_REG_STATUS_o,
    output wire [AXI_DATA_W-1:0]    w_REG_IRQ_STATUS_o,
    output wire [AXI_DATA_W-1:0]    w_REG_IRQ_CLR_o,
    output wire [AXI_DATA_W-1:0]    w_REG_TX_DATA_o
);

    // REG_CTRL @0x0000 [RW] reset=32'h00000000
    //   - ENABLE[0]: Enable block
    //   - MODE[3:1]: Mode select
    //   - SOFT_RST[4]: Software reset (self-clearing by SW)
    //   - RSVD[31:5]: Reserved
    // REG_CFG @0x0004 [RW] reset=32'h00000010
    //   - DIV[7:0]: Clock divider
    //   - THRESH[15:8]: Threshold
    //   - RSVD[31:16]: Reserved
    // REG_STATUS @0x0008 [RO] reset=32'h00000001
    //   - READY[0]: Ready status
    //   - BUSY[1]: Busy status
    //   - ERR[8]: Error flag
    //   - RSVD[7:2]: Reserved
    //   - RSVD2[31:9]: Reserved
    // REG_IRQ_STATUS @0x000C [RO] reset=32'h00000000
    //   - IRQ_PEND[7:0]: Interrupt pending bits
    //   - RSVD[31:8]: Reserved
    // REG_IRQ_CLR @0x0010 [W1C] reset=32'h00000000
    //   - IRQ_CLR[7:0]: Write-1-to-clear interrupt bits
    //   - RSVD[31:8]: Reserved
    // REG_TX_DATA @0x0014 [WO] reset=32'h00000000
    //   - DATA[31:0]: Write-only TX data

    localparam [AXI_ADDR_W-1:0] ADDR_REG_CTRL = 0;
    localparam [AXI_ADDR_W-1:0] ADDR_REG_CFG = 4;
    localparam [AXI_ADDR_W-1:0] ADDR_REG_STATUS = 8;
    localparam [AXI_ADDR_W-1:0] ADDR_REG_IRQ_STATUS = 12;
    localparam [AXI_ADDR_W-1:0] ADDR_REG_IRQ_CLR = 16;
    localparam [AXI_ADDR_W-1:0] ADDR_REG_TX_DATA = 20;

    // Registers
    reg [AXI_DATA_W-1:0] r_REG_CTRL;
    reg [AXI_DATA_W-1:0] r_REG_CFG;
    reg [AXI_DATA_W-1:0] r_REG_STATUS;
    reg [AXI_DATA_W-1:0] r_REG_IRQ_STATUS;
    reg [AXI_DATA_W-1:0] r_REG_IRQ_CLR;
    reg [AXI_DATA_W-1:0] r_REG_TX_DATA;

    // Reference outputs
    assign w_REG_CTRL_o = r_REG_CTRL;
    assign w_REG_CFG_o = r_REG_CFG;
    assign w_REG_STATUS_o = r_REG_STATUS;
    assign w_REG_IRQ_STATUS_o = r_REG_IRQ_STATUS;
    assign w_REG_IRQ_CLR_o = r_REG_IRQ_CLR;
    assign w_REG_TX_DATA_o = r_REG_TX_DATA;

    // REG_CTRL (RW)
    always @(posedge clk) begin
        if (!reset_n) begin
            r_REG_CTRL <= 32'h00000000;
        end else begin
            if (wr_en && (wr_addr == ADDR_REG_CTRL)) begin
                r_REG_CTRL <= (r_REG_CTRL & ~wr_mask) | (wr_data & wr_mask);
            end
        end
    end

    // REG_CFG (RW)
    always @(posedge clk) begin
        if (!reset_n) begin
            r_REG_CFG <= 32'h00000010;
        end else begin
            if (wr_en && (wr_addr == ADDR_REG_CFG)) begin
                r_REG_CFG <= (r_REG_CFG & ~wr_mask) | (wr_data & wr_mask);
            end
        end
    end

    // REG_STATUS (RO)
    always @(posedge clk) begin
        if (!reset_n) begin
            r_REG_STATUS <= 32'h00000001;
        end else begin
            // RO: no write update
        end
    end

    // REG_IRQ_STATUS (RO)
    always @(posedge clk) begin
        if (!reset_n) begin
            r_REG_IRQ_STATUS <= 32'h00000000;
        end else begin
            // RO: no write update
        end
    end

    // REG_IRQ_CLR (W1C)
    always @(posedge clk) begin
        if (!reset_n) begin
            r_REG_IRQ_CLR <= 32'h00000000;
        end else begin
            if (wr_en && (wr_addr == ADDR_REG_IRQ_CLR)) begin
                r_REG_IRQ_CLR <= r_REG_IRQ_CLR & ~(wr_data & wr_mask);
            end
        end
    end

    // REG_TX_DATA (WO)
    always @(posedge clk) begin
        if (!reset_n) begin
            r_REG_TX_DATA <= 32'h00000000;
        end else begin
            if (wr_en && (wr_addr == ADDR_REG_TX_DATA)) begin
                r_REG_TX_DATA <= (r_REG_TX_DATA & ~wr_mask) | (wr_data & wr_mask);
            end
        end
    end


    // Read mux (combinational)
    always @(*) begin
        rd_data = {AXI_DATA_W{1'b0}};
        case (rd_addr)
            ADDR_REG_CTRL: rd_data = r_REG_CTRL;
            ADDR_REG_CFG: rd_data = r_REG_CFG;
            ADDR_REG_STATUS: rd_data = r_REG_STATUS;
            ADDR_REG_IRQ_STATUS: rd_data = r_REG_IRQ_STATUS;
            ADDR_REG_IRQ_CLR: rd_data = r_REG_IRQ_CLR;
            ADDR_REG_TX_DATA: rd_data = {AXI_DATA_W{1'b0}};
            default: rd_data = {AXI_DATA_W{1'b0}};
        endcase
    end

    // Hit decode (combinational)
    always @(*) begin
        wr_hit = 1'b0;
        case (wr_addr)
            ADDR_REG_CTRL: wr_hit = 1'b1;
            ADDR_REG_CFG: wr_hit = 1'b1;
            ADDR_REG_STATUS: wr_hit = 1'b1;
            ADDR_REG_IRQ_STATUS: wr_hit = 1'b1;
            ADDR_REG_IRQ_CLR: wr_hit = 1'b1;
            ADDR_REG_TX_DATA: wr_hit = 1'b1;
            default: wr_hit = 1'b0;
        endcase
    end

    always @(*) begin
        rd_hit = 1'b0;
        case (rd_addr)
            ADDR_REG_CTRL: rd_hit = 1'b1;
            ADDR_REG_CFG: rd_hit = 1'b1;
            ADDR_REG_STATUS: rd_hit = 1'b1;
            ADDR_REG_IRQ_STATUS: rd_hit = 1'b1;
            ADDR_REG_IRQ_CLR: rd_hit = 1'b1;
            ADDR_REG_TX_DATA: rd_hit = 1'b1;
            default: rd_hit = 1'b0;
        endcase
    end

endmodule
