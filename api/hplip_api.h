/*****************************************************************************\

  hplip_api.h - hplip client interface
 
  (c) 2005-2006 Copyright Hewlett-Packard Development Company, LP

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

#ifndef hplip_api_INCLUDED
#define hplip_api_INCLUDED

#define HPLIP_RCFILE "/etc/hp/hplip.conf" /* The config file */
#define HPIODFILE "hpiod.port"
#define HPSSDFILE "hpssd.port"

#define HPLIP_LINE_SIZE 256 /* Length of buffer reads */
#define HPLIP_BUFFER_SIZE 4096
#define HPLIP_HEADER_SIZE 4096   /* Rough estimate for message header */
#define HPLIP_EXCEPTION_TIMEOUT 45  /* seconds */

enum HPLIP_RESULT_CODE
{
   R_AOK = 0,
   R_INVALID_DESCRIPTOR = 3,
   R_INVALID_URI = 4,
   R_INVALID_MESSAGE = 5,
   R_INVALID_LENGTH = 8,
   R_IO_ERROR = 12,
   R_INVALID_CHANNEL_ID = 30,
   R_CHANNEL_BUSY = 31,
};

enum HPLIP_IO_MODE
{
   UNI_MODE=0, /* uni-di */
   RAW_MODE,   /* bi-di */
   MLC_MODE,
   DOT4_MODE
};

enum HPLIP_FLOW_CONTROL
{
   GUSHER=0,
   MISER
};

enum HPLIP_SCAN_PORT
{
   SCAN_PORT0=0,
   SCAN_PORT1
};

typedef struct
{
   char cmd[HPLIP_LINE_SIZE];
   int prt_mode; 
   int mfp_mode;         
   int flow_ctl;
   int scan_port;
   int descriptor;       /* device descriptor (device-id) */
   int length;           /* length of data in bytes */
   int result;
   int channel;          /* channel descriptor (channel-id) */
   int writelen;           /* bytes-written */
   int readlen;          /* bytes-to-read */
   int ndevice;
   int scantype;
   int type;
   int pmlresult;
   unsigned char status;   /* 8-bit device status */
   unsigned char *data;           /* pointer to data */
} HplipMsgAttributes;

typedef struct
{
   int hpiod_socket;
   int hpssd_socket;
} HplipSession;

#ifdef __cplusplus
extern "C" {
#endif

int hplip_GetPair(char *buf, char *key, char *value, char **tail);
int hplip_ParseMsg(char *buf, int len, HplipMsgAttributes *ma);
int hplip_GetModel(char *id, char *buf, int bufSize);
int hplip_GetURIModel(char *uri, char *buf, int bufSize);
int hplip_GetURIDataLink(char *uri, char *buf, int bufSize);
int hplip_ModelQuery(char *uri, HplipMsgAttributes *ma);
int hplip_GetModelAttributes(char *model, char *attr, int attrSize);

int hplip_OpenHP(HplipSession *session, char *dev, HplipMsgAttributes *ma);
int hplip_CloseHP(HplipSession *session, int hd);
int hplip_WriteHP(HplipSession *session, int hd, int channel, char *buf, int size);
int hplip_ReadHP(HplipSession *session, int hd, int channel, char *buf, int size, int timeout);
int hplip_OpenChannel(HplipSession *session, int hd, char *sni);
int hplip_CloseChannel(HplipSession *session, int hd, int channel);
int hplip_GetID(HplipSession *session, int hd, char *buf, int bufSize);
int hplip_GetStatus(HplipSession *session, int hd, char *buf, int size);
int hplip_Init(HplipSession **session);
int hplip_Exit(HplipSession *session);

int bug(const char *fmt, ...);

#ifdef __cplusplus
}
#endif

#endif       /* hplip_api_INCLUDED */
