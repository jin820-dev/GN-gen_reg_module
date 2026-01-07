#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import os
import re
from dataclasses import dataclass
from typing import Dict, List, Tuple


# ============================================================
# Data structures
# ============================================================
@dataclass
class Field:
    name: str
    lsb: int
    msb: int
    desc: str


@dataclass
class Reg:
    name: str
    offset: int
    access: str  # RW/RO/WO/W1C (register-level)
    reset: int
    fields: List[Field]


# ============================================================
# Helpers
# ============================================================
_INT_RE = re.compile(r"^\s*(0x[0-9a-fA-F_]+|\d+)\s*$")


def parse_int(s: str) -> int:
    m = _INT_RE.match(s or "")
    if not m:
        raise ValueError(f"Invalid integer literal: '{s}'")
    t = m.group(1).replace("_", "")
    return int(t, 0)


def norm_access(s: str) -> str:
    a = (s or "").strip().upper()
    if a not in ("RW", "RO", "WO", "W1C"):
        raise ValueError(f"Unsupported access '{s}'. Use one of: RW, RO, WO, W1C")
    return a


def verilog_ident(s: str) -> str:
    t = re.sub(r"[^a-zA-Z0-9_]", "_", (s or "").strip())
    if not t:
        t = "_"
    if not re.match(r"^[a-zA-Z_]", t):
        t = "_" + t
    return t


def file_stem(s: str) -> str:
    t = re.sub(r"[^a-zA-Z0-9_]+", "_", (s or "").strip())
    return t or "regblock"


def fmt_hex32(v: int) -> str:
    return f"32'h{(v & 0xFFFF_FFFF):08X}"


def check_no_overlap(fields: List[Field]) -> None:
    used = set()
    for f in fields:
        if f.lsb < 0 or f.msb < f.lsb:
            raise ValueError(f"Invalid bit range {f.name}[{f.msb}:{f.lsb}]")
        for b in range(f.lsb, f.msb + 1):
            if b in used:
                raise ValueError(f"Bit overlap detected at bit {b} (field {f.name})")
            used.add(b)


def reg_token_from_csv(name: str) -> str:
    """
    CSV register name is expected like 'REG_CTRL' etc.
    We normalize to a Verilog identifier and force uppercase.
    """
    return verilog_ident(name).upper()


def join_ports(lines: List[str]) -> str:
    """
    Join Verilog port lines with commas safely (no trailing comma).
    """
    lines = [ln.rstrip() for ln in lines if ln.strip()]
    if not lines:
        return ""
    out: List[str] = []
    for i, ln in enumerate(lines):
        if i != len(lines) - 1:
            out.append(ln + ",")
        else:
            out.append(ln)
    return "\n".join(out)


# ============================================================
# CSV parsing
# ============================================================
REQUIRED_COLS = ("name", "offset", "access", "reset", "field", "lsb", "msb", "desc")


def load_regs(csv_path: str) -> List[Reg]:
    with open(csv_path, "r", encoding="utf-8-sig", newline="") as f:
        r = csv.DictReader(f)
        fns = r.fieldnames or []
        for c in REQUIRED_COLS:
            if c not in fns:
                raise ValueError(f"CSV missing required column: {c}")

        groups: Dict[Tuple[str, int], List[dict]] = {}
        for row in r:
            name = (row["name"] or "").strip()
            if not name:
                continue
            off = parse_int(row["offset"])
            groups.setdefault((name, off), []).append(row)

    regs: List[Reg] = []
    for (name, off), rows in sorted(groups.items(), key=lambda x: x[0][1]):
        accs = {norm_access(rr["access"]) for rr in rows}
        if len(accs) != 1:
            raise ValueError(f"Access mismatch in reg '{name}' @0x{off:X}: {sorted(accs)}")
        access = next(iter(accs))

        resets = {parse_int(rr["reset"]) for rr in rows}
        if len(resets) != 1:
            raise ValueError(f"Reset mismatch in reg '{name}' @0x{off:X}: {sorted(resets)}")
        reset = next(iter(resets))

        fields: List[Field] = []
        for rr in rows:
            fname = (rr["field"] or "").strip()
            if not fname:
                continue
            lsb = parse_int(rr["lsb"])
            msb = parse_int(rr["msb"])
            desc = (rr.get("desc") or "").strip()
            fields.append(Field(name=fname, lsb=lsb, msb=msb, desc=desc))

        check_no_overlap(fields)

        if off % 4 != 0:
            raise ValueError(f"Offset not 4-byte aligned: {name} offset=0x{off:X}")

        regs.append(Reg(name=name, offset=off, access=access, reset=reset, fields=fields))

    return regs


