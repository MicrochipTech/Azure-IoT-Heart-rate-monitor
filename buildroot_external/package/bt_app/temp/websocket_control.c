/*
 * Copyright (c) 2014 Putilov Andrey
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in
 * all copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
 * THE SOFTWARE.
 *
 */

#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <unistd.h>
#include <pthread.h>
#include <fcntl.h>
#include <errno.h>

#include "websocket_protocol.h"

#define PORT 8088
#define BUF_LEN 0xFFFF
//#define PACKET_DUMP

uint8_t gBuffer[BUF_LEN];
extern volatile uint8_t data_ready;
volatile uint8_t connection_established = 0;
int clientSocket;
int listenSocket;

void SendDataToSocket(int clientSocket, char *SendString, uint8_t dataSize);
void CommandParser(char *pc);

void error(const char *msg) {
    perror(msg);
    exit(EXIT_FAILURE);
}

int safeSend(int clientSocket, const uint8_t *buffer, size_t bufferSize) {
#ifdef PACKET_DUMP
    printf("out packet:\n");
    fwrite(buffer, 1, bufferSize, stdout);
    printf("\n");
#endif
    ssize_t written = send(clientSocket, buffer, bufferSize, 0);
    if (written == -1) {
        close(clientSocket);
        perror("send failed");
        return EXIT_FAILURE;
    }
    if (written != bufferSize) {
        close(clientSocket);
        perror("written not all bytes");
        return EXIT_FAILURE;
    }

    return EXIT_SUCCESS;
}

void clientWorker(int clientSocket) {
    int err;
    ssize_t readed;

    memset(gBuffer, 0, BUF_LEN);
    size_t readedLength = 0;
    size_t frameSize = BUF_LEN;
    enum wsState state = WS_STATE_OPENING;
    uint8_t *data = NULL;
    size_t dataSize = 0;
    enum wsFrameType frameType = WS_INCOMPLETE_FRAME;
    struct handshake hs;
    nullHandshake(&hs);

#define prepareBuffer frameSize = BUF_LEN; memset(gBuffer, 0, BUF_LEN);
#define initNewFrame frameType = WS_INCOMPLETE_FRAME; readedLength = 0; memset(gBuffer, 0, BUF_LEN);

    while (frameType == WS_INCOMPLETE_FRAME) {
        do {
            errno = 0;
            readed = recv(clientSocket, gBuffer + readedLength, BUF_LEN - readedLength, 0);
            err = errno;
        } while (err == EAGAIN);

        if (!readed) {
            close(clientSocket);
            perror("recv failed...");
            return;
        }
#ifdef PACKET_DUMP
        printf("in packet:\n");
        fwrite(gBuffer, 1, readed, stdout);
        printf("\n");
#endif
        readedLength += readed;
        assert(readedLength <= BUF_LEN);

        if (state == WS_STATE_OPENING) {
            frameType = wsParseHandshake(gBuffer, readedLength, &hs);
        } else {
            frameType = wsParseInputFrame(gBuffer, readedLength, &data, &dataSize);
        }

        if ((frameType == WS_INCOMPLETE_FRAME && readedLength == BUF_LEN) || frameType == WS_ERROR_FRAME) {
            if (frameType == WS_INCOMPLETE_FRAME) {
                printf("buffer too small");
            } else {
                printf("error in incoming frame\n");
            }

            if (state == WS_STATE_OPENING) {
                prepareBuffer;
                frameSize = sprintf((char *) gBuffer,
                        "HTTP/1.1 400 Bad Request\r\n"
                        "%s%s\r\n\r\n",
                        versionField,
                        version);
                safeSend(clientSocket, gBuffer, frameSize);
                break;
            } else {
                prepareBuffer;
                wsMakeFrame(NULL, 0, gBuffer, &frameSize, WS_CLOSING_FRAME);
                if (safeSend(clientSocket, gBuffer, frameSize) == EXIT_FAILURE)
                    break;
                state = WS_STATE_CLOSING;
                initNewFrame;
            }
        }

        if (state == WS_STATE_OPENING) {
            assert(frameType == WS_OPENING_FRAME);
            if (frameType == WS_OPENING_FRAME) {
                // if resource is right, generate answer handshake and send it
                if (strcmp(hs.resource, "/echo") != 0) {
                    frameSize = sprintf((char *) gBuffer, "HTTP/1.1 404 Not Found\r\n\r\n");
                    safeSend(clientSocket, gBuffer, frameSize);
                    break;
                }

                prepareBuffer;
                wsGetHandshakeAnswer(&hs, gBuffer, &frameSize);
                freeHandshake(&hs);
                if (safeSend(clientSocket, gBuffer, frameSize) == EXIT_FAILURE)
                    break;
                state = WS_STATE_NORMAL;
                initNewFrame;
            }
        } else {
            if (frameType == WS_CLOSING_FRAME) {
                if (state == WS_STATE_CLOSING) {
                    break;
                } else {
                    prepareBuffer;
                    wsMakeFrame(NULL, 0, gBuffer, &frameSize, WS_CLOSING_FRAME);
                    safeSend(clientSocket, gBuffer, frameSize);
                    break;
                }
            } else if (frameType == WS_TEXT_FRAME) {
                uint8_t *recievedString = NULL;
                recievedString = malloc(dataSize + 1);
                assert(recievedString);
                memcpy(recievedString, data, dataSize);
                recievedString[ dataSize ] = 0;

                CommandParser((char *) recievedString);

                //prepareBuffer;
                //wsMakeFrame(recievedString, dataSize, gBuffer, &frameSize, WS_TEXT_FRAME);
                //free(recievedString);
                //if (safeSend(clientSocket, gBuffer, frameSize) == EXIT_FAILURE)
                //    break;
                initNewFrame;

            }
        }
    } // read/write cycle

    //close(clientSocket);
}

