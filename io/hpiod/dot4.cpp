/*****************************************************************************\

  dot4.cpp - 1284.4 channel class  
 
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

/*
 * This 1284.4 implementation does not support "Multiple Outstanding Transactions" which is optional.
 */

Dot4Channel::Dot4Channel(Device *pD) : Channel(pD)
{
   pcredit = scredit = 0;
   rcnt = rindex = 0;
}

/* Map socket id to channel index. */
int Dot4Channel::Dot4Socket2Channel(unsigned char sockid)
{
   int i, n;

   for (i=0, n=0; i<MAX_CHANNEL && n<pDev->ChannelCnt; i++)
   {
      if (pDev->pChannel[i] != NULL)
      {
         n++;
         if (sockid == pDev->pChannel[i]->GetSocketID())
            return i;
      }
   }
   syslog(LOG_ERR, "no channel for sockid=%d: %s %d\n", sockid, __FILE__, __LINE__);
   return -1;   
}

/* Write command reply back to peripheral. */
int Dot4Channel::Dot4ForwardReply(int fd, unsigned char *buf, int size)
{
   int len=0;

   if ((len = pDev->Write(fd, buf, size)) != size)
   {
      syslog(LOG_ERR, "unable to Dot4ForwarReply: %m %s %d\n", __FILE__, __LINE__);
   }   
   return len;
}

/* Execute command from peripheral. */
int Dot4Channel::Dot4ExecReverseCmd(int fd, unsigned char *buf)
{
   DOT4Cmd *pCmd;
   DOT4Reply *pReply;
   DOT4Credit *pCredit;
   DOT4CreditReply *pCreditReply;
   DOT4CreditRequest *pCreditReq;
   DOT4CreditRequestReply *pCreditReqReply;
   DOT4Error *pError;
   Dot4Channel *pC=NULL;
   int i, len, size;
   unsigned char socket;

   pCmd = (DOT4Cmd *)buf;

   /* See if this packet is a command packet. */
   if (!(pCmd->h.psid == 0 && pCmd->h.ssid == 0))
   {
      if ((pCmd->h.psid == pCmd->h.ssid) && ((i = Dot4Socket2Channel(pCmd->h.psid)) >= 0))
      {
         /* Got a valid data packet handle it. This can happen when ReadData timeouts and p2hcredit=1. */
         pC = (Dot4Channel *)pDev->pChannel[i];
         size = ntohs(pCmd->h.length) - sizeof(DOT4Header);
         if (size > (MAX_RECEIVER_DATA - pC->rcnt))
         {
            syslog(LOG_ERR, "invalid data packet size=%d: %s %d\n", size, __FILE__, __LINE__);
            return 0;
         }
         memcpy(&pC->rbuf[pC->rcnt], buf+sizeof(DOT4Header), size);
         pC->rcnt += size;
         if (pCmd->h.credit)
            pC->SetH2PCredit(pC->GetH2PCredit() + pCmd->h.credit);  /* note, piggy back credit is 1 byte wide */ 
         pC->SetP2HCredit(pC->GetP2HCredit()-1); /* one data packet was read, decrement credit count */
      }
      else
      {
         len = ntohs(pCmd->h.length);
         syslog(LOG_ERR, "unsolicited data packet: psid=%x, ssid=%x, length=%d, credit=%d, status=%x: %s %d\n", pCmd->h.psid,
                                     pCmd->h.ssid, len, pCmd->h.credit, pCmd->h.control, __FILE__, __LINE__);
         sysdump(buf, len);
      }
      return 0;  
   }

   /* Process any command. */
   switch (pCmd->cmd)
   {
      case DOT4_CREDIT:
         pCredit = (DOT4Credit *)buf;
         if ((i = Dot4Socket2Channel(pCredit->psocket)) < 0)
            return 1;
         pC = (Dot4Channel *)pDev->pChannel[i];
         pC->SetH2PCredit(pC->GetH2PCredit()+ntohs(pCredit->credit));
         pCreditReply = (DOT4CreditReply *)buf;
         pCreditReply->h.length = htons(sizeof(DOT4CreditReply));
         pCreditReply->h.credit = 1;       /* transaction credit for next command */
         pCreditReply->h.control = 0;
         pCreditReply->cmd |= 0x80;
         pCreditReply->result = 0;
         pCreditReply->psocket = pC->GetSocketID();
         pCreditReply->ssocket = pC->GetSocketID();
         Dot4ForwardReply(fd, (unsigned char *)pCreditReply, sizeof(DOT4CreditReply)); 
         break;
      case DOT4_CREDIT_REQUEST:
         static int cnt=0;
         pCreditReq = (DOT4CreditRequest *)buf;
         if (cnt++ < 5)         
            syslog(LOG_ERR, "unexpected DOT4CreditRequest: cmd=%x, hid=%x, pid=%x, maxcredit=%d: %s %d\n", pCreditReq->cmd,
                                         pCreditReq->psocket, pCreditReq->ssocket, ntohs(pCreditReq->maxcredit), __FILE__, __LINE__);
         socket = pCreditReq->ssocket;
         pCreditReqReply = (DOT4CreditRequestReply *)buf;
         pCreditReqReply->h.length = htons(sizeof(DOT4CreditRequestReply));
         pCreditReqReply->h.credit = 1;       /* transaction credit for next command */
         pCreditReqReply->h.control = 0;
         pCreditReqReply->cmd |= 0x80;
         pCreditReqReply->result = 0;
         pCreditReqReply->psocket = socket;
         pCreditReqReply->ssocket = socket;
         pCreditReqReply->credit = 0;
         Dot4ForwardReply(fd, (unsigned char *)pCreditReqReply, sizeof(DOT4CreditRequestReply)); 
         break;
      case DOT4_ERROR:
         pError = (DOT4Error *)buf;
         syslog(LOG_ERR, "unexpected DOT4Error: cmd=%x, psocket=%d, ssocket=%d, error=%x\n: %s %d", pError->cmd, pError->psocket, pError->ssocket, pError->error, __FILE__, __LINE__);
         return 1;
      default:
         pReply = (DOT4Reply *)buf;
         syslog(LOG_ERR, "unexpected command: cmd=%x, result=%x: %s %d\n", pReply->cmd, pReply->result, __FILE__, __LINE__);
         pReply->h.length = htons(sizeof(DOT4Reply));
         pReply->h.credit = 1;       /* transaction credit for next command */
         pReply->h.control = 0;
         pReply->cmd |= 0x80;
         pReply->result = 1;
         Dot4ForwardReply(fd, (unsigned char *)pReply, sizeof(DOT4Reply)); 
         break;
   }
   return 0;
}