# ============================================================
# Verilog generation: reg_busif (template)
# ============================================================
def gen_busif_v(mod_busif: str) -> str:
    m = verilog_ident(mod_busif)
    return f"""// Auto-generated: AXI4-Lite bus interface (template)
// Module: {m}
// - Single outstanding read/write
// - AW and W may arrive independently; write occurs when both captured
// - Uses core-side hit flags to generate SLVERR on undefined address
// - Verilog-2001

module {m} #(
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
            strb_to_mask = {{AXI_DATA_W{{1'b0}}}};
            for (i = 0; i < AXI_STRB_W; i = i + 1) begin
                strb_to_mask[i*8 +: 8] = {{8{{strb[i]}}}};
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
            awaddr_lat <= {{AXI_ADDR_W{{1'b0}}}};
            wdata_lat  <= {{AXI_DATA_W{{1'b0}}}};
            wstrb_lat  <= {{AXI_STRB_W{{1'b0}}}};
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
            araddr_lat <= {{AXI_ADDR_W{{1'b0}}}};
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
            rdata_i  <= {{AXI_DATA_W{{1'b0}}}};
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
"""


# ============================================================
# Verilog generation: reg_core (CSV dependent)
# - write: one always per reg, NO case
# - read: case OK
# - external reference outputs: w_REG_***_o
# - internal regs: r_REG_***
# ============================================================
def gen_core_v(mod_core: str, regs: List[Reg]) -> str:
    m = verilog_ident(mod_core)

    # Comments (fields)
    field_comments: List[str] = []
    for rg in regs:
        token = reg_token_from_csv(rg.name)  # e.g. REG_CTRL
        field_comments.append(f"    // {token} @0x{rg.offset:04X} [{rg.access}] reset={fmt_hex32(rg.reset)}")
        for f in rg.fields:
            rng = f"[{f.msb}:{f.lsb}]" if f.msb != f.lsb else f"[{f.lsb}]"
            d = f.desc.replace("\n", " ").strip()
            field_comments.append(f"    //   - {f.name}{rng}: {d}")

    # Address localparams
    addr_lines: List[str] = []
    for rg in regs:
        token = reg_token_from_csv(rg.name)
        addr_lines.append(f"    localparam [AXI_ADDR_W-1:0] ADDR_{token} = {rg.offset};")

    # Reg declarations (internal)
    reg_decl: List[str] = []
    for rg in regs:
        token = reg_token_from_csv(rg.name)
        reg_decl.append(f"    reg [AXI_DATA_W-1:0] r_{token};")

    # Output ports (reference)
    out_ports: List[str] = []
    for rg in regs:
        token = reg_token_from_csv(rg.name)
        out_ports.append(f"    output wire [AXI_DATA_W-1:0]    w_{token}_o")

    # Assign outputs
    out_assigns: List[str] = []
    for rg in regs:
        token = reg_token_from_csv(rg.name)
        out_assigns.append(f"    assign w_{token}_o = r_{token};")

    # Write always blocks (one always per register, no case)
    write_blocks: List[str] = []
    for rg in regs:
        token = reg_token_from_csv(rg.name)
        acc = rg.access
        reset = fmt_hex32(rg.reset)

        if acc == "RO":
            blk = f"""    // {token} (RO)
    always @(posedge clk) begin
        if (!reset_n) begin
            r_{token} <= {reset};
        end else begin
            // RO: no write update
        end
    end
"""
        elif acc in ("RW", "WO"):
            blk = f"""    // {token} ({acc})
    always @(posedge clk) begin
        if (!reset_n) begin
            r_{token} <= {reset};
        end else begin
            if (wr_en && (wr_addr == ADDR_{token})) begin
                r_{token} <= (r_{token} & ~wr_mask) | (wr_data & wr_mask);
            end
        end
    end
"""
        elif acc == "W1C":
            blk = f"""    // {token} (W1C)
    always @(posedge clk) begin
        if (!reset_n) begin
            r_{token} <= {reset};
        end else begin
            if (wr_en && (wr_addr == ADDR_{token})) begin
                r_{token} <= r_{token} & ~(wr_data & wr_mask);
            end
        end
    end
"""
        else:
            blk = f"""    // {token} (unsupported access)
    always @(posedge clk) begin
        if (!reset_n) begin
            r_{token} <= {reset};
        end else begin
            // unsupported: no update
        end
    end
"""
        write_blocks.append(blk)

    # Read mux: case OK
    read_cases: List[str] = []
    rd_hit_cases: List[str] = []
    wr_hit_cases: List[str] = []

    for rg in regs:
        token = reg_token_from_csv(rg.name)

        if rg.access == "WO":
            read_cases.append(f"            ADDR_{token}: rd_data = {{AXI_DATA_W{{1'b0}}}};\n")
        else:
            read_cases.append(f"            ADDR_{token}: rd_data = r_{token};\n")

        rd_hit_cases.append(f"            ADDR_{token}: rd_hit = 1'b1;\n")
        wr_hit_cases.append(f"            ADDR_{token}: wr_hit = 1'b1;\n")

    port_lines = [
        "    input  wire                     clk",
        "    input  wire                     reset_n",
        "",
        "    input  wire                     wr_en",
        "    input  wire [AXI_ADDR_W-1:0]    wr_addr",
        "    input  wire [AXI_DATA_W-1:0]    wr_data",
        "    input  wire [AXI_DATA_W-1:0]    wr_mask",
        "    output reg                      wr_hit",
        "",
        "    input  wire                     rd_en",
        "    input  wire [AXI_ADDR_W-1:0]    rd_addr",
        "    output reg  [AXI_DATA_W-1:0]    rd_data",
        "    output reg                      rd_hit",
    ]
    # Add reference outputs at the end of the port list
    port_lines += [""] + out_ports

    return f"""// Auto-generated: register core (from CSV)
// Module: {m}
// Rules:
// - Register names in CSV are expected like 'REG_*'
// - Internal registers: r_REG_*
// - External reference outputs: w_REG_*_o
// - WRITE logic: one always block per register (no case)
// - READ logic: case allowed (combinational)
// - Verilog-2001

module {m} #(
    parameter integer AXI_ADDR_W = 32,
    parameter integer AXI_DATA_W = 32
)(
{join_ports(port_lines)}
);

{os.linesep.join(field_comments)}

{os.linesep.join(addr_lines)}

    // Registers
{os.linesep.join(reg_decl)}

    // Reference outputs
{os.linesep.join(out_assigns)}

{os.linesep.join(write_blocks)}

    // Read mux (combinational)
    always @(*) begin
        rd_data = {{AXI_DATA_W{{1'b0}}}};
        case (rd_addr)
{''.join(read_cases)}            default: rd_data = {{AXI_DATA_W{{1'b0}}}};
        endcase
    end

    // Hit decode (combinational)
    always @(*) begin
        wr_hit = 1'b0;
        case (wr_addr)
{''.join(wr_hit_cases)}            default: wr_hit = 1'b0;
        endcase
    end

    always @(*) begin
        rd_hit = 1'b0;
        case (rd_addr)
{''.join(rd_hit_cases)}            default: rd_hit = 1'b0;
        endcase
    end

endmodule
"""


