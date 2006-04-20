/*****************************************************************************\

  mlc.h - MLC channel class 
 
  (c) 2004 Copyright Hewlett-Packard Development Company, LP

  Permission is hereby granted, free of charge, to any person obtaining a copy 
  of this software and associated documentation files (the "Software"), to deal 
  in the Software without restriction, including without limitation the rights 
  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies 
  of the Software, and to permit persons to whom the Software is furnished to do 
  so, subject to the following conditions:

  The above copyright notice and this permission notice shall be included in all
  copies or substantial portions of the Software.

  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR 
  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS 
  FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR 
  COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER 
  IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION 
  WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

\*****************************************************************************/

#ifndef _MLC_H
#define _MLC_H

enum MLC_COMMAND
{
  MLC_INIT = 0,
  MLC_OPEN_CHANNEL = 1,
  MLC_CLOSE_CHANNEL = 2,
  MLC_CREDIT = 3,
  MLC_CREDIT_REQUEST = 4,
  MLC_DEBIT = 5,
  MLC_DEBIT_REQUEST = 6,
  MLC_CONFIG_SOCKET = 7,
  MLC_EXIT = 8,
  MLC_ERROR = 0x7f
};

#pragma pack(1)

typedef struct
{
   unsigned char hsid;   /* host socket id */
   unsigned char psid;   /* peripheral socket id */
   unsigned short length;   /* packet length (includes header) */ 
   unsigned char credit;   /* data packet credit, reserved if command */
   unsigned char status;  /* upper layer status */
} MLCHeader;

typedef struct
{
   MLCHeader h;
   unsigned char cmd;
   unsigned char rev;
} MLCInit;

typedef struct
{
   MLCHeader h;
   unsigned char cmd;
   unsigned char result;
   unsigned char rev;
} MLCInitReply;

typedef struct
{
   MLCHeader h;
   unsigned char cmd;
} MLCExit;

typedef struct
{
   MLCHeader h;
   unsigned char cmd;
   unsigned char result;
} MLCExitReply;

typedef struct
{
   MLCHeader h;
   unsigned char cmd;
   unsigned char socket;      /* socket id */
   unsigned short h2psize;    /* host-to-peripheral packet size */
   unsigned short p2hsize;    /* peripheral-to-host packet size */
   unsigned char status;      /* status level */
} MLCConfigSocket;

typedef struct
{
   MLCHeader h;
   unsigned char cmd;
   unsigned char result;
   unsigned short h2psize;    /* host-to-peripheral packet size */
   unsigned short p2hsize;    /* peripheral-to-host packet size */
   unsigned char status;      /* status level */
} MLCConfigSocketReply;

typedef struct
{
   MLCHeader h;
   unsigned char cmd;
   unsigned char hsocket;      /* host socket id */
   unsigned char psocket;      /* peripheral socket id */
   unsigned short credit;
} MLCOpenChannel;

typedef struct
{
   MLCHeader h;
   unsigned char cmd;
   unsigned char result;
   unsigned short credit;
} MLCOpenChannelReply;

typedef struct
{
   MLCHeader h;
   unsigned char cmd;
   unsigned char hsocket;      /* host socket id */
   unsigned char psocket;      /* peripheral socket id */
} MLCCloseChannel;

typedef MLCExitReply MLCCloseChannelReply;
typedef MLCExitReply MLCReply;
typedef MLCExit MLCCmd;
typedef MLCOpenChannel MLCCredit;
typedef MLCExitReply MLCCreditReply;
typedef MLCOpenChannel MLCCreditRequest;
typedef MLCOpenChannelReply MLCCreditRequestReply;
typedef MLCExitReply MLCError;

#pragma pack()

#endif // _MLC_H