/* Get command from peripheral and processes the reverse command. */
int Dot4Channel::Dot4ReverseCmd(int fd)
{
   unsigned char buf[MAX_COMMAND_PACKET];   
   int stat=0, len, size;
   unsigned int pklen;
   unsigned char *pBuf;
   DOT4Reply *pPk;

   pPk = (DOT4Reply *)buf;

   pBuf = buf;

   /* Read packet header. */
   size = sizeof(DOT4Header);
   while (size > 0)
   {
      if ((len = pDev->Read(fd, pBuf, size)) < 0)
      {
         syslog(LOG_ERR, "unable to read Dot4ReverseCmd header: %m %s %d\n", __FILE__, __LINE__);
         stat = 1;
         goto bugout;
      }
      size-=len;
      pBuf+=len;
   }

   /* Determine packet size. */
   if ((pklen = ntohs(pPk->h.length)) > sizeof(buf))
   {
      syslog(LOG_ERR, "invalid Dot4ReverseCmd packet size: size=%d %s %d\n", pklen, __FILE__, __LINE__);
      stat = 1;
      goto bugout;
   }

   /* Read packet data field. */
   size = pklen - sizeof(DOT4Header);
   while (size > 0)
   {
      if ((len = pDev->Read(fd, pBuf, size)) < 0)
      {
         syslog(LOG_ERR, "unable to read Dot4ReverseCmd data: %m exp=%d act=%d %s %d\n", pklen-sizeof(DOT4Header), pklen-sizeof(DOT4Header)-size, __FILE__, __LINE__);
         stat = 1;
         goto bugout;
      }
      size-=len;
      pBuf+=len;
   }

   stat = Dot4ExecReverseCmd(fd, buf);

bugout:
   return stat;
}

/*
 * Get command reply from peripheral. Waits for reply then returns. Processes any reverse commands
 * while waiting for a reply.
 */
