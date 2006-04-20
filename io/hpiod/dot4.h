/*****************************************************************************\

  dot4.h - 1284.4 channel class 
 
  (c) 2005 Copyright Hewlett-Packard Development Company, LP

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

#ifndef _DOT4_H
#define _DOT4_H

enum DOT4_COMMAND
{
  DOT4_INIT = MLC_INIT,
  DOT4_OPEN_CHANNEL = MLC_OPEN_CHANNEL,
  DOT4_CLOSE_CHANNEL = MLC_CLOSE_CHANNEL,
  DOT4_CREDIT = MLC_CREDIT,
  DOT4_CREDIT_REQUEST = MLC_CREDIT_REQUEST,
  DOT4_GET_SOCKET = 0x9,
  DOT4_GET_SERVICE = 0xa,
  DOT4_EXIT = MLC_EXIT,
  DOT4_ERROR = MLC_ERROR
};

#pragma pack(1)

typedef struct
{
   unsigned char psid;   /* primary socket id (ie: host) */
   unsigned char ssid;   /* secondary socket id (ie: peripheral) */
   unsigned short length;   /* packet length (includes header) */ 
   unsigned char credit;   /* data packet credit, reserved if command */
   unsigned char control;  /* bit field: 0=normal */
} DOT4Header;

typedef struct
{
   DOT4Header h;
   unsigned char cmd;
   unsigned char rev;
} DOT4Init;

typedef struct
{
   DOT4Header h;
   unsigned char cmd;
   unsigned char result;
   unsigned char rev;
} DOT4InitReply;

typedef struct
{
   DOT4Header h;
   unsigned char cmd;
} DOT4Exit;

typedef struct
{
   DOT4Header h;
   unsigned char cmd;
   unsigned char result;
} DOT4ExitReply;

typedef struct
{
   DOT4Header h;
   unsigned char cmd;
   unsigned char psocket;      /* primary socket id */
   unsigned char ssocket;      /* secondary socket id */
   unsigned short maxp2s;      /* max primary to secondary packet size in bytes */
   unsigned short maxs2p;      /* max secondary to primary packet size in bytes */
   unsigned short maxcredit;   /* max outstanding credit */
} DOT4OpenChannel;

typedef struct
{
   DOT4Header h;
   unsigned char cmd;
   unsigned char result;
   unsigned char psocket;
   unsigned char ssocket;
   unsigned short maxp2s;      /* max primary to secondary packet size in bytes */
   unsigned short maxs2p;      /* max secondary to primary packet size in bytes */
   unsigned short maxcredit;   /* max outstanding credit */
   unsigned short credit;
} DOT4OpenChannelReply;

typedef struct
{
   DOT4Header h;
   unsigned char cmd;
   unsigned char psocket;      /* primary socket id */
   unsigned char ssocket;      /* secondary socket id */
} DOT4CloseChannel;

typedef struct
{
   DOT4Header h;
   unsigned char cmd;
   unsigned char result;
   unsigned char psocket;      /* primary socket id */
   unsigned char ssocket;      /* secondary socket id */
} DOT4CloseChannelReply;

typedef struct
{
   DOT4Header h;
   unsigned char cmd;
   unsigned char result;
   unsigned char socket;
} DOT4GetSocketReply; 

typedef struct
{
   DOT4Header h;
   unsigned char cmd;
   unsigned char psocket;
   unsigned char ssocket;
   unsigned short credit;    /* credit for sender */ 
} DOT4Credit; 

typedef struct
{
   DOT4Header h;
   unsigned char cmd;
   unsigned char psocket;
   unsigned char ssocket;
   unsigned short maxcredit;   /* maximum outstanding credit */
} DOT4CreditRequest; 

typedef struct
{
   DOT4Header h;
   unsigned char cmd;
   unsigned char result;
   unsigned char psocket;
   unsigned char ssocket;
   unsigned short credit;   /* credit for sender */
} DOT4CreditRequestReply; 

typedef struct
{
   DOT4Header h;
   unsigned char cmd;
   unsigned char psocket;     /* primary socket id which contains the error */
   unsigned char ssocket;     /* secondary socket id which contains the error */
   unsigned char error;
} DOT4Error; 

typedef DOT4ExitReply DOT4Reply;
typedef DOT4Exit DOT4Cmd;
typedef DOT4CloseChannelReply DOT4CreditReply;
typedef DOT4Exit DOT4GetSocket;

#pragma pack()

#endif // _DOT4_H