void SendDataToWebsocketClient(char *SendString, uint8_t dataSize) {
    if (connection_established == 1) {
        SendDataToSocket(clientSocket, SendString, dataSize);
    }
}

void SendDataToSocket(int clientSocket, char *SendString, uint8_t dataSize) {
    size_t frameSize = BUF_LEN;
    memset(gBuffer, 0, BUF_LEN);

    wsMakeFrame((uint8_t *) SendString, dataSize, gBuffer, &frameSize, WS_TEXT_FRAME);
    safeSend(clientSocket, gBuffer, frameSize);
}

int main(void) {
    int err;

    listenSocket = socket(AF_INET, SOCK_STREAM, 0);
    if (listenSocket == -1) {
        error("create socket failed");
    }

    /*
        int flags = fcntl(listenSocket, F_GETFL, 0);
        fcntl(listenSocket, F_SETFL, flags | O_NONBLOCK);

        flags = fcntl(listenSocket, F_GETFL, 0);
        if ((flags & O_NONBLOCK) == O_NONBLOCK) {
            printf("it's nonblocking\n");
        } else {
            printf("it's blocking.\n");
        }
     */

    int reuse = 1;
    if (setsockopt(listenSocket, SOL_SOCKET, SO_REUSEADDR, (const char*) &reuse, sizeof (reuse)) < 0)
        perror("setsockopt(SO_REUSEADDR) failed");

    struct sockaddr_in local;
    memset(&local, 0, sizeof (local));
    local.sin_family = AF_INET;
    local.sin_addr.s_addr = INADDR_ANY;
    local.sin_port = htons(PORT);
    if (bind(listenSocket, (struct sockaddr *) &local, sizeof (local)) == -1) {
        error("bind failed");
    }

    if (listen(listenSocket, 1) == -1) {
        error("listen failed");
    }
    printf("opened %s:%d\n", inet_ntoa(local.sin_addr), ntohs(local.sin_port));

    while (TRUE) {
        struct sockaddr_in remote;
        socklen_t sockaddrLen = sizeof (remote);
        do {
            errno = 0;
            clientSocket = accept(listenSocket, (struct sockaddr*) &remote, &sockaddrLen);
            err = errno;
        } while (err == EAGAIN);

        if (clientSocket == -1) {
            error("accept failed");
        }

        printf("connected %s:%d\n", inet_ntoa(remote.sin_addr), ntohs(remote.sin_port));
        connection_established = 1;
        clientWorker(clientSocket);
        connection_established = 0;
        printf("disconnected\n");
    }

    close(listenSocket);
    return 0;
}

