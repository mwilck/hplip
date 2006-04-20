/************************************************************************************\

  io.c - HP SANE backend for multi-function peripherals (libsane-hpaio)

  (c) 2001-2004 Copyright Hewlett-Packard Development Company, LP

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

  Current Author: Don Welch
  Contributing Author: David Suffield 

\************************************************************************************/

#include "hpaio.h"

#if defined( HPAIO_DEBUG )
void DBG(int level, const char *format, ...)
{
    va_list args;
    va_start(args, format);
    vfprintf(stderr, format, args);
    va_end(args);
}
#else
void DBG(int level, const char *format, ...)
{
}
#endif
    
int bug(const char *fmt, ...)
{
   char buf[256];
   va_list args;
   int n;

   va_start(args, fmt);
   if ((n = vsnprintf(buf, 256, fmt, args)) == -1)
      buf[255] = 0;     /* output was truncated */
   syslog(LOG_WARNING, buf);
   va_end(args);
   return n;
}

unsigned long DivideAndShift( int line,
                              unsigned long numerator1,
                              unsigned long numerator2,
                              unsigned long denominator,
                              int shift )
{
    unsigned long remainder, shiftLoss = 0;
    unsigned long long result = numerator1;
    result *= numerator2;
    if( shift > 0 )
    {
        result <<= shift;
    }
    remainder = result % denominator;
    result /= denominator;
    if( shift < 0 )
    {
        shiftLoss = result & ( ( 1 << ( -shift ) ) - 1 );
        result >>= ( -shift );
    }
    return result;
}

void NumListClear( int * list )
{
    memset( list, 0, sizeof( int ) * MAX_LIST_SIZE );
}

int NumListIsInList( int * list, int n )
{
    int i;
    for( i = 1; i < MAX_LIST_SIZE; i++ )
    {
        if( list[i] == n )
        {
            return 1;
        }
    }
    return 0;
}

int NumListAdd( int * list, int n )
{
    if( NumListIsInList( list, n ) )
    {
        return 1;
    }
    if( list[0] >= ( MAX_LIST_SIZE - 1 ) )
    {
        return 0;
    }
    list[0]++;
    list[list[0]] = n;
    return 1;
}

int NumListGetCount( int * list )
{
    return list[0];
}

int NumListGetFirst( int * list )
{
    int n = list[0];
    if( n > 0 )
    {
        n = list[1];
    }
    return n;
}

void StrListClear( const char ** list )
{
    memset( list, 0, sizeof( char * ) * MAX_LIST_SIZE );
}

int StrListIsInList( const char ** list, char * s )
{
    while( *list )
    {
        if( !strcasecmp( *list, s ) )
        {
            return 1;
        }
        list++;
    }
    return 0;
}

int StrListAdd( const char ** list, char * s )
{
    int i;
    for( i = 0; i < MAX_LIST_SIZE - 1; i++ )
    {
        if( !list[i] )
        {
            list[i] = s;
            return 1;
        }
        if( !strcasecmp( list[i], s ) )
        {
            return 1;
        }
    }
    return 0;
}

int ResetDevices( SANE_Device *** devices )
{
    DBG( 0, "ResetDevices()\n" );
    
    if( *devices != NULL )
    {
        int d = 0;
        
        while( (*devices)[d] != NULL )
        {
            if( ((*devices)[d])->name != NULL )
                free( (void *)((*devices)[d])->name );
            
            if( ((*devices)[d])->model != NULL )
                free( (void *)((*devices)[d])->model );
            
            free( (*devices)[d] );
            
            d++;
        }
        
        free( *devices );
        *devices = NULL;
    }
    
    return OK;
}

int SendScanEvent( char * device_uri, int event, char * type )
{
    char message[ BUFFER_SIZE ];

    int len = sprintf( message, "msg=Event\ndevice-uri=%s\nevent-code=%d\nevent-type=%s\n", 
        device_uri, event, type );

    if ( send( hpssd_socket, message, len, 0 ) == -1 ) 
    {
       bug("SendScanEvent(): unable to send message: %m\n" );  
    }

    return 0;    
}

