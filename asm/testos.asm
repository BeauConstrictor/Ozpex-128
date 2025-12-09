  .org $0200

TIMER =      $c001
SERIAL =     $c000

CLEAR =      $11

PRINT_INTERVAL = 250;ms

; memory allocation:
LAST_TIMER =  $50        ; 1 byte

reset:
  lda #PRINT_INTERVAL
  sta TIMER+1

  sta TIMER ; start timer

timer:
  ldy TIMER
  cpy LAST_TIMER
  beq timer

  jsr print
  sty LAST_TIMER
  
  lda SERIAL
  beq timer
  rts

print:
  ldx #0
_print_loop:
  lda message,x
  beq _print_done
  sta SERIAL
  inx
  jmp _print_loop
_print_done:
  rts

message:
  .byte "Hello, world!\n", 0