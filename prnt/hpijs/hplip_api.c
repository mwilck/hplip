/*****************************************************************************\

  hplip_api.c - hplip client interface 
 
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

#include <sys/types.h>
#include <sys/stat.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <netdb.h>
#include <stdio.h>
#include <stdlib.h>
#include <fcntl.h>
#include <string.h>
#include <unistd.h>
#include <stdarg.h>
#include <syslog.h>
#include "hplip_api.h"

static int hpiod_port_num = 50000;
static int hpssd_port_num = 50002;
int hpiod_socket=-1;
int hpssd_socket=-1;
int jdprobe=0;

int ReadConfig()
{
   char rcbuf[255];
   char section[32];
   char rundir[255];
   char file[255];
   FILE *inFile = NULL;
   char *tail;
   int n, stat=1;
        
   if((inFile = fopen(RCFILE, "r")) == NULL) 
   {
      bug("unable to open %s: %m: %s %d\n", RCFILE, __FILE__, __LINE__);
      goto bugout;
   } 

   section[0] = 0;

   /* Read the config file */
   while ((fgets(rcbuf, sizeof(rcbuf), inFile) != NULL))
   {
      if (rcbuf[0] == '[')
         strncpy(section, rcbuf, sizeof(section)); /* found new section */
      else if ((strncasecmp(section, "[hplip]", 7) == 0) && (strncasecmp(rcbuf, "jdprobe=", 8) == 0))
         jdprobe = strtol(rcbuf+8, &tail, 10);
      else if ((strncasecmp(section, "[dirs]", 6) == 0) && (strncasecmp(rcbuf, "run=", 4) == 0))
      {
         strncpy(rundir, rcbuf+4, sizeof(rundir));
         n = strlen(rundir);
         rundir[n-1]=0;  /* remove CR */
      }
   }
        
   fclose(inFile);

   snprintf(file, sizeof(file), "%s/%s", rundir, HPIODFILE); 
   if((inFile = fopen(file, "r")) == NULL) 
   {
      bug("unable to open %s: %m: %s %d\n", file, __FILE__, __LINE__);
      goto bugout;
   } 
   if (fgets(rcbuf, sizeof(rcbuf), inFile) != NULL)
      hpiod_port_num = strtol(rcbuf, &tail, 10);
   fclose(inFile);

   snprintf(file, sizeof(file), "%s/%s", rundir, HPSSDFILE); 
   if((inFile = fopen(file, "r")) == NULL) 
   {
      bug("unable to open %s: %m: %s %d\n", file, __FILE__, __LINE__);
      goto bugout;
   } 
   if (fgets(rcbuf, sizeof(rcbuf), inFile) != NULL)
      hpssd_port_num = strtol(rcbuf, &tail, 10);

   stat = 0;

bugout:        
   if (inFile != NULL)
      fclose(inFile);
         
   return stat;
}

int GetPair(char *buf, char *key, char *value, char **tail)
{
   int i=0, j;

   key[0] = 0;
   value[0] = 0;

   if (buf[i] == '#')
   {
      for (; buf[i] != '\n' && i < HEADER_SIZE; i++);  /* eat comment line */
      i++;
   }

   if (strncasecmp(&buf[i], "data:", 5) == 0)
   {
      strcpy(key, "data:");   /* "data:" key has no value */
      i+=5;
   }   
   else
   {
      j = 0;
      while ((buf[i] != '=') && (i < HEADER_SIZE) && (j < LINE_SIZE))
         key[j++] = buf[i++];
      for (j--; key[j] == ' ' && j > 0; j--);  /* eat white space before = */
      key[++j] = 0;

      for (i++; buf[i] == ' ' && i < HEADER_SIZE; i++);  /* eat white space after = */

      j = 0;
      while ((buf[i] != '\n') && (i < HEADER_SIZE) && (j < LINE_SIZE))
         value[j++] = buf[i++];
      for (j--; value[j] == ' ' && j > 0; j--);  /* eat white space before \n */
      value[++j] = 0;
   }

   i++;   /* bump past '\n' */

   if (tail != NULL)
      *tail = buf + i;  /* tail points to next line */

   return i;
}