int Dot4Channel::Dot4ReverseReply(int fd, unsigned char *buf, int bufsize)
{
   int stat=0, len, size, pklen;
   unsigned char *pBuf;
   DOT4Reply *pPk;

   pPk = (DOT4Reply *)buf;
   
   while (1)
   {
      pBuf = buf;

      /* Read packet header. */
      size = sizeof(DOT4Header);
      while (size > 0)
      {
         if ((len = pDev->Read(fd, pBuf, size, 2000000)) < 0)   /* wait 2 second */
         {
            syslog(LOG_ERR, "unable to read Dot4ReverseReply header: %m bytesRead=%d %s %d\n", sizeof(DOT4Header)-size, __FILE__, __LINE__);
            stat = 2;  /* short timeout */
            goto bugout;
         }
         size-=len;
         pBuf+=len;
      }

      /* Determine packet size. */
      pklen = ntohs(pPk->h.length);
      if (pklen <= 0 || pklen > bufsize)
      {
         syslog(LOG_ERR, "invalid Dot4ReverseReply packet size: size=%d, buf=%d %s %d\n", pklen, bufsize, __FILE__, __LINE__);
         stat = 1;
         goto bugout;
      }

      /* Read packet data field. */
      size = pklen - sizeof(DOT4Header);
      while (size > 0)
      {
         if ((len = pDev->Read(fd, pBuf, size)) < 0)
         {
            syslog(LOG_ERR, "unable to read Dot4ReverseReply data: %m exp=%d act=%d %s %d\n", pklen-sizeof(DOT4Header), pklen-sizeof(DOT4Header)-size, __FILE__, __LINE__);
            stat = 1;
            goto bugout;
         }
         size-=len;
         pBuf+=len;
      }

      /* Check for reply. */
      if (pPk->cmd & 0x80)
         break;

      stat = Dot4ExecReverseCmd(fd, buf);

      if (stat != 0)
         break;

   } /* while (1) */

bugout:
   return stat;
}

int Dot4Channel::Dot4Init(int fd)
{
   unsigned char buf[MAX_COMMAND_PACKET];
   int stat=0, len, n, cnt;
   DOT4Init *pCmd;
   DOT4InitReply *pReply;

   memset(buf, 0, sizeof(DOT4Init));
   pCmd = (DOT4Init *)buf;
   n = sizeof(DOT4Init);
   pCmd->h.length = htons(n);
   pCmd->h.credit = 1;       /* transaction credit for reply */
   pCmd->cmd = DOT4_INIT;
   pCmd->rev = 0x20;
   
   if ((len = pDev->Write(fd, pCmd, n)) != n)
   {
      syslog(LOG_ERR, "unable to write DOT4Init: %m %s %d\n", __FILE__, __LINE__);
      stat = 1;
      goto bugout;
   }

   cnt=0;
   while(1)
   {
      stat = Dot4ReverseReply(fd, buf, sizeof(buf));
      pReply = (DOT4InitReply *)buf;

      if ((stat != 0) || (pReply->cmd != (0x80 | DOT4_INIT)) || (pReply->result != 0))
      {
         if (errno == EIO && cnt<1)
         {
            /* hack for usblp.c 2.6.5 */
            syslog(LOG_INFO, "invalid DOT4InitReply retrying... %s %d\n", __FILE__, __LINE__);
            sleep(1);   
            cnt++;
            continue;
         }
         syslog(LOG_ERR, "invalid DOT4InitReply: cmd=%x, result=%x\n, revision=%x %s %d\n", pReply->cmd, pReply->result, pReply->rev, __FILE__, __LINE__);
         stat = 1;
         goto bugout;
      }
      break;
   }

bugout:
   return stat;
}

int Dot4Channel::Dot4Exit(int fd)
{
   unsigned char buf[MAX_COMMAND_PACKET];
   int stat=0, len, n;
   DOT4Exit *pCmd;
   DOT4ExitReply *pReply;

   memset(buf, 0, sizeof(DOT4Exit));
   pCmd = (DOT4Exit *)buf;
   n = sizeof(DOT4Exit);
   pCmd->h.length = htons(n);
   pCmd->h.credit = 1;
   pCmd->cmd = DOT4_EXIT;
   
   if ((len = pDev->Write(fd, pCmd, n)) != n)
   {
      syslog(LOG_ERR, "unable to write DOT4Exit: %m %s %d\n", __FILE__, __LINE__);
      stat = 1;
      goto bugout;
   }

   stat = Dot4ReverseReply(fd, buf, sizeof(buf));
   pReply = (DOT4ExitReply *)buf;

   if ((stat != 0) || (pReply->cmd != (0x80 | DOT4_EXIT)) || (pReply->result != 0))
   {
      syslog(LOG_ERR, "invalid DOT4ExitReply: cmd=%x, result=%x %s %d\n", pReply->cmd, pReply->result, __FILE__, __LINE__);
      stat = 1;
      goto bugout;
   }

bugout:
   return stat;
}