# ============================================================
# Verilog generation: reg_wrap (connect busif + core + expose outputs)
# ============================================================
def gen_wrap_v(mod_wrap: str, mod_busif: str, mod_core: str, regs: List[Reg]) -> str:
    mw = verilog_ident(mod_wrap)
    mb = verilog_ident(mod_busif)
    mc = verilog_ident(mod_core)

    # Wrap output ports (same as core reference outputs)
    out_ports: List[str] = []
    for rg in regs:
        token = reg_token_from_csv(rg.name)
        out_ports.append(f"    output wire [AXI_DATA_W-1:0]    w_{token}_o")

    # Core instance connections for those outputs
    out_conns: List[str] = []
    for rg in regs:
        token = reg_token_from_csv(rg.name)
        out_conns.append(f"        .w_{token}_o(w_{token}_o)")

    wrap_ports = [
        "    input  wire                     clk",
        "    input  wire                     reset_n",
        "",
        "    input  wire [AXI_ADDR_W-1:0]    s_axi_awaddr",
        "    input  wire                     s_axi_awvalid",
        "    output wire                     s_axi_awready",
        "",
        "    input  wire [AXI_DATA_W-1:0]    s_axi_wdata",
        "    input  wire [AXI_DATA_W/8-1:0]  s_axi_wstrb",
        "    input  wire                     s_axi_wvalid",
        "    output wire                     s_axi_wready",
        "",
        "    output wire [1:0]               s_axi_bresp",
        "    output wire                     s_axi_bvalid",
        "    input  wire                     s_axi_bready",
        "",
        "    input  wire [AXI_ADDR_W-1:0]    s_axi_araddr",
        "    input  wire                     s_axi_arvalid",
        "    output wire                     s_axi_arready",
        "",
        "    output wire [AXI_DATA_W-1:0]    s_axi_rdata",
        "    output wire [1:0]               s_axi_rresp",
        "    output wire                     s_axi_rvalid",
        "    input  wire                     s_axi_rready",
        "",
    ] + out_ports

    return f"""// Auto-generated: wrapper
// Module: {mw}
// Instantiates:
//  - {mb} (AXI4-Lite bus interface)
//  - {mc} (register core)

module {mw} #(
    parameter integer AXI_ADDR_W = 32,
    parameter integer AXI_DATA_W = 32
)(
{join_ports(wrap_ports)}
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

    {mb} #(
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

    {mc} #(
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

{join_ports(out_conns)}
    );

endmodule
"""