//hplip_ParseMsg
//!  Parse and convert all key value pairs in message. Do sanity check on values.
/*!
******************************************************************************/
int hplip_ParseMsg(char *buf, int len, MsgAttributes *ma)
{
   char key[LINE_SIZE];
   char value[LINE_SIZE];
   char *tail, *tail2;
   int i, ret=R_AOK;

   ma->cmd[0] = 0;
   ma->prt_mode = UNI_MODE;
   ma->mfp_mode = MLC_MODE;
   ma->flow_ctl = GUSHER;
   ma->scan_port = SCAN_PORT0;
   ma->descriptor = -1;
   ma->length = 0;
   ma->channel = -1;
   ma->data = NULL;
   ma->result = -1;
   ma->writelen = 0;
   ma->readlen = 0;
   ma->status = 0;

   if (buf == NULL)
      return R_AOK;    /* initialize ma */

   i = GetPair(buf, key, value, &tail);
   if (strcasecmp(key, "msg") != 0)
   {
      bug("invalid message: %s: %s %d \n", key, __FILE__, __LINE__);
      return R_INVALID_MESSAGE;
   }
   strncpy(ma->cmd, value, sizeof(ma->cmd));

   while (i < len)
   {
      i += GetPair(tail, key, value, &tail);

      if (strcasecmp(key, "device-id") == 0)
      {
         ma->descriptor = strtol(value, &tail2, 10);
         if (ma->descriptor < 0)
         {
            bug("invalid device descriptor: %d: %s %d\n", ma->descriptor, __FILE__, __LINE__);
            ret = R_INVALID_DESCRIPTOR;
            break;
         }
      }
      else if (strcasecmp(key, "channel-id") == 0)
      {
         ma->channel = strtol(value, &tail2, 10);
         if (ma->channel < 0)
         {
            bug("invalid channel descriptor: %d: %s %d\n", ma->channel, __FILE__, __LINE__);
            ret = R_INVALID_CHANNEL_ID;
            break;
         }
      }
      else if (strcasecmp(key, "length") == 0)
      {
         ma->length = strtol(value, &tail2, 10);
         if (ma->length > BUFFER_SIZE)
         {
            bug("invalid data length: %d: %s %d\n", ma->length, __FILE__, __LINE__);
            ret = R_INVALID_LENGTH;
         }
      }
      else if (strcasecmp(key, "data:") == 0)
      {
         ma->data = (unsigned char *)tail;
         break;  /* done parsing */
      }
      else if (strcasecmp(key, "result-code") == 0)
      {
         ma->result = strtol(value, &tail2, 10);
      }
      else if (strcasecmp(key, "bytes-written") == 0)
      {
         ma->writelen = strtol(value, &tail2, 10);
      }
      else if (strcasecmp(key, "bytes-to-read") == 0)
      {
         ma->readlen = strtol(value, &tail2, 10);
         if (ma->readlen > BUFFER_SIZE)
         {
            bug("invalid read length: %d: %s %d\n", ma->readlen, __FILE__, __LINE__);
            ret = R_INVALID_LENGTH;
         }
      }
      else if (strcasecmp(key, "status-code") == 0)
      {
         ma->status = strtol(value, &tail2, 10);
      }
      else if (strcasecmp(key, "io-mode") == 0)
      {
         ma->prt_mode = strtol(value, &tail2, 10);      /* uni | raw | mlc */
      }
      else if (strcasecmp(key, "io-mfp-mode") == 0)
      {
         ma->mfp_mode = strtol(value, &tail2, 10);      /* mfc | dot4 */
      }
      else if (strcasecmp(key, "io-scan-port") == 0)
      {
         ma->scan_port = strtol(value, &tail2, 10);      /* normal | CLJ28xx */
      }
      else if (strcasecmp(key, "io-control") == 0)
      {
         ma->flow_ctl = strtol(value, &tail2, 10);     /* gusher | miser */
      }
      else if( strcasecmp( key, "num-devices" ) == 0 )
      {
         ma->ndevice = strtol( value, &tail2, 10 );
      }
      else if( strcasecmp( key, "scan-type" ) == 0 )
      {
         ma->scantype = strtol( value, &tail2, 10 );
      }
      else if( strcasecmp( key, "type" ) == 0 )
      {
         ma->type = strtol( value, &tail2, 10 );
      }
      else if( strcasecmp( key, "pml-result-code" ) == 0 )
      {
         ma->pmlresult = strtol( value, &tail2, 10 );
      }
      else
      {
         /* Unknown keys are ignored (R_AOK). */
//         bug("invalid key:%s\n", key);
      }
   }  // end while (i < len)

   return ret;
}

