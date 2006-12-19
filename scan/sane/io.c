/************************************************************************************\

  io.c - HP SANE backend for multi-function peripherals (libsane-hpaio)

  (c) 2001-2006 Copyright Hewlett-Packard Development Company, LP

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

  Contributing Authors: Don Welch, David Suffield 

\************************************************************************************/

#include <stdio.h>
#include <sys/types.h>
#include <sys/socket.h>
#include "hplip_api.h"
#include "common.h"
#include "pml.h"
#include "io.h"

HplipSession *hplip_session = NULL;

int SendScanEvent( char * device_uri, int event, char * type )
{
    char message[ HPLIP_BUFFER_SIZE ];

    int len = sprintf( message, "msg=Event\ndevice-uri=%s\nevent-code=%d\nevent-type=%s\n", 
        device_uri, event, type );

    if (send(hplip_session->hpssd_socket, message, len, 0) == -1) 
    {
       bug("SendScanEvent(): unable to send message: %m\n" );  
    }

    return 0;    
}

int GetPml(int hd, int channel, char *oid, char *buf, int size, int *result, int *type, int *pml_result)
{
   char message[HPLIP_BUFFER_SIZE+HPLIP_HEADER_SIZE];  
   int len=0, rlen=0;
   HplipMsgAttributes ma;

   *result = ERROR;
   *type = PML_TYPE_NULL_VALUE;
   *pml_result = PML_ERROR; 
 
   len = sprintf(message, "msg=GetPML\ndevice-id=%d\nchannel-id=%d\noid=%s\n", hd, channel, oid);

   if (send(hplip_session->hpiod_socket, message, len, 0) == -1) 
   {  
      bug("unable to send GetPML: %m\n");  
      goto mordor;  
   }  

   if ((len = recv(hplip_session->hpiod_socket, message, sizeof(message), 0)) == -1) 
   {  
      bug("unable to receive ChannelDataInResult: %m\n");  
      goto mordor;
   }  

   message[len] = 0;

   hplip_ParseMsg(message, len, &ma);

   if (ma.result == R_AOK)
   {  
      rlen = (ma.length > size) ? size : ma.length;
      memcpy(buf, ma.data, rlen);
      *result = OK;
      *type = ma.type;
      *pml_result = ma.pmlresult;
   }

mordor:

   return rlen;
}

int SetPml(int hd, int channel, char *oid, int type, char *buf, int size, int *result, int *pml_result)
{
   char message[HPLIP_BUFFER_SIZE+HPLIP_HEADER_SIZE];  
   int len=0, slen=0;
   HplipMsgAttributes ma;
 
   *result = ERROR;
   *pml_result = PML_ERROR; 

   len = sprintf(message, "msg=SetPML\ndevice-id=%d\nchannel-id=%d\noid=%s\ntype=%d\nlength=%d\ndata:\n", hd, channel, oid, type, size);
   if (size+len > sizeof(message))
   {  
      bug("unable to fill data buffer: size=%d: line %d\n", size, __LINE__);  
      goto mordor;  
   }  

   memcpy(message+len, buf, size);

   if (send(hplip_session->hpiod_socket, message, size+len, 0) == -1) 
   {  
      bug("unable to send SetPML: %m\n");  
      goto mordor;  
   }  

   if ((len = recv(hplip_session->hpiod_socket, message, sizeof(message), 0)) == -1) 
   {  
      bug("unable to receive SetPMLResult: %m\n");  
      goto mordor;
   }  

   message[len] = 0;

   hplip_ParseMsg(message, len, &ma);

   if (ma.result == R_AOK)
   {  
      slen = size;
      *result = OK;
      *pml_result = ma.pmlresult;
   }

mordor:

   return slen;
}

/* Read full requested data length in BUFFER_SIZE chunks. Return number of bytes read. */
int ReadChannelEx(int deviceid, int channelid, unsigned char * buffer, int length, int timeout)
{
   int n, len, size, total=0;

   size = length;

   while(size > 0)
   {
      len = size > HPLIP_BUFFER_SIZE ? HPLIP_BUFFER_SIZE : size;
        
      n = hplip_ReadHP(hplip_session, deviceid, channelid, (char *)buffer+total, len, timeout);
      if (n <= 0)
      {
         break;    /* error or timeout */
      }
      size-=n;
      total+=n;
   }
        
   return total;
}

