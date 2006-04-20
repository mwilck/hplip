/*****************************************************************************\

  hpiod.cpp - HP I/O backend daemon (hpiod)
 
  (c) 2004-2005 Copyright Hewlett-Packard Development Company, LP

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


  Client/Server generic message format (see messaging-protocol.doc):
    # comment lines start with a #
    # each line ends in a newline (\n)
    # spaces before/after = are not significant
    # spaces before/after \n are not significant
    # all keys and values are case insensitive
    msg=<msg-type>  
    result-code=<error code> # only for result messages.
    device-uri=<device-uri> # used for open and hpssd/GUI
    device-id=<device-id> # used after open to identify device
    job-id=<job-id> # CUPS jobid. Optional. For printing only
    char-encoding=utf-8 | latin-1 # default is utf-8 if not present
    encoding=none | base64 # default is none if not present
    length=<n> # length of data section in bytes. max=4K bytes
    digest=<sha1 of data> # if 0 or not present, no digest
    data=<4K max. data> # must be last field

  Notes:
    Rockhopper will call hpiod for printer capabilities only (DeviceID). Rockhopper will
    pass printer ready bits to HP cups backend. The cups backend will write data to the 
    actual device and monitor printer state.
 
    Hpiod will handle simultaneous open/close states (ie: Rockhopper & cups backend). 

\*****************************************************************************/

#include "hpiod.h"

int HpiodPortNumber;               /* IP port number */
char HpiodPidFile[LINE_SIZE];      /* full pid file path */
char HpiodPortFile[LINE_SIZE];     /* full port file path */

static System *pS;

#ifdef HPIOD_DEBUG
int bug(void *data, int size)
{
   int n, fd;
   char buf[128];
   static int cnt=1;

   if (cnt == 1)
      fd = open("/tmp/bug.txt", O_CREAT | O_TRUNC | O_WRONLY, 666);
   else
      fd = open("/tmp/bug.txt", O_CREAT | O_APPEND | O_WRONLY);
   n = sprintf(buf, "bug call %d, size=%d\n", cnt++, size);
   write(fd, buf, n);
   write(fd, data, size);
   close(fd);

   return 0;
}
#endif

/*
 * sysdump() originally came from http://sws.dett.de/mini/hexdump-c , steffen@dett.de .  
 */
void sysdump(void *data, int size)
{
    /* dumps size bytes of *data to syslog. Looks like:
     * [0000] 75 6E 6B 6E 6F 77 6E 20
     *                  30 FF 00 00 00 00 39 00 unknown 0.....9.
     * (in a single line of course)
     */

    unsigned char *p = (unsigned char *)data;
    unsigned char c;
    int n;
    char bytestr[4] = {0};
    char addrstr[10] = {0};
    char hexstr[16*3 + 5] = {0};
    char charstr[16*1 + 5] = {0};
    for(n=1;n<=size;n++) {
        if (n%16 == 1) {
            /* store address for this line */
            snprintf(addrstr, sizeof(addrstr), "%.4x", (p-(unsigned char *)data) && 0xffff);
        }
            
        c = *p;
        if (isprint(c) == 0) {
            c = '.';
        }

        /* store hex str (for left side) */
        snprintf(bytestr, sizeof(bytestr), "%02X ", *p);
        strncat(hexstr, bytestr, sizeof(hexstr)-strlen(hexstr)-1);

        /* store char str (for right side) */
        snprintf(bytestr, sizeof(bytestr), "%c", c);
        strncat(charstr, bytestr, sizeof(charstr)-strlen(charstr)-1);

        if(n%16 == 0) { 
            /* line completed */
            syslog(LOG_INFO, "[%4.4s]   %-50.50s  %s\n", addrstr, hexstr, charstr);
            hexstr[0] = 0;
            charstr[0] = 0;
        }
        p++; /* next byte */
    }

    if (strlen(hexstr) > 0) {
        /* print rest of buffer if not empty */
        syslog(LOG_INFO, "[%4.4s]   %-50.50s  %s\n", addrstr, hexstr, charstr);
    }
}