//GetModel
//! Parse the model from the IEEE 1284 device id string.
/*!
******************************************************************************/
int hplip_GetModel(char *id, char *buf, int bufSize)
{
   char *pMd;
   int i, j, dd=0;

   buf[0] = 0;

   if ((pMd = strstr(id, "MDL:")) != NULL)
      pMd+=4;
   else if ((pMd = strstr(id, "MODEL:")) != NULL)
      pMd+=6;
   else
      return 0;

   for (i=0; pMd[i] == ' ' && i < bufSize; i++);  /* eat leading white space */

   for (j=0; (pMd[i] != ';') && (i < bufSize); i++)
   {
      if (pMd[i]==' ' || pMd[i]=='/')
      {
         /* Remove double spaces. */
         if (!dd)
         { 
            buf[j++] = '_';   /* convert space to "_" */
            dd=1;              
         }
      }
      else
      {
         buf[j++] = pMd[i];
         dd=0;       
      }
   }

   for (j--; buf[j] == '_' && j > 0; j--);  /* eat trailing white space */

   buf[++j] = 0;

   return j;    /* return size does not include zero terminator */
}

//GetURIModel
//! Parse the model from a uri string.
/*!
******************************************************************************/
int hplip_GetURIModel(char *uri, char *buf, int bufSize)
{
   char *p;
   int i;

   buf[0] = 0;

   if ((p = strstr(uri, "/")) == NULL)
      return 0;
   if ((p = strstr(p+1, "/")) == NULL)
      return 0;
   p++;

   for (i=0; (p[i] != '?') && (i < bufSize); i++)
      buf[i] = p[i];

   buf[i] = 0;

   return i;
}

//ModelQuery
//!  Request ModelQuery from hpssd.
/*!
******************************************************************************/
int hplip_ModelQuery(char *uri, MsgAttributes *ma)
{
   char message[HEADER_SIZE];  
   char model[128];
   int len=0,stat=1;

   hplip_ParseMsg(NULL, 0, ma);  /* set ma defaults */

   if (hpssd_socket < 0)
      goto bugout;  

   len = hplip_GetURIModel(uri, model, sizeof(model));

   len = sprintf(message, "msg=ModelQuery\nmodel=%s\n", model);

   if (send(hpssd_socket, message, len, 0) == -1) 
   {  
      bug("unable to send ModelQuery: %m: %s %d\n", __FILE__, __LINE__);  
      goto bugout;  
   }  

   if ((len = recv(hpssd_socket, message, sizeof(message), 0)) == -1) 
   {  
      bug("unable to receive ModelQueryResult: %m: %s %d\n", __FILE__, __LINE__);  
      goto bugout;
   }  

   message[len] = 0;

   hplip_ParseMsg(message, len, ma);

   if (ma->result != R_AOK)
   {  
      bug("invalid ModelQueryResult: %s %s %d\n", message, __FILE__, __LINE__);  
      goto bugout;
   }  

   stat=0;

bugout:

   return stat;
}

int hplip_OpenHP(char *dev, MsgAttributes *mai)
{
   char message[512];  
   int len=0, fd=-1;
   MsgAttributes ma;
 
   if (hpiod_socket < 0)
      goto bugout;  

   len = sprintf(message, "msg=DeviceOpen\ndevice-uri=%s\nio-mode=%d\nio-control=%d\nio-mfp-mode=%d\nio-scan-port=%d\n", dev, mai->prt_mode, mai->flow_ctl, mai->mfp_mode, mai->scan_port);
 
   if (send(hpiod_socket, message, len, 0) == -1) 
   {  
      bug("unable to send DeviceOpen: %m: %s %d\n", __FILE__, __LINE__);  
      goto bugout;  
   }  

   if ((len = recv(hpiod_socket, message, sizeof(message), 0)) == -1) 
   {  
      bug("unable to receive DeviceOpenResult: %m: %s %d\n", __FILE__, __LINE__);  
      goto bugout;
   }  

   message[len] = 0;

   hplip_ParseMsg(message, len, &ma);
   if (ma.result == R_AOK)
      fd = ma.descriptor;

bugout:

   return fd;
}

