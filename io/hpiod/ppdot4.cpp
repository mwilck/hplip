/*****************************************************************************\

  ppdot4.cpp - Parallel 1284.4 channel class  
 
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

#include "hpiod.h"

#ifdef HAVE_PPORT

ParDot4Channel::ParDot4Channel(Device *pD) : Dot4Channel(pD)
{
}

int ParDot4Channel::Open(char *sendBuf, int *result)
{
   const char res[] = "msg=OpenChannelResult\nresult-code=%d\n";
   int slen, m;
   ParDevice *pD = (ParDevice *)pDev;

   *result = R_IO_ERROR;
   slen = sprintf(sendBuf, res, R_IO_ERROR);  

   /* Check for multiple opens on the same channel (ie: two clients using PML). */
   if (ClientCnt==1)
   {
      /* Initialize MLC transport if this is the first MLC channel. */
      if (pDev->ChannelCnt==1)
      {
         /* Negotiate ECP mode. */
         m = IEEE1284_MODE_ECPSWE;
         if (ioctl(pDev->GetOpenFD(), PPNEGOT, &m)) 
         {
            syslog(LOG_ERR, "unable to negotiate %s ECP mode: %m %s %d\n", pDev->GetURI(), __FILE__, __LINE__);
            goto bugout;
         }

         /* Enable MLC mode with ECP channel-77. */
         pD->ecp_write_addr(pDev->GetOpenFD(), 78);
         pD->ecp_write(pDev->GetOpenFD(), "\0", 1);
         pD->ecp_write_addr(pDev->GetOpenFD(), 77);

         /* MLC initialize */
         if (Dot4Init(pDev->GetOpenFD()) != 0)
            goto bugout;

         pDev->MlcUp=1;

      } /* if (pDev->ChannelCnt==1) */
 
      if (Dot4GetSocket(pDev->GetOpenFD()) != 0)
         goto bugout;

      if (Dot4OpenChannel(pDev->GetOpenFD()) != 0)
         goto bugout;

   } /* if (ClientCnt==1) */

   *result = R_AOK;
   slen = sprintf(sendBuf, "msg=ChannelOpenResult\nresult-code=%d\nchannel-id=%d\n", *result, Index);

bugout:

   return slen;  
}

int ParDot4Channel::Close(char *sendBuf, int *result)
{
   const char res[] = "msg=ChannelCloseResult\nresult-code=%d\n";
   int len=0, m;
   ParDevice *pD = (ParDevice *)pDev;

   *result = R_AOK;

   if (ClientCnt==1)
   {
      if (pDev->MlcUp)
      {
         if (Dot4CloseChannel(pDev->GetOpenFD()) != 0)
            *result = R_IO_ERROR;
      }
   }

   /* Remove MLC transport if this is the last MLC channel. */
   if (pDev->ChannelCnt==1)
   {
      if (pDev->MlcUp)
      {
         if (Dot4Exit(pDev->GetOpenFD()) != 0)
            *result = R_IO_ERROR;
      }
      pDev->MlcUp=0;
      memset(pDev->CA, 0, sizeof(pDev->CA));

      pD->ecp_write_addr(pDev->GetOpenFD(), 78);     /* disable MLC mode with ECP channel-78 */
      pD->ecp_write(pDev->GetOpenFD(), "\0", 1);

      m = IEEE1284_MODE_NIBBLE;
      ioctl(pDev->GetOpenFD(), PPNEGOT, &m);

      /* Delay for batch scanning. */
      sleep(1);
   }

   len = sprintf(sendBuf, res, *result);  

   return len;
}

#endif  /* HAVE_PPORT */

