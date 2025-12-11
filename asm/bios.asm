  .org $e000

BOOT_LOADER = $0200 ; -> $02ff
SERIAL_PORT = $c000
DISK_SECTOR = $c003
DISK_SELECT = $c004
DISK_STATUS = $c005
DISK_DATA   = $c100

PRINT      =   $50

reset:
  jsr find_bootable_disk

  lda #<disk_found_msg
  sta PRINT
  lda #>disk_found_msg
  sta PRINT+1
  jsr print

  lda DISK_SELECT
  jsr hex_byte
  cpx #"0"
  beq skip_leading_zero
  stx SERIAL_PORT
skip_leading_zero:
  sty SERIAL_PORT
  
  lda #"."
  sta SERIAL_PORT
  lda #"\n"
  sta SERIAL_PORT
  sta SERIAL_PORT

  jsr load_bootloader  
  jmp BOOT_LOADER

find_bootable_disk:
  lda #0
  sta DISK_SELECT
_find_bootable_disk_loop:
  lda DISK_STATUS
  cmp #%00010100
  beq _find_bootable_disk_success
  inc DISK_SELECT
  bne _find_bootable_disk_loop
  lda #<disk_not_found_msg
  sta PRINT
  lda #>disk_not_found_msg
  sta PRINT+1
  jsr print
  jmp halt
_find_bootable_disk_success:
  rts

load_bootloader:
  lda #0
  sta DISK_SECTOR
  jsr busy_wait

  ldx #0
_load_bootloader_loop:
  lda DISK_DATA,x
  sta BOOT_LOADER,x
  inx
  bne _load_bootloader_loop

  rts

halt:
  jmp halt  


; wait until the current block device is not busy
; modifies: a
busy_wait:
  lda $c005     ; read the device status
  and #%00000010 ; check the busy flag
  bne busy_wait ; keep checking if the device is busy
  rts

; return (in a) the a register as hex
; modifies: a (duh)
hex_nibble:
  cmp #10
  bcc _hex_nibble_digit
  clc
  adc #"a" - 10
  rts
_hex_nibble_digit:
  adc #"0"
  rts

; return (in x & y) the a register as hex
; modifies: a, x, y
hex_byte:
  pha ; save the full value for later
  ; get just the MSN
  lsr
  lsr
  lsr
  lsr
  jsr hex_nibble
  tax ; but the hex char for the MSN in x

  pla ; bring back the full value
  and #$0f ; get just the LSN
  jsr hex_nibble
  tay ; but the hex char for the LSN in y

  rts

; write the address of a null-terminated string to PRINT
; modifies: a, y
print:
  ldy #0
_print_loop:
  lda (PRINT),y
  beq _print_done
  sta SERIAL_PORT
  iny
  jmp _print_loop
_print_done:
  rts


disk_not_found_msg:
  .byte "No boot device found.", 0
disk_found_msg:
  .byte "Booting disk ", 0

  .org $fffc
  .word reset