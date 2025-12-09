# === CONFIG ===
ASM_SRC := $(wildcard asm/*.asm)
BIN_DIR := bin
BIN_OUT := $(patsubst asm/%.asm,$(BIN_DIR)/%,$(ASM_SRC))

VASM := ./vasm6502_oldstyle
VFLAGS := -Fbin -dotdir -esc -chklabels

define NOTFOUNDMSG
fatal: could not find '$(VASM)' in the current dir.
you can find vasm here: http://sun.hasenbraten.de/vasm/index.php?view=binrel


endef

ifeq (,$(wildcard $(VASM)))
$(error $(NOTFOUNDMSG))
endif

all: $(BIN_DIR) $(BIN_OUT)

$(BIN_DIR):
	mkdir -p $(BIN_DIR)

$(BIN_DIR)/%: asm/%.asm
	$(VASM) $(VFLAGS) -o $@ $<

clean:
	rm -f $(BIN_DIR)/*