int hplip_WriteHP(int hd, int channel, char *buf, int size)
{
   char message[BUFFER_SIZE+256];  
   int len=0, slen=0;
   MsgAttributes ma;
 
   len = sprintf(message, "msg=ChannelDataOut\ndevice-id=%d\nchannel-id=%d\nlength=%d\ndata:\n", hd, channel, size);
   if (size+len > sizeof(message))
   {  
      bug("unable to fill data buffer: size=%d: %s %d\n", size, __FILE__, __LINE__);  
      goto mordor;  
   }  

   memcpy(message+len, buf, size);
  
   if (send(hpiod_socket, message, size+len, 0) == -1) 
   {  
      bug("unable to send ChannelDataOut: %m: %s %d\n", __FILE__, __LINE__);  
      goto mordor;  
   }  

   if ((len = recv(hpiod_socket, message, sizeof(message), 0)) == -1) 
   {  
      bug("unable to receive ChannelDataOutResult: %m: %s %d\n", __FILE__, __LINE__);  
      goto mordor;
   }  

   message[len] = 0;
   hplip_ParseMsg(message, len, &ma);

   slen = ma.writelen;

mordor:

   return slen;
}

int hplip_ReadHP(int hd, int channel, char *buf, int size, int timeout)
{
   char message[BUFFER_SIZE+256];  
   int len=0, rlen=0;
   MsgAttributes ma;
 
   len = sprintf(message, "msg=ChannelDataIn\ndevice-id=%d\nchannel-id=%d\nbytes-to-read=%d\ntimeout=%d\n", hd, channel, size, timeout);  /* timeout = seconds */
   if (size+len > sizeof(message))
   {  
      fprintf(stderr, "Error data size=%d\n", size);  
      goto mordor;  
   }  

   if (send(hpiod_socket, message, len, 0) == -1) 
   {  
      syslog(LOG_ERR, "unable to send ChannelDataIn: %m\n");  
      goto mordor;  
   }  

   if ((len = recv(hpiod_socket, message, sizeof(message), 0)) == -1) 
   {  
      syslog(LOG_ERR, "unable to receive ChannelDataInResult: %m\n");  
      goto mordor;
   }  

   message[len] = 0;

   hplip_ParseMsg(message, len, &ma);

   if (ma.result == 0)
   {  
      rlen = ma.length;
      memcpy(buf, ma.data, rlen);
   }

mordor:

   return rlen;
}

int hplip_OpenChannel(int hd, char *sn)
{
   char message[512];  
   int len=0, channel=-1;
   MsgAttributes ma;

   len = sprintf(message, "msg=ChannelOpen\ndevice-id=%d\nservice-name=%s\n", hd, sn);

   if (send(hpiod_socket, message, len, 0) == -1) 
   {  
      bug("unable to send ChannelOpen: %m: %s %d\n", __FILE__, __LINE__);  
      goto mordor;  
   }  

   if ((len = recv(hpiod_socket, message, sizeof(message), 0)) == -1) 
   {  
      bug("unable to receive ChannelOpenResult: %m: %s %d\n", __FILE__, __LINE__);  
      goto mordor;
   }  

   message[len] = 0;

   hplip_ParseMsg(message, len, &ma);
   if (ma.result == R_AOK)
      channel = ma.channel;

mordor:

   return channel;
}

int hplip_CloseChannel(int hd, int channel)
{
   char message[512];  
   int len=0;

   len = sprintf(message, "msg=ChannelClose\ndevice-id=%d\nchannel-id=%d\n", hd, channel);
 
   if (send(hpiod_socket, message, len, 0) == -1) 
   {  
      bug("unable to send ChannelClose: %m: %s %d\n", __FILE__, __LINE__);  
      goto mordor;  
   }  

   if ((len = recv(hpiod_socket, message, sizeof(message), 0)) == -1) 
   {  
      bug("unable to receive ChannelCloseResult: %m: %s %d\n", __FILE__, __LINE__);  
      goto mordor;
   }  

   message[len] = 0;

mordor:

   return 0;
}

int hplip_CloseHP(int hd)
{
   char message[512];  
   int len=0;
 
   len = sprintf(message, "msg=DeviceClose\ndevice-id=%d\n", hd);
 
   if (send(hpiod_socket, message, len, 0) == -1) 
   {  
      bug("unable to send DeviceClose: %m: %s %d\n", __FILE__, __LINE__);  
      goto mordor;  
   }  

   if ((len = recv(hpiod_socket, message, sizeof(message), 0)) == -1) 
   {  
      bug("unable to receive DeviceCloseResult: %m: %s %d\n", __FILE__, __LINE__);  
      goto mordor;
   }  

   message[len] = 0;

mordor:
   return 0;
}