void CloseTheWebsocket(void) {
    close(listenSocket);
}
char * str_map(char *s,char *m)
{
        while (*s++ == *m++);

        return --s;
}

void reboot_system(void)
{
  sleep(2);
  system("ifconfig wlan0 down");
  sleep(5);
  system("reboot");
}
void update_wpa_supp(char ssid[],char psk[])
{
  int fd=0,sz=0;
  fd = open("/etc/wpa_supplicant.conf", O_WRONLY | O_CREAT | O_TRUNC, 0777);
  if (fd < 0)
  {
     perror("r1");
     exit(1);
  }

  sz = write(fd, "ctrl_interface=/var/run/wpa_supplicant\n", strlen("ctrl_interface=/var/run/wpa_supplicant\n"));
  sz = write(fd, "ap_scan=1\n", strlen("ap_scan=1\n"));
  sz = write(fd, "network={\n", strlen("network={\n"));
  sz = write(fd, "ssid=", strlen("ssid="));
  sz = write(fd, ssid, strlen(ssid));
  sz = write(fd, "\n", strlen("\n"));
   printf( "psk=%s psklen=%d\n", psk,strlen(psk) );
  if(strlen(psk) > 3)
  {
  	sz = write(fd, "psk=", strlen("psk="));
  	sz = write(fd, psk, strlen(psk));
  	sz = write(fd, "\n", strlen("\n"));
  }else
  {
  	sz = write(fd, "key_mgmt=NONE\n", strlen("key_mgmt=NONE\n"));
  }
  
  sz = write(fd, "}\n", strlen("}\n"));
  close(fd);
}
void update_start_script()
{

  int fd=0,sz=0;
  char str[] = "#!/bin/sh\n case $1 in \n         start)\n                 sh /root/Start_STA.sh\n \
                 ;;\n        stop)\n                 ifconfig wlan0 down\n                 ;;\n esac\n exit 0\n";
  fd = open("/etc/init.d/S85start_wlan", O_WRONLY | O_CREAT | O_TRUNC, 0755);
  if (fd < 0)
  {
     perror("r1");
     exit(1);
  }
  sz = write(fd, str, strlen(str));
  close(fd);
}
void CommandParser(char *pc) {

   char s[] = "connect=connect&login=";
   char s1[] = "&password=";
   char s2[] = "&device-name=";
   char *token,*p;
   char ssid[32];
   char psk[64];
   char dev[32];
   char a='"';

    memset(ssid,0,32);
    memset(psk,0,64);
    memset(dev,0,32);

   /* get the first token */
   //token = strtok(str, s);
   p= str_map(pc, s);
  // printf( " p=%s\n", p );
   token = strchr(p,'&');
   strncpy(ssid,&a,1);                //storing special character " for wpa_supplicant formating
   strncpy(ssid+1,p,token-p);
   strncpy(ssid+(token-p)+1,&a,1);  //storing special character " for wpa_supplicant formating  
   ssid[(token-p)+2]='\0';

   printf( " ssid=%s\n", ssid );

   p=str_map(token, s1);
   token = strchr(p,'&');
   strncpy(psk,&a,1);                //storing special character " for wpa_supplicant formating
   strncpy(psk+1,p,token-p);
   strncpy(psk+(token-p)+1,&a,1);  //storing special character " for wpa_supplicant formating  
   psk[(token-p)+2]='\0';

   printf( " psk=%s\n", psk );
   p=str_map(token, s2);
  // printf( " p=%s\n", p );
   //token = strchr(p,'&');     
   strcpy(dev,p);
   dev[strlen(dev)]='\0';

   printf( " dev=%s\n", dev );
  
  update_wpa_supp(ssid,psk);
  update_start_script();  

  reboot_system();

}