# ============================================================
# Write files
# ============================================================
def write_text(path: str, text: str) -> None:
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)


def main() -> int:
    ap = argparse.ArgumentParser(description="Generate reg_wrap/reg_busif/reg_core from CSV.")
    ap.add_argument("csv", help="Input CSV (reg fields).")
    ap.add_argument("--base", default="regblock", help="Base name for modules/files (e.g. gn_common_test).")
    ap.add_argument("--outdir", default=".", help="Output directory (e.g. src).")
    args = ap.parse_args()

    regs = load_regs(args.csv)

    base_mod = verilog_ident(args.base)
    base_file = file_stem(args.base)

    mod_wrap  = f"{base_mod}_reg_wrap"
    mod_busif = f"{base_mod}_reg_busif"
    mod_core  = f"{base_mod}_reg_core"

    fn_wrap  = os.path.join(args.outdir, f"{base_file}_reg_wrap.v")
    fn_busif = os.path.join(args.outdir, f"{base_file}_reg_busif.v")
    fn_core  = os.path.join(args.outdir, f"{base_file}_reg_core.v")

    v_busif = gen_busif_v(mod_busif)
    v_core  = gen_core_v(mod_core, regs)
    v_wrap  = gen_wrap_v(mod_wrap, mod_busif, mod_core, regs)

    write_text(fn_busif, v_busif)
    write_text(fn_core, v_core)
    write_text(fn_wrap, v_wrap)

    print("Generated:")
    print(f"    {fn_wrap}")
    print(f"    {fn_busif}")
    print(f"    {fn_core}")
    print(f"Registers: {len(regs)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
