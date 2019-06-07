CROSS_COMPILE := arm-linux-gnueabi-

CC	:= $(CROSS_COMPILE)gcc

CFLAGS	:= -Wall -std=gnu11 -g -D_REENTRANT

SRC	:= websocket_control.c websocket_protocol.c
OBJ	:= $(SRC:.c=.o)

PROG	:= websocket
	
all: $(PROG)
	
$(PROG): $(OBJ)
	$(CC) -static $^ -o $@

clean:
	$(RM) $(PROG) $(OBJ)