/* Get device id string. Assume binary length value at begining of string has been removed. */
int hplip_GetID(int hd, char *buf, int bufSize)
{
   char message[1024+512];
   int len=0;  
   MsgAttributes ma;
 
   buf[0] = 0;

   len = sprintf(message, "msg=DeviceID\ndevice-id=%d\n", hd);
 
   if (send(hpiod_socket, message, len, 0) == -1) 
   {  
      bug("unable to send DeviceID: %m: %s %d\n", __FILE__, __LINE__);  
      goto mordor;  
   }  

   if ((len = recv(hpiod_socket, buf, bufSize, 0)) == -1) 
   {  
      bug("unable to receive DeviceIDResult: %m: %s %d\n", __FILE__, __LINE__);  
      goto mordor;
   }  

   hplip_ParseMsg(buf, len, &ma);
   if (ma.result == R_AOK)
   {
      len = ma.length < bufSize ? ma.length : bufSize-1;
      memcpy(buf, ma.data, len);
      buf[len] = 0;       /* zero terminate */
   }
   else
      len = 0;   /* error */

mordor:

   return len;         /* length does not include zero termination */
}  
 
int hplip_GetStatus(int hd, char *buf, int size)
{
   char message[512];  
   int len=0;  
   MsgAttributes ma;
 
   buf[0] = 0;

   len = sprintf(message, "msg=DeviceStatus\ndevice-id=%d\n", hd);
 
   if (send(hpiod_socket, message, len, 0) == -1) 
   {  
      bug("unable to send DeviceStatus: %m: %s %d\n", __FILE__, __LINE__);  
      goto mordor;  
   }  

   if ((len = recv(hpiod_socket, message, sizeof(message), 0)) == -1) 
   {  
      bug("unable to receive DeviceStatusResult: %m: %d %d\n", __FILE__, __LINE__);  
      goto mordor;
   }  

   message[len] = 0;

   hplip_ParseMsg(message, len, &ma);
   if (ma.result == R_AOK)
   {
      len = 1;
      buf[0] = ma.status;
   }
   else
      len = 0;   /* error */

mordor:

   return len;
}  

int hplip_Init(void)
{
   struct sockaddr_in pin;  
   int stat=1;

   if (hpiod_socket >= 0 || hpssd_socket >= 0)    
   {
      bug("invalid state sockets are already open: %s %d\n", __FILE__, __LINE__);
      goto bugout;
   }

   ReadConfig();

   bzero(&pin, sizeof(pin));  
   pin.sin_family = AF_INET;  
   pin.sin_addr.s_addr = htonl(INADDR_LOOPBACK);
   pin.sin_port = htons(hpiod_port_num);  

   if ((hpiod_socket = socket(AF_INET, SOCK_STREAM, 0)) == -1) 
   {  
      bug("unable to create hpiod socket %d: %m: %s %d\n", hpiod_port_num, __FILE__, __LINE__);
      goto bugout;  
   }  
    
   if (connect(hpiod_socket, (void *)&pin, sizeof(pin)) == -1)  
   {  
      bug("unable to connect hpiod socket %d: %m: %s %d\n", hpiod_port_num, __FILE__, __LINE__);
      goto bugout;  
   }  

   bzero(&pin, sizeof(pin));  
   pin.sin_family = AF_INET;  
   pin.sin_addr.s_addr = htonl(INADDR_LOOPBACK);
   pin.sin_port = htons(hpssd_port_num);  
    
   if ((hpssd_socket = socket(AF_INET, SOCK_STREAM, 0)) == -1) 
   {  
      bug("unable to create hpssd socket %d: %m: %s %d\n", hpssd_port_num, __FILE__, __LINE__);
      goto bugout;  
   }  

   if (connect(hpssd_socket, (void *)&pin, sizeof(pin)) == -1)  
   {  
      bug("unable to connect hpssd socket %d: %m: %s %d\n", hpssd_port_num, __FILE__, __LINE__);
      goto bugout;  
   }  
  
   stat = 0;

bugout:
   return stat;
}

int hplip_Exit(void)
{
    if (hpiod_socket >= 0)
    {
       close(hpiod_socket);
       hpiod_socket = -1;  
    }
    if (hpssd_socket >= 0)
    {
       close(hpssd_socket);
       hpssd_socket = -1;
    }
    return 0;
}