int Dot4Channel::Dot4GetSocket(int fd)
{
   unsigned char buf[MAX_COMMAND_PACKET];
   int stat=0, len, n;
   DOT4GetSocket *pCmd;
   DOT4GetSocketReply *pReply;

   memset(buf, 0, sizeof(DOT4GetSocket));
   pCmd = (DOT4GetSocket *)buf;
   n = sizeof(DOT4GetSocket);
   len = strlen(GetService());
   memcpy(buf+sizeof(DOT4GetSocket), GetService(), len);
   n += len;
   pCmd->h.length = htons(n);
   pCmd->h.credit = 1;
   pCmd->cmd = DOT4_GET_SOCKET;
   
   if ((len = pDev->Write(fd, pCmd, n)) != n)
   {
      syslog(LOG_ERR, "unable to write DOT4GetSocket: %m %s %d\n", __FILE__, __LINE__);
      stat = 1;
      goto bugout;
   }

   stat = Dot4ReverseReply(fd, buf, sizeof(buf));
   pReply = (DOT4GetSocketReply *)buf;

   if ((stat != 0) || (pReply->cmd != (0x80 | DOT4_GET_SOCKET)) || (pReply->result != 0))
   {
      syslog(LOG_ERR, "invalid DOT4GetSocketReply: cmd=%x, result=%x %s %d\n", pReply->cmd, pReply->result, __FILE__, __LINE__);
      stat = 1;
      goto bugout;
   }

   SetSocketID(pReply->socket);

bugout:
   return stat;
}

/* Write data to peripheral. */
int Dot4Channel::Dot4ForwardData(int fd, int sockid, unsigned char *buf, int size)
{
   int stat=0, len, n;
   DOT4Header h;

   memset(&h, 0, sizeof(h));
   n = sizeof(DOT4Header) + size;
   h.length = htons(n);
   h.psid = sockid;
   h.ssid = sockid;
      
   if ((len = pDev->Write(fd, &h, sizeof(DOT4Header))) != sizeof(DOT4Header))
   {
      syslog(LOG_ERR, "unable to write Dot4ForwardData header: %m %s %d\n", __FILE__, __LINE__);
      stat = 1;
      goto bugout;
   }

   if ((len = pDev->Write(fd, buf, size)) != size)
   {
      syslog(LOG_ERR, "unable to write Dot4ForwardData: %m %s %d\n", __FILE__, __LINE__);
      stat = 1;
      goto bugout;
   }

bugout:
   return stat;
}

