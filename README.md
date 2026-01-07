# GN-gen_reg_module

AXI4-Lite register block generator (CSV → Verilog)

- Language: Python
- Output: Verilog (AXI4-Lite register block)
- License: MIT

## Overview
This repository provides a **register block generation tool** for
AXI4-Lite based designs.

Register definitions are described in a CSV file, and the tool
automatically generates a complete AXI4-Lite compatible register block,
including:

- AXI4-Lite bus interface
- Register core
- Wrapper module

The generated RTL is intended for **verification and control register
implementation**, not for high-performance datapaths.

## Features
- CSV-based register definition
- AXI4-Lite slave interface (single outstanding transaction)
- Register-level access types:
  - RW (Read / Write)
  - RO (Read Only)
  - WO (Write Only)
  - W1C (Write-One-to-Clear)
- Automatic reset value initialization
- External register value reference ports
- Verilog-2001 compatible output
- Deterministic code generation (no templates at runtime)

## Generated Files
For a given base name (e.g. `gn_common_test`), the following files are generated:
```
<base>_reg_wrap.v
 ├─ <base>_reg_busif.v # AXI4-Lite bus interface
 └─ <base>_reg_core.v # Register core (CSV dependent)
```

## Module Responsibilities
- reg_busif
  - Implements AXI4-Lite protocol handling
  - Converts AXI transactions into simple read/write requests
  - Generates OKAY / SLVERR responses based on address hit

- reg_core
  - Implements register storage and access logic
  - One always block per register for write logic
  - Case-based read mux
  - Exposes register values for external RTL access

- reg_wrap
  - Thin wrapper connecting bus interface and register core
  - Exposes AXI4-Lite slave interface and register reference outputs

## Register Naming Rules
CSV register names are expected to follow this convention:
  - CSV name: REG_<NAME>
  - Internal register: r_REG_<NAME>
  - External reference output: w_REG_<NAME>_o

This avoids name duplication and clearly distinguishes:
  - storage (r_)
  - wire signals (w_)
  - logical register names (REG_)

## CSV Format
The register map is described in a CSV file with the following columns:

| Column | Description                            |
| ------ | -------------------------------------- |
| name   | Register name (e.g. `REG_CTRL`)        |
| offset | Byte offset (must be 4-byte aligned)   |
| access | Register access type (RW, RO, WO, W1C) |
| reset  | Reset value (hex or decimal)           |
| field  | Bit field name (for documentation)     |
| lsb    | Least significant bit                  |
| msb    | Most significant bit                   |
| desc   | Field description                      |

## Notes
  - Access type and reset value are register-level, not field-level
  - Bit fields are used for documentation and overlap checking only
  - All registers are assumed to be AXI_DATA_W wide

## Usage
Generate register block
``` powershell
py -3 gn_gen_reg.py regmap.csv --base gn_common_test --outdir ./src
```
## Parameters
- regmap.csv : Register definition CSV
- --base : Base name for generated modules/files
- --outdir : Output directory for generated Verilog

## Limitations
- Single outstanding AXI4-Lite transaction
- No field-level access control
- No RTL-side register write interface (read-only reference supported)
- No address decoding beyond exact match

These limitations are intentional to keep the generated RTL
simple, predictable, and easy to verify.

## Intended Use
- Verification DUTs
- Control/status register blocks
- Simulation environments
- FPGA/ASIC prototypes where simplicity is preferred over flexibility

## Licens
This project is licensed under the MIT License.
