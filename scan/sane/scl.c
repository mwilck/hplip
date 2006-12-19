/************************************************************************************\

  scl.c - HP SANE backend for multi-function peripherals (libsane-hpaio)

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

  Contributing Authors: David Paschal, Don Welch, David Suffield 

\************************************************************************************/

#include <errno.h>
#include <stdio.h>
#include <string.h>
#include "hplip_api.h"
#include "io.h"
#include "common.h"
#include "scl.h"

static int SclBufferIsPartialReply( unsigned char * data, int datalen )
{
    int i = 0, value = 0;
    unsigned char d;  

    if( i >= datalen )
    {
        return 0;
    }
    if( data[i++] != 27 )
    {
        return 0;
    }
    if( i >= datalen )
    {
        return 0;
    }
    if( data[i++] != '*' )
    {
        return 0;
    }
    if( i >= datalen )
    {
        return 0;
    }
    if( data[i++] != 's' )
    {
        return 0;
    }
    while( 42 )
    {
        if( i >= datalen )
        {
            return 0;
        }
        d = data[i] - '0';
        if( d > 9 )
        {
            break;
        }
        i++;
    }
    d = data[i++];
    if( d<'a' || d>'z' )
    {
        return 0;
    }
    while( 42 )
    {
        if( i >= datalen )
        {
            return 0;
        }
        d = data[i] - '0';
        if( d > 9 )
        {
            break;
        }
        i++;
        value = ( value * 10 ) + d;
    }
    if( i >= datalen )
    {
        return 0;
    }
    if( data[i++] != 'W' )
    {
        return 0;
    }
    value = i + value - datalen;
    if( value < 0 )
    {
        value = 0;
    }
    return value;
}


static int SclChannelRead( /*ptalChannel_t chan,*/
                            int deviceid,
                            int channelid,
                            char * buffer,
                            int countdown,
                            //struct timeval * startTimeout,
                            //struct timeval * continueTimeout,
                            int isSclResponse )
{
    char * bufferStart = buffer;
    int bufferLen = countdown, countup = 0, r;
    /*struct timeval myContinueTimeout =
    {
      0, 0
    };*/

    if( !isSclResponse )
    {
        /*return ptalChannelReadTimeout( chan,
                                       buffer,
                                       countdown,
                                       startTimeout,
                                       continueTimeout );*/
        return hplip_ReadHP(hplip_session, deviceid, channelid, buffer, bufferLen, HPLIP_EXCEPTION_TIMEOUT);  
        
    }

    while( 1 )
    {
        /*r = ptalChannelReadTimeout( chan,
                                    buffer,
                                    countdown,
                                    startTimeout,
                                    &myContinueTimeout );*/
        r = hplip_ReadHP(hplip_session, deviceid, channelid, buffer, countdown, HPLIP_EXCEPTION_TIMEOUT);                                      

        if( r <= 0 )
        {
            break;
        }
        countup += r;

        countdown = SclBufferIsPartialReply( (unsigned char *)bufferStart, countup );
        
        if( countup + countdown > bufferLen )
        {
            countdown = bufferLen - countup;
        }
        if( countdown <= 0 )
        {
            break;
        }

        buffer += r;
        //startTimeout = continueTimeout;
    }

    if( !countup )
    {
        return r;
    }
    return countup;

}

SANE_Status SclSendCommand(int deviceid, int channelid, int cmd, int param)
{
    char buffer[LEN_SCL_BUFFER];
    int datalen;
    char punc = SCL_CMD_PUNC( cmd );
    char letter1 = SCL_CMD_LETTER1( cmd),letter2 = SCL_CMD_LETTER2( cmd );

    if( cmd == SCL_CMD_RESET )
    {
        datalen = snprintf( buffer, LEN_SCL_BUFFER, "\x1B%c", letter2 );
    }
    else
    {
        if( cmd == SCL_CMD_CLEAR_ERROR_STACK )
        {
            datalen = snprintf( buffer,
                                LEN_SCL_BUFFER,
                                "\x1B%c%c%c",
                                punc,
                                letter1,
                                letter2 );
        }
        else
        {
            datalen = snprintf( buffer,
                                LEN_SCL_BUFFER,
                                "\x1B%c%c%d%c",
                                punc,
                                letter1,
                                param,
                                letter2 );
        }
    }

    if(hplip_WriteHP(hplip_session, deviceid, channelid, buffer, datalen) != datalen)
    {
        return SANE_STATUS_IO_ERROR;
    }

    return SANE_STATUS_GOOD;
}