/* Read data from peripheral. */
int Dot4Channel::Dot4ReverseData(int fd, int sockid, unsigned char *buf, int length, int timeout)
{
   int len, size, total;
   DOT4Header *pPk;

   pPk = (DOT4Header *)buf;

   while (1)
   {
      total = 0;

      /* Read packet header. */
      size = sizeof(DOT4Header);
      while (size > 0)
      {
         /* Use requested client timeout until we start reading. */
         if (total == 0)
            len = pDev->Read(fd, buf+total, size, timeout);
         else
            len = pDev->Read(fd, buf+total, size);

         if (len < 0)
         {
            /* Got a timeout, if timeout occured after read started thats an error. */
            if (total > 0)
               syslog(LOG_ERR, "unable to read Dot4ReverseData header: %m %s %d\n", __FILE__, __LINE__);
            goto bugout;
         }
         size-=len;
         total+=len;
      }

      /* Determine data size. */
      size = ntohs(pPk->length) - sizeof(DOT4Header);

      if (size > length)
      {
         syslog(LOG_ERR, "invalid Dot4ReverseData size: size=%d, buf=%d %s %d\n", size, length, __FILE__, __LINE__);
         goto bugout;
      } 

      /* Make sure data packet is for this channel. */
      if (pPk->psid != sockid && pPk->ssid != sockid)
      {
         if (pPk->psid == 0 && pPk->ssid == 0)
         {
            /* Ok, got a command channel packet instead of a data packet, handle it... */
            while (size > 0)
            {
               if ((len = pDev->Read(fd, buf+total, size)) < 0)
               {
                  syslog(LOG_ERR, "unable to read Dot4ReverseData command: %m %s %d\n", __FILE__, __LINE__);
                  goto bugout;
               }
               size-=len;
               total=len;
            }
            Dot4ExecReverseCmd(fd, buf);
            continue;   /* try again for data packet */
         }
         else
         {
            DOT4Cmd *pCmd = (DOT4Cmd *)buf;
            syslog(LOG_ERR, "invalid Dot4ReverseData state: unexpected packet psid=%x, ssid=%x, cmd=%x %s %d\n", pPk->psid, pPk->ssid, pCmd->cmd, __FILE__, __LINE__);
            goto bugout;
         }
      }

      if (pPk->credit)
      {
         SetH2PCredit(GetH2PCredit() + pPk->credit);  /* note, piggy back credit is 1 byte wide */ 
      }

      total = 0;  /* eat packet header */
   
      /* Read packet data field without exception_timeout. */
      while (size > 0)
      {
         if ((len = pDev->Read(fd, buf+total, size)) < 0)
         {
            syslog(LOG_ERR, "unable to read Dot4ReverseData: %m %s %d\n", __FILE__, __LINE__);
            goto bugout;
         }
         size-=len;
         total+=len;
      }
      break; /* done reading data packet */
   }  /* while (1) */

bugout:
   return total;
}

int Dot4Channel::Dot4OpenChannel(int fd)
{
   unsigned char buf[MAX_COMMAND_PACKET];
   int stat=0, len, n;
   DOT4OpenChannel *pCmd;
   DOT4OpenChannelReply *pReply;

   memset(buf, 0, sizeof(DOT4OpenChannel));
   pCmd = (DOT4OpenChannel *)buf;
   n = sizeof(DOT4OpenChannel);
   pCmd->h.length = htons(n);
   pCmd->h.credit = 1;
   pCmd->cmd = DOT4_OPEN_CHANNEL;
   pCmd->psocket = GetSocketID();
   pCmd->ssocket = GetSocketID();
   pCmd->maxp2s = htons(MAX_SENDER_DATA);  /* max primary to secondary packet size in bytes */
   pCmd->maxs2p = htons(MAX_RECEIVER_DATA);  /* max secondary to primary packet size in bytes */
   pCmd->maxcredit = htons(0xffff);          /* "unlimited credit" mode, give primary (sender) as much credit as possible */
   
   if ((len = pDev->Write(fd, pCmd, n)) != n)
   {
      syslog(LOG_ERR, "unable to write Dot4OpenChannel: %m %s %d\n", __FILE__, __LINE__);
      stat = 1;
      goto bugout;
   }

   stat = Dot4ReverseReply(fd, buf, sizeof(buf));
   pReply = (DOT4OpenChannelReply *)buf;

   if ((stat != 0) || (pReply->cmd != (0x80 | DOT4_OPEN_CHANNEL)) || (pReply->result != 0))
   {
      syslog(LOG_ERR, "invalid Dot4OpenChannelReply: cmd=%x, result=%x %s %d\n", pReply->cmd, pReply->result, __FILE__, __LINE__);
      stat = 1;
      goto bugout;
   }

   SetH2PSize(ntohs(pReply->maxp2s));
   SetP2HSize(ntohs(pReply->maxs2p));
   SetH2PCredit(ntohs(pReply->credit));

bugout:
   return stat;
}

int Dot4Channel::Dot4CloseChannel(int fd)
{
   unsigned char buf[MAX_COMMAND_PACKET];
   int stat=0, len, n;
   DOT4CloseChannel *pCmd;
   DOT4CloseChannelReply *pReply;

   memset(buf, 0, sizeof(DOT4CloseChannel));
   pCmd = (DOT4CloseChannel *)buf;
   n = sizeof(DOT4CloseChannel);
   pCmd->h.length = htons(n);
   pCmd->h.credit = 1;
   pCmd->cmd = DOT4_CLOSE_CHANNEL;
   pCmd->psocket = GetSocketID();
   pCmd->ssocket = GetSocketID();

   if ((len = pDev->Write(fd, pCmd, n)) != n)
   {
      syslog(LOG_ERR, "unable to write Dot4CloseChannel: %m %s %d\n", __FILE__, __LINE__);
      stat = 1;
      goto bugout;
   }

   stat = Dot4ReverseReply(fd, buf, sizeof(buf));
   pReply = (DOT4CloseChannelReply *)buf;

   if ((stat != 0) || (pReply->cmd != (0x80 | DOT4_CLOSE_CHANNEL)) || (pReply->result != 0))
   {
      syslog(LOG_ERR, "invalid Dot4CloseChannelReply: cmd=%x, result=%x\n %s %d", pReply->cmd, pReply->result, __FILE__, __LINE__);
      stat = 1;
      goto bugout;
   }

bugout:
   return stat;
}