int ProbeDevices( SANE_Device *** devices )
{
    char message[ BUFFER_SIZE ];
    MsgAttributes ma;

    int len = sprintf( message, "msg=ProbeDevicesFiltered\nbus=%s\nfilter=scan\nformat=default\n", 
        "usb,cups,par" );

    if ( send( hpssd_socket, message, len, 0 ) == -1 ) 
    {
       bug("ProbeDevices(): unable to send message: %m\n" );  
       goto abort;  
    }

    if ( ( len = recv( hpssd_socket, message, sizeof(message), 0 ) ) == -1 ) 
    {
       bug("ProbeDevices(): unable to receive result message: %m\n" );  
       goto abort;
    }

    hplip_ParseMsg( message, len, &ma );

    int d = 0;
    char * uri = NULL;
    char * mdl = NULL;
    
    if( ma.ndevice > 0 )
    {
        *devices = malloc( sizeof( SANE_Device * ) * ( ma.ndevice + 1 ) );

        int remaining = ma.length;
        char *p = (char *)ma.data;

        int state = 0;

        while( remaining > 0 && *p != '\0' && d < ma.ndevice )
        {
            //DBG( 0, "\n>>>\n%d,%c\n", state, *p );
            
            switch( state )
            {
                case 0:
                {
                    if( *p == ':' )
                    {
                        p++; remaining--;
                        uri = p;
                        state = 1;
                    }        
                    break;
                }

                case 1: 
                {
                    if( *p == ',' )
                    {
                        *p = '\0';
                        state = 2;
                        p++; remaining--;
                        mdl = p;
                    }
                    break;
                }

                case 2:
                {
                    if( *p == '\n' )
                    {
                        *p = '\0';
                        (*devices)[d] = malloc( sizeof( SANE_Device ) );
                        ((*devices)[d])->name = strdup( uri ); // URI w/o hp: 
                        ((*devices)[d])->vendor = "hp";
                        ((*devices)[d])->model = strdup( mdl );
                        ((*devices)[d])->type = "multi-function peripheral";
                        DBG( 0, "\n%s\n", uri );    
                        d++;
                        state = 0;
                        break;
                    }
                }
            } // switch

            p++;
            remaining--;

        } // while
        
        (*devices)[d] = NULL;
        return d;
    }
    else  
    {
        *devices = malloc( sizeof( SANE_Device * ) );
        (*devices)[0] = NULL;
    }

abort:
    return 0;

}

int GetScannerType( SANE_String model )
{
    char message[512];
    MsgAttributes ma;

    int len = sprintf( message, "msg=ModelQuery\nmodel=%s\n", model );

    if ( send( hpssd_socket, message, len, 0 ) == -1 ) 
    {
       bug("GetScannerType(): unable to send message: %m\n" );  
       goto abort;  
    }

    if ( ( len = recv( hpssd_socket, message, sizeof(message), 0 ) ) == -1 ) 
    {
       bug("GetScannerType(): unable to receive result message: %m\n" );  
       goto abort;
    }
    
    hplip_ParseMsg( message, len, &ma );

    return ma.scantype;

abort:
    return 0;
}

int GetPml(int hd, int channel, char *oid, char *buf, int size, int *result, int *type, int *pml_result)
{
   char message[BUFFER_SIZE+HEADER_SIZE];  
   int len=0, rlen=0;
   MsgAttributes ma;

   *result = ERROR;
   *type = PML_TYPE_NULL_VALUE;
   *pml_result = PML_ERROR; 
 
   len = sprintf(message, "msg=GetPML\ndevice-id=%d\nchannel-id=%d\noid=%s\n", hd, channel, oid);

   if (send(hpiod_socket, message, len, 0) == -1) 
   {  
      bug("unable to send GetPML: %m\n");  
      goto mordor;  
   }  

   if ((len = recv(hpiod_socket, message, sizeof(message), 0)) == -1) 
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
   char message[BUFFER_SIZE+HEADER_SIZE];  
   int len=0, slen=0;
   MsgAttributes ma;
 
   *result = ERROR;
   *pml_result = PML_ERROR; 

   len = sprintf(message, "msg=SetPML\ndevice-id=%d\nchannel-id=%d\noid=%s\ntype=%d\nlength=%d\ndata:\n", hd, channel, oid, type, size);
   if (size+len > sizeof(message))
   {  
      bug("unable to fill data buffer: size=%d: line %d\n", size, __LINE__);  
      goto mordor;  
   }  

   memcpy(message+len, buf, size);

   if (send(hpiod_socket, message, size+len, 0) == -1) 
   {  
      bug("unable to send SetPML: %m\n");  
      goto mordor;  
   }  

   if ((len = recv(hpiod_socket, message, sizeof(message), 0)) == -1) 
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
      len = size > BUFFER_SIZE ? BUFFER_SIZE : size;
        
      n = hplip_ReadHP(deviceid, channelid, (char *)buffer+total, len, timeout);
      if (n <= 0)
      {
         break;    /* error or timeout */
      }
      size-=n;
      total+=n;
   }
        
   return total;
}