SANE_Status SclInquire(int deviceid, int channelid, int cmd, int param, int * pValue, char * buffer, int maxlen)
{
    SANE_Status retcode;
    int lenResponse, len, value;
    char _response[LEN_SCL_BUFFER + 1], * response = _response;
    char expected[LEN_SCL_BUFFER], expectedChar;

    if( !pValue )
    {
        pValue = &value;
    }
    if( buffer && maxlen > 0 )
    {
        memset( buffer, 0, maxlen );
    }
    memset( _response, 0, LEN_SCL_BUFFER + 1 );

    /* Send inquiry command. */
    if( ( retcode = SclSendCommand( deviceid, channelid, cmd, param ) ) != SANE_STATUS_GOOD )
    {
        return retcode;
    }

    /* Figure out what format of response we expect. */
    expectedChar = SCL_CMD_LETTER2( cmd ) - 'A' + 'a' - 1;
    if( expectedChar == 'q' )
    {
        expectedChar--;
    }
    len = snprintf( expected,
                    LEN_SCL_BUFFER,
                    "\x1B%c%c%d%c",
                    SCL_CMD_PUNC( cmd ),
                    SCL_CMD_LETTER1( cmd ),
                    param,
                    expectedChar );

    /* Read the response. */
    lenResponse = SclChannelRead( deviceid, channelid, response, LEN_SCL_BUFFER, 1 );
                                      
    /* Validate the first part of the response. */
    if( lenResponse <= len || memcmp( response, expected, len ) )
    {
        bug("hpaio:hpaioSclInquire(cmd=%d,param=%d) didn't get expected response of <<ESC>%s>!\n", cmd, param, expected+1);
        return SANE_STATUS_IO_ERROR;
    }
    response += len;
    lenResponse -= len;

    /* Null response? */
    if( response[0] == 'N' )
    {
      //        bug("hpaio:%s: Got null response.\n", hpaio->saneDevice.name);
        return SANE_STATUS_UNSUPPORTED;
    }

    /* Parse integer part of non-null response.
     * If this is a binary-data response, then this value is the
     * length of the binary-data portion. */
    if( sscanf( response, "%d%n", pValue, &len ) != 1 )
    {
      //        bug("hpaio:%s: hpaioSclInquire(cmd=%d,param=%d) didn't find integer!\n", hpaio->saneDevice.name, cmd, param);
        return SANE_STATUS_IO_ERROR;
    }

    /* Integer response? */
    if( response[len] == 'V' )
    {
        return SANE_STATUS_GOOD;
    }

    /* Binary-data response? */
    if( response[len] != 'W' )
    {
      //        bug("hpaio:%s: hpaioSclInquire(cmd=%d,param=%d): Unexpected character '%c'!\n", hpaio->saneDevice.name,
      //                                                      cmd, param, response[len]);
        return SANE_STATUS_IO_ERROR;
    }
    response += len + 1;
    lenResponse -= len + 1;

    /* Make sure we got the right length of binary data. */
    if( lenResponse<0 || lenResponse != *pValue || lenResponse>maxlen )
    {
      //        bug("hpaio:%s: hpaioSclInquire(cmd=%d,param=%d) unexpected binary data lenResponse=%d, *pValue=%d, and/or maxlen=%d!\n",
      //                       hpaio->saneDevice.name, cmd, param, lenResponse, *pValue, maxlen );
        return SANE_STATUS_IO_ERROR;
    }

    /* Copy binary data into user's buffer. */
    if( buffer )
    {
        maxlen = *pValue;
        memcpy( buffer, response, maxlen );
    }

    return SANE_STATUS_GOOD;
}