int Dot4Channel::Dot4Credit(int fd, unsigned short credit)
{
   unsigned char buf[MAX_COMMAND_PACKET];
   int stat=0, len, n;
   DOT4Credit *pCmd;
   DOT4CreditReply *pReply;

   memset(buf, 0, sizeof(DOT4Credit));
   pCmd = (DOT4Credit *)buf;
   n = sizeof(DOT4Credit);
   pCmd->h.length = htons(n);
   pCmd->h.credit = 1;
   pCmd->cmd = DOT4_CREDIT;
   pCmd->psocket = GetSocketID();
   pCmd->ssocket = GetSocketID();
   pCmd->credit = htons(credit);                /* set peripheral to host credit */
   
   if ((len = pDev->Write(fd, pCmd, n)) != n)
   {
      syslog(LOG_ERR, "unable to write Dot4Credit: %m %s %d\n", __FILE__, __LINE__);
      stat = 1;
      goto bugout;
   }

   stat = Dot4ReverseReply(fd, buf, sizeof(buf));
   pReply = (DOT4CreditReply *)buf;

   if ((stat != 0) || (pReply->cmd != (0x80 | DOT4_CREDIT)) || (pReply->result != 0))
   {
      syslog(LOG_ERR, "invalid Dot4CreditReply: cmd=%x, result=%x %s %d\n", pReply->cmd, pReply->result, __FILE__, __LINE__);
      stat = 1;
      goto bugout;
   }

   SetP2HCredit(GetP2HCredit()+credit);

bugout:
   return stat;
}

int Dot4Channel::Dot4CreditRequest(int fd, unsigned short credit)
{
   unsigned char buf[MAX_COMMAND_PACKET];
   int stat=0, len, n;
   DOT4CreditRequest *pCmd;
   DOT4CreditRequestReply *pReply;

   memset(buf, 0, sizeof(DOT4CreditRequest));
   pCmd = (DOT4CreditRequest *)buf;
   n = sizeof(DOT4CreditRequest);
   pCmd->h.length = htons(n);
   pCmd->h.credit = 1;
   pCmd->cmd = DOT4_CREDIT_REQUEST;
   pCmd->psocket = GetSocketID(); 
   pCmd->ssocket = GetSocketID();
   //   pCmd->maxcredit = htons(credit);                /* request host to peripheral credit */
   pCmd->maxcredit = htons(0xffff);                /* request host to peripheral credit */
   
   if ((len = pDev->Write(fd, pCmd, n)) != n)
   {
      syslog(LOG_ERR, "unable to write Dot4CreditRequest: %m %s %d\n", __FILE__, __LINE__);
      stat = 1;
      goto bugout;
   }

   stat = Dot4ReverseReply(fd, buf, sizeof(buf));
   pReply = (DOT4CreditRequestReply *)buf;

   if ((stat != 0) || (pReply->cmd != (0x80 | DOT4_CREDIT_REQUEST)) || (pReply->result != 0))
   {
      syslog(LOG_ERR, "invalid Dot4CreditRequestReply: cmd=%x, result=%x %s %d\n", pReply->cmd, pReply->result, __FILE__, __LINE__);
      stat = 1;
      goto bugout;
   }

   SetH2PCredit(GetH2PCredit()+ntohs(pReply->credit));

bugout:
   return stat;
}