//ReadConfig
//! Read changeable system parameters.
/*!
******************************************************************************/
int ReadConfig()
{
   char rcbuf[LINE_SIZE]; /* Hold the value read */
   char rundir[LINE_SIZE];
   char section[32];
   FILE *inFile;
   char *tail;
   int n;
        
   /* Set some defaults. */
   HpiodPortNumber = 50000;
   HpiodPidFile[0] = 0;
   HpiodPortFile[0] = 0;

   if((inFile = fopen(RCFILE, "r")) == NULL) 
   {
      syslog(LOG_ERR, "unable to open %s: %m\n", RCFILE);
      return 1;
   } 

   /* Read the config file */
   while ((fgets(rcbuf, sizeof(rcbuf), inFile) != NULL))
   {
      if (rcbuf[0] == '[')
         strncpy(section, rcbuf, sizeof(section)); /* found new section */
      else if ((strncasecmp(section, "[hpiod]", 7) == 0) && (strncasecmp(rcbuf, "port=", 5) == 0))
         HpiodPortNumber = strtol(rcbuf+5, &tail, 10);
      else if ((strncasecmp(section, "[dirs]", 6) == 0) && (strncasecmp(rcbuf, "run=", 4) == 0))
      {
         strncpy(rundir, rcbuf+4, sizeof(rundir));
         n = strlen(rundir);
         rundir[n-1]=0;  /* remove CR */
         snprintf(HpiodPidFile, sizeof(HpiodPidFile), "%s/%s", rundir, PIDFILE); 
         snprintf(HpiodPortFile, sizeof(HpiodPortFile), "%s/%s", rundir, PORTFILE); 
      }
   }
   
   if (HpiodPidFile[0] == 0)
      fprintf(stderr, "unable to read 'run' directory in %s: %s %d\n", RCFILE, __FILE__, __LINE__);
        
   fclose(inFile);
         
   return 0;
}

/*
 * Write hpiod pid to pidfile, and lock it.
 */
static void get_lock(const char* pidfile_name)
{
   static FILE *daemon_lockfp = NULL;   /* Lockfile file pointer */
   static int daemon_lockfd;               /* Lockfile file descriptor */
   int otherpid = 0;
   int r;

   if (!daemon_lockfp) 
   {
      if (((daemon_lockfd = open(pidfile_name, O_RDWR|O_CREAT, 0644)) == -1)
                || ((daemon_lockfp = fdopen(daemon_lockfd, "r+"))) == NULL) 
      {
         fprintf(stderr, "can't open or create %s: %m %s %d\n", pidfile_name, __FILE__, __LINE__);
         exit(EXIT_FAILURE);
      }
      fcntl(daemon_lockfd, F_SETFD, 1);

      do 
      {
         r = flock(daemon_lockfd, LOCK_EX|LOCK_NB);
      } while (r && (errno == EINTR));

      if (r)
      {
         if (errno == EWOULDBLOCK)
         {
            rewind(daemon_lockfp);
            fscanf(daemon_lockfp, "%d", &otherpid);
            fprintf(stderr, "can't lock %s, running daemon's pid may be %d: %s %d\n", pidfile_name, otherpid, __FILE__, __LINE__);
         }
         else
         {
            fprintf(stderr, "can't lock %s: %m %s %d\n", pidfile_name, __FILE__, __LINE__);
         }
         exit(EXIT_FAILURE);
      }
   }

   rewind(daemon_lockfp);
   fprintf(daemon_lockfp, "%ld\n", (long int) getpid());
   fflush(daemon_lockfp);
   ftruncate(fileno(daemon_lockfp), ftell(daemon_lockfp));
}

void session(SessionAttributes *psa)
{
   char recvBuf[BUFFER_SIZE+HEADER_SIZE];
   char sendBuf[BUFFER_SIZE+HEADER_SIZE];
   int len, slen, total;

   pS->RegisterSession(psa);

   psa->descriptor = -1;
   psa->tid = pthread_self();

   while (1)
   {
      /* Handle read data from temporary connection. */
      if ((len = recv(psa->sockid, recvBuf, sizeof(recvBuf), 0)) == -1) 
      {
         if (errno == ECONNRESET)
         {
            len=0;  /* connection reset by client */
         }
         else
         {
            syslog(LOG_ERR, "unable to recv: %m\n");
            len=0;  
         }
      }
   
      if (len==0)
         goto sdone;

      /* Execute message from client. */
      slen = pS->ExecuteMsg(psa, recvBuf, len, sendBuf, sizeof(sendBuf));

      /* Send response back to client. */
      total=0;
      do
      {
         if ((len = send(psa->sockid, sendBuf+total, slen-total, 0)) == -1) 
         {
            syslog(LOG_ERR, "unable to send: %m\n");
            goto sdone;
         }
         total += len;
      }
      while (total < slen);

   }   // while (1)

sdone:
   close(psa->sockid);  /* Remove temporary socket connection. */

   /* Check for device clean-up. */
   if (psa->descriptor != -1)
      pS->DeviceCleanUp(psa); 

   pS->UnRegisterSession(psa);
   free(psa);
}