int Dot4Channel::Open(char *sendBuf, int *result)
{
   const char res[] = "msg=OpenChannelResult\nresult-code=%d\n";
   int slen, fd;
   int config, interface, altset;

   *result = R_IO_ERROR;
   slen = sprintf(sendBuf, res, R_IO_ERROR);  

   /* Check for multiple opens on the same channel (ie: two clients using PML). */
   if (ClientCnt==1)
   {
      /* Initialize DOT4 transport if this is the first DOT4 channel. */
      if (pDev->ChannelCnt==1)
      {
         /* If 7/1/3 (MLC/1284.4) protocol is available use it. */
         if (pDev->GetInterface(7, 1, 3, &config, &interface, &altset) == 0)
            fd = FD_7_1_3;    /* mlc, dot4 */
         else
            fd = FD_7_1_2;    /* raw, mlc, dot4 */

         /* If new usb interface, release old and claim new. */
         if (pDev->OpenFD != fd)
         {
            pDev->ReleaseInterface(pDev->OpenFD);
            if (pDev->ClaimInterface(fd, config, interface, altset))
               goto bugout;
            pDev->OpenFD = fd;
         }

         if (fd == FD_7_1_2)
         { 
            if (pDev->GetChannelMode() == DOT4_BRIDGE_MODE)
            {
               /* Emulate 7/1/3 on 7/1/2 using the bridge chip set (ie: CLJ2500). */
               if (pDev->BridgeChipUp(fd))
                  goto bugout;
            }
            else
            {
               /* Emulate 7/1/3 on 7/1/2 using vendor-specific ECP channel-77. */
               if (pDev->WriteECPChannel(fd, 77)) 
                  goto bugout;
            }
         }

         if (fd == FD_7_1_3 && pDev->GetChannelMode() == DOT4_PHOENIX_MODE && strcasecmp(GetService(), "hp-message") == 0)
            pDev->WritePhoenixSetup(fd);

         int len;
         unsigned int i;
         unsigned char buf[255];

         /* Drain any reverse data. */
         for (i=0,len=1; len > 0 && i < sizeof(buf); i++)
            len = pDev->Read(fd, buf+i, 1, 0);    /* no blocking */

         /* DOT4 initialize */
         if (Dot4Init(fd) != 0)
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

int Dot4Channel::Close(char *sendBuf, int *result)
{
   const char res[] = "msg=ChannelCloseResult\nresult-code=%d\n";
   int len=0;
   int config, interface, altset;

   *result = R_AOK;

   if (ClientCnt==1)
   {
      if (pDev->MlcUp)
      {
         if (Dot4CloseChannel(pDev->GetOpenFD()) != 0)
            *result = R_IO_ERROR;
      }
   }

   /* Remove 1284.4 transport if this is the last 1284.4 channel. */
   if (pDev->ChannelCnt==1)
   {
      if (pDev->MlcUp)
      {
         if (Dot4Exit(pDev->GetOpenFD()) != 0)
            *result = R_IO_ERROR;
      }
      pDev->MlcUp=0;
      memset(pDev->CA, 0, sizeof(pDev->CA));

      if (pDev->OpenFD == FD_7_1_2)
      {
         if (pDev->GetChannelMode() == DOT4_BRIDGE_MODE)
         {
            pDev->BridgeChipDown(pDev->GetOpenFD());
         }
         else
         {
            pDev->WriteECPChannel(pDev->GetOpenFD(), 78);
            pDev->WriteECPChannel(pDev->GetOpenFD(), 0);
         }
      }

      /* If 7/1/2 protocol is available, use it. */
      if (pDev->OpenFD == FD_7_1_3 && pDev->GetInterface(7, 1, 2, &config, &interface, &altset) == 0)
      {
         pDev->ReleaseInterface(FD_7_1_3);
         pDev->ClaimInterface(FD_7_1_2, config, interface, altset);
         pDev->OpenFD = FD_7_1_2;
      }

      /* Delay for back-to-back scanning using scanimage (ie: OJ 7110, OJ d135). */
      sleep(1);
   }

   len = sprintf(sendBuf, res, *result);  

   return len;
}

int Dot4Channel::WriteData(unsigned char *data, int length, char *sendBuf, int *result)
{
   const char res[] = "msg=ChannelDataOutResult\nresult-code=%d\nbytes-written=%d\n"; 
   int ret, len, size, sLen, dlen, total=0;
   int cnt=0;

   *result=R_IO_ERROR;

   size = length;
   dlen = GetH2PSize() - sizeof(DOT4Header);
   while (size > 0)
   {
      len = (size > dlen) ? dlen : size;

      /* Check for Phoenix chipset hack (ie: clj2840, lj3055). */
      if (GetH2PCredit() == 0 && pDev->GetChannelMode() == DOT4_PHOENIX_MODE && strcasecmp(GetService(), "hp-message") == 0)
      {
         /* For PML channel only, issue credit to peripheral followed by credit request to peripheral. */ 
         if (GetP2HCredit() == 0)
         {
            if (Dot4Credit(pDev->GetOpenFD(), 1) != 0)
            {
               syslog(LOG_ERR, "invalid Dot4Credit to peripheral: %s %d\n", __FILE__, __LINE__);
               goto bugout;
            }     
	 }
         if (Dot4CreditRequest(pDev->GetOpenFD(), 1) != 0) 
         {
            syslog(LOG_ERR, "invalid Dot4CreditRequest from peripheral: %s %d\n", __FILE__, __LINE__);
            goto bugout;
         }
      }

      if (GetH2PCredit() == 0)
      {
         ret = Dot4ReverseCmd(pDev->GetOpenFD());
         if (GetH2PCredit() == 0)
         {
            if (ret == 0)
               continue;  /* Got a reverse command, but no Dot4Credit, try again. */ 

	    //            syslog(LOG_ERR, "no credit from peripheral, trying credit request: %s %d\n", __FILE__, __LINE__);
	    //            if (Dot4CreditRequest(pDev->GetOpenFD(), 1) != 0)
	    //            {
               syslog(LOG_ERR, "invalid Dot4Credit from peripheral: %s %d\n", __FILE__, __LINE__);
               goto bugout;
	       //            }
	       //            if (cnt++ == 0)
	       //               continue; /* credit requested, try again. */
	       //            else
	       //               goto bugout;
         }
      }

      if (Dot4ForwardData(pDev->GetOpenFD(), GetSocketID(), data+total, len) != 0)
      {
         goto bugout;
      }

      SetH2PCredit(GetH2PCredit()-1);
      size-=len;
      total+=len;
      cnt=0;
   }

   *result = R_AOK;

bugout:
   sLen = sprintf(sendBuf, res, *result, total);  
   return sLen;
}

/*
 * ReadData() tries to read "length" bytes from the peripheral. ReadData() reads data in packet size chunks. 
 * The returned read count may be zero (timeout, no data available), less than "length" or equal "length".
 *
 * ReadData() may read more the "length" if the data packet is greater than "length". For this case the
 * return value will equal "length" and the left over data will be buffered for the next ReadData() call.
 *
 * The "timeout" specifies how many seconds to wait for a data packet. Once the read of the data packet has
 * started the "timeout" is no longer used.
 *
 * Note, if a "timeout" occurs one peripheral to host credit is left outstanding. Which means the peripheral
 * can send unsolicited data later.
 */
int Dot4Channel::ReadData(int length, int timeout, char *sendBuf, int sendBufLength, int *result)
{
   const char res[] = "msg=ChannelDataInResult\nresult-code=%d\n";
   int sendLen;

   *result=R_IO_ERROR;

   if ((length + HEADER_SIZE) > sendBufLength)
   {
      syslog(LOG_ERR, "invalid data size Dot4Channel::ReadData: %d %s %d\n", length, __FILE__, __LINE__);
      sendLen = sprintf(sendBuf, res, *result);  
      goto bugout;
   }

   if (GetP2HSize()==0)
   {
      syslog(LOG_ERR, "invalid peripheral to host packet size Dot4Channel::ReadData: %d %s %d\n", GetP2HSize(), __FILE__, __LINE__);
      sendLen = sprintf(sendBuf, res, *result);  
      goto bugout;
   }

   if (rcnt)
   {
      *result=R_AOK;
      sendLen = CutBuf(sendBuf, length);
      goto bugout;
   }

   if (GetP2HCredit() == 0)
   {
      /* Issue enough credit to the peripheral to read one data packet. */ 
      if (Dot4Credit(pDev->GetOpenFD(), 1) != 0)
      {
         sendLen = sprintf(sendBuf, res, *result);  
         goto bugout;
      }     
   }

   *result=R_AOK;
   rcnt = Dot4ReverseData(pDev->GetOpenFD(), GetSocketID(), rbuf, sizeof(rbuf), timeout);
   if (rcnt)
      SetP2HCredit(GetP2HCredit()-1); /* one data packet was read, decrement credit count */
 
   sendLen = CutBuf(sendBuf, length);

bugout:
   return sendLen;
}