int main(int argc, char *argv[])
{
   pid_t pid, sid;
   struct sockaddr_in pin;
   int tmpsd;
   char client[LINE_SIZE];
   char server[LINE_SIZE];
   struct hostent *h;
   int len;
   pthread_attr_t attributes;
   pthread_t tid;
   SessionAttributes *psa;

   if (argc > 1)
   {
      const char *arg = argv[1];
      if ((arg[0] == '-') && (arg[1] == 'h'))
      {
         fprintf(stdout, "HP I/O Backend Daemon %s\n", VERSION);
         fprintf(stdout, "(c) 2003-2005 Copyright Hewlett-Packard Development Company, LP\n");
         exit(EXIT_SUCCESS);
      }
   }

   ReadConfig();

   /* Write initial pidfile and lock it. */
   get_lock(HpiodPidFile);

   pid = fork();
   if(pid < 0) 
   {
      syslog(LOG_ERR, "%m\n");
      exit(EXIT_FAILURE);
   }
   if(pid > 0) 
      exit(EXIT_SUCCESS);

   /* Update pidfile with new pid. */
   get_lock(NULL);

   /* First, start a new session */
   if((sid = setsid()) < 0)
   {
      syslog(LOG_ERR, "%s\n", "setsid");
      exit(EXIT_FAILURE);
   }

   /* Next, make / the current directory */
   if((chdir("/")) < 0) 
   {
      syslog(LOG_ERR, "%s\n", "chdir");
      exit(EXIT_FAILURE);
   }

   /* Reset the file mode */
   umask(0);

   /* Close unneeded file descriptors */
   close(STDIN_FILENO);
   close(STDOUT_FILENO);
   close(STDERR_FILENO);

   pS = new System();

   signal(SIGPIPE, SIG_IGN);  /* ignor SIGPIPE */

   pthread_attr_init(&attributes);
   pthread_attr_setdetachstate(&attributes, PTHREAD_CREATE_DETACHED);

   while(1) 
   {
      /* Get new connection on permanent socket. */
      len = sizeof(pin);
      tmpsd = accept(pS->Permsd, (struct sockaddr *)&pin, (socklen_t *)&len);
      if (tmpsd == -1)
      {
         syslog(LOG_ERR, "unable to accept: %m\n");
         continue;
      }

      /* Allow connection from local client only. */
      strcpy(client, inet_ntoa(pin.sin_addr));          /* client IP */
      if (strcmp(client, "127.0.0.1") != 0)
      {
         gethostname(server, sizeof(server));
         h = gethostbyname(server);
         strcpy(server, inet_ntoa(*((struct in_addr *)h->h_addr)));   /* server IP */
         if (strcmp(client, server) != 0)
         {
            syslog(LOG_INFO, "Rejected connection from %s\n", client);
            close(tmpsd);
            continue;
         }
      }  

      /* Create session attributes. */
      if ((psa = (SessionAttributes *)malloc(sizeof(SessionAttributes))) == NULL)
      {
         syslog(LOG_ERR, "unable to creat session attributes: %m\n");
         continue;
      }
      memset(psa, 0, sizeof(SessionAttributes));
      psa->sockid = tmpsd;  /* save temporary socket connection */

      /* Dispatch new thread with session attributes. */
      if (pthread_create(&tid, &attributes, (void *(*)(void*))session, (void *)psa) != 0)
         syslog(LOG_ERR, "unable to creat thread: %m\n");

   }   // while (1)

   exit(EXIT_SUCCESS);
}

